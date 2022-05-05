from django.shortcuts import render

from .forms import ImageGetForm
from .forms import TransientSearchForm
from .models import Cutout
from .models import ExternalResourceCall
from .models import Transient
from .models import Aperture
from .plotting_utils import plot_cutout_image


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
    calls = ExternalResourceCall.objects.all()
    return render(request, "analytics.html", {"resource_calls": calls})


def results(request, slug):
    transients = Transient.objects.all()
    transient = transients.get(name__exact=slug)

    global_aperture = Aperture.objects.filter(type__exact="global", transient=transient)


    all_cutouts = Cutout.objects.filter(transient__name__exact=slug)
    filters = [cutout.filter.name for cutout in all_cutouts]

    if request.method == "POST":
        form = ImageGetForm(request.POST, filter_choices=filters)
        if form.is_valid():
            filter = form.cleaned_data["filters"]
            cutout = all_cutouts.filter(filter__name__exact=filter)[0]
    else:
        cutout = None
        form = ImageGetForm(filter_choices=filters)

    bokeh_context = plot_cutout_image(cutout=cutout, transient=transient,
                                      global_aperture=global_aperture)

    context = {**{"transient": transient, "form": form}, **bokeh_context}
    return render(request, "results.html", context)
