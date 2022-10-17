from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import re_path
from revproxy.views import ProxyView

from .forms import ImageGetForm
from .forms import TransientSearchForm
from .models import Acknowledgement
from .models import Aperture
from .models import AperturePhotometry
from .models import Cutout
from .models import Filter
from .models import SEDFittingResult
from .models import TaskRegisterSnapshot
from .models import Transient
from .plotting_utils import plot_cutout_image
from .plotting_utils import plot_pie_chart
from .plotting_utils import plot_sed
from .plotting_utils import plot_sed_posterior
from .plotting_utils import plot_timeseries
from .plotting_utils import get_if_exists

def transient_list(request):
    transients = Transient.objects.all()

    if request.method == "POST":
        form = TransientSearchForm(request.POST)

        if form.is_valid():
            name = form.cleaned_data["name"]
            if name != "all":
                transients = Transient.objects.filter(name__contains=name)
    else:
        form = TransientSearchForm()

    transients = transients.order_by("-public_timestamp")[:100]

    context = {"transients": transients, "form": form}
    return render(request, "transient_list.html", context)


def analytics(request):
    analytics_results = {}

    for aggregate in ["total", "not completed", "completed", "waiting"]:

        transients = TaskRegisterSnapshot.objects.filter(
            aggregate_type__exact=aggregate
        )
        transients_ordered = transients.order_by("-time")

        if transients_ordered.exists():
            transients_current = transients_ordered[0]
        else:
            transients_current = None

        analytics_results[
            f"{aggregate}_transients_current".replace(" ", "_")
        ] = transients_current
        bokeh_processing_context = plot_timeseries()

    return render(
        request, "analytics.html", {**analytics_results, **bokeh_processing_context}
    )


def results(request, slug):
    transients = Transient.objects.all()
    transient = transients.get(name__exact=slug)

    sed_posterior_bokeh_div, sed_posterior_bokeh_script = plot_sed_posterior(transient, aperture_types=["local", "global"])
    sed_bokeh_div, sed_bokeh_script = plot_sed(transient, aperture_types=["local", "global"])

    local_aperture_photometry = AperturePhotometry.objects.filter(
        transient=transient, aperture__type__exact="local"
    )
    global_aperture_photometry = AperturePhotometry.objects.filter(
        transient=transient, aperture__type__exact="global"
    )

    global_aperture = get_if_exists(Aperture.objects.filter(type__exact="global", transient=transient))
    local_aperture = get_if_exists(Aperture.objects.filter(type__exact="local", transient=transient))

    local_sed_posterior = get_if_exists(SEDFittingResult.objects.filter(
        transient=transient, aperture__type__exact="local"
    ))
    global_sed_posterior = get_if_exists(SEDFittingResult.objects.filter(
        transient=transient, aperture__type__exact="global"
    ))

    all_cutouts = Cutout.objects.filter(transient__name__exact=slug)
    filters = [cutout.filter.name for cutout in all_cutouts]
    all_filters = Filter.objects.all()

    filter_status = {
        filter_.name: ("yes" if filter_.name in filters else "no")
        for filter_ in all_filters
    }

    if request.method == "POST":
        form = ImageGetForm(request.POST, filter_choices=filters)
        if form.is_valid():
            filter = form.cleaned_data["filters"]
            cutout = all_cutouts.filter(filter__name__exact=filter)[0]
    else:
        cutout = None
        form = ImageGetForm(filter_choices=filters)

    cutout_bokeh_div, cutout_bokeh_script = plot_cutout_image(
        cutout=cutout,
        transient=transient,
        global_aperture=global_aperture,
        local_aperture=local_aperture,
    )

    render_context = {}
    render_context['transient'] = transient
    render_context['form'] = form
    render_context['local_aperture_photometry'] = local_aperture_photometry
    render_context['global_aperture_photometry'] = global_aperture_photometry
    render_context['local_aperture'] = local_aperture
    render_context['global_aperture'] = global_aperture
    render_context['filter_status'] = filter_status
    render_context['local_sed_results'] = local_sed_posterior
    render_context['global_sed_results'] = global_sed_posterior
    render_context['bokeh_scripts'] = sed_bokeh_script + sed_posterior_bokeh_script + [cutout_bokeh_script]
    render_context['cutout_bokeh_script'] = cutout_bokeh_script
    render_context = {**render_context, **sed_posterior_bokeh_div, **sed_bokeh_div, **cutout_bokeh_div}

    return render(request, "results.html", render_context)


def acknowledgements(request):
    context = {"acknowledgements": Acknowledgement.objects.all()}
    return render(request, "acknowledgements.html", context)


def home(request):
    analytics_results = {}

    for aggregate in ["total", "not completed", "completed", "waiting"]:

        transients = TaskRegisterSnapshot.objects.filter(
            aggregate_type__exact=aggregate
        )

        transients_ordered = transients.order_by("-time")

        if transients_ordered.exists():
            transients_current = transients_ordered[0].number_of_transients
        else:
            transients_current = None

        analytics_results[f"{aggregate}".replace("_", " ")] = transients_current

    total = analytics_results["total"]
    del analytics_results["total"]
    bokeh_processing_context = plot_pie_chart(analytics_results)

    return render(request, "index.html", {"total": total, **bokeh_processing_context})


# @user_passes_test(lambda u: u.is_staff and u.is_superuser)
def flower_view(request):
    """passes the request back up to nginx for internal routing"""
    response = HttpResponse()
    path = request.get_full_path()
    path = path.replace("flower", "flower-internal", 1)
    response["X-Accel-Redirect"] = path
    return response


class FlowerProxyView(UserPassesTestMixin, ProxyView):
    # `flower` is Docker container, you can use `localhost` instead
    upstream = "http://{}:{}".format("0.0.0.0", 8888)
    url_prefix = "flower"
    rewrite = ((r"^/{}$".format(url_prefix), r"/{}/".format(url_prefix)),)

    def test_func(self):
        return self.request.user.is_superuser

    @classmethod
    def as_url(cls):
        return re_path(r"^(?P<path>{}.*)$".format(cls.url_prefix), cls.as_view())
