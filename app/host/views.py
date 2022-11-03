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
from .plotting_utils import plot_timeseries
from .host_utils import select_cutout_aperture

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

    cutouts = Cutout.objects.filter(transient=transient)
    cutout_for_aperture = select_cutout_aperture(cutouts)[0]
    global_aperture = Aperture.objects.filter(type__exact="global", transient=transient, cutout=cutout_for_aperture)
    local_aperture = Aperture.objects.filter(type__exact="local", transient=transient)
    local_aperture_photometry = AperturePhotometry.objects.filter(
        transient=transient, aperture__type__exact="local", flux__isnull=False
    )
    global_aperture_photometry = AperturePhotometry.objects.filter(
        transient=transient, aperture__type__exact="global", flux__isnull=False
    )

    local_sed_obj = SEDFittingResult.objects.filter(
        transient=transient, aperture__type__exact="local"
    )
    global_sed_obj = SEDFittingResult.objects.filter(
        transient=transient, aperture__type__exact="global"
    )
    # ugly, but effective?
    local_sed_results, global_sed_results = (), ()
    for param in ["mass", "sfr", "ssfr", "age", "tau"]:
        if local_sed_obj.exists():
            local_sed_results += (
                (
                    param,
                    local_sed_obj[0].__dict__[f"log_{param}_16"],
                    local_sed_obj[0].__dict__[f"log_{param}_50"],
                    local_sed_obj[0].__dict__[f"log_{param}_84"],
                ),
            )
        if global_sed_obj.exists():
            global_sed_results += (
                (
                    param,
                    global_sed_obj[0].__dict__[f"log_{param}_16"],
                    global_sed_obj[0].__dict__[f"log_{param}_50"],
                    global_sed_obj[0].__dict__[f"log_{param}_84"],
                ),
            )
    if local_sed_obj.exists():
        local_sed_file = local_sed_obj[0].posterior.name
    else:
        local_sed_file = None
    if global_sed_obj.exists():
        global_sed_file = global_sed_obj[0].posterior.name
    else:
        global_sed_file = None

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

    bokeh_context = plot_cutout_image(
        cutout=cutout,
        transient=transient,
        global_aperture=global_aperture,
        local_aperture=local_aperture,
    )
    bokeh_sed_local_context = plot_sed(
        aperture_photometry=local_aperture_photometry,
        type="local",
        sed_results_file=local_sed_file,
    )
    bokeh_sed_global_context = plot_sed(
        aperture_photometry=global_aperture_photometry,
        type="global",
        sed_results_file=global_sed_file,
    )

    if local_aperture.exists():
        local_aperture = local_aperture[0]
    else:
        local_aperture = None

    if global_aperture.exists():
        global_aperture = global_aperture[0]
    else:
        global_aperture = None

    context = {
        **{
            "transient": transient,
            "form": form,
            "local_aperture_photometry": local_aperture_photometry,
            "global_aperture_photometry": global_aperture_photometry,
            "filter_status": filter_status,
            "local_aperture": local_aperture,
            "global_aperture": global_aperture,
            "local_sed_results": local_sed_results,
            "global_sed_results": global_sed_results,
        },
        **bokeh_context,
        **bokeh_sed_local_context,
        **bokeh_sed_global_context,
    }

    return render(request, "results.html", context)


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
