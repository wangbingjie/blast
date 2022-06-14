from django.shortcuts import render

from .forms import ImageGetForm
from .forms import TransientSearchForm
from .models import Acknowledgement
from .models import Aperture
from .models import AperturePhotometry
from .models import Cutout
from .models import Filter
from .models import TaskRegisterSnapshot
from .models import Transient
from .plotting_utils import plot_cutout_image
from .plotting_utils import plot_sed
from .plotting_utils import plot_timeseries



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

        transients = TaskRegisterSnapshot.objects.filter(aggregate_type__exact=aggregate)
        transients_ordered = transients.order_by("-time")

        if transients_ordered.exists():
            transients_current = transients_ordered[0]
        else:
            transients_current = None

        analytics_results[f"{aggregate}_transients_current".replace(" ", "_")] = transients_current
        bokeh_processing_context = plot_timeseries()

    return render(request, "analytics.html", {**analytics_results,
                                             **bokeh_processing_context})


def results(request, slug):
    transients = Transient.objects.all()
    transient = transients.get(name__exact=slug)

    global_aperture = Aperture.objects.filter(type__exact="global", transient=transient)
    local_aperture = Aperture.objects.filter(type__exact="local", transient=transient)
    local_aperture_photometry = AperturePhotometry.objects.filter(transient=transient,
                                                                  aperture__type__exact="local")
    global_aperture_photometry = AperturePhotometry.objects.filter(transient=transient,
                                                                  aperture__type__exact="global")

    all_cutouts = Cutout.objects.filter(transient__name__exact=slug)
    filters = [cutout.filter.name for cutout in all_cutouts]
    all_filters = Filter.objects.all()

    filter_status = {filter_.name :
                         ('yes' if filter_.name in filters else 'no')
                     for filter_ in all_filters}

    if request.method == "POST":
        form = ImageGetForm(request.POST, filter_choices=filters)
        if form.is_valid():
            filter = form.cleaned_data["filters"]
            cutout = all_cutouts.filter(filter__name__exact=filter)[0]
    else:
        cutout = None
        form = ImageGetForm(filter_choices=filters)

    bokeh_context = plot_cutout_image(cutout=cutout, transient=transient,
                                      global_aperture=global_aperture,
                                      local_aperture=local_aperture)
    bokeh_sed_local_context = plot_sed(aperture_photometry=local_aperture_photometry,type="local")
    bokeh_sed_global_context = plot_sed(aperture_photometry=global_aperture_photometry, type="global")

    if local_aperture.exists():
        local_aperture = local_aperture[0]
    else:
        local_aperture = None

    if global_aperture.exists():
        global_aperture = global_aperture[0]
    else:
        global_aperture = None

    context = {**{"transient": transient,
                  "form": form,
                  "local_aperture_photometry": local_aperture_photometry,
                  "global_aperture_photometry": global_aperture_photometry,
                  "filter_status": filter_status,
                  "local_aperture": local_aperture,
                  "global_aperture": global_aperture},
               **bokeh_context,
               **bokeh_sed_local_context,
               **bokeh_sed_global_context}

    return render(request, "results.html", context)


def acknowledgements(request):
    context = {'acknowledgements': Acknowledgement.objects.all()}
    return render(request, "acknowledgements.html", context)
