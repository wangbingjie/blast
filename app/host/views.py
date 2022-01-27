from django.shortcuts import render
from .forms import TransientSearchForm
from .models import Transient, ExternalResourceCall


def transient_list(request):
    transients = Transient.objects.all()

    if request.method == 'POST':
        form = TransientSearchForm(request.POST)

        if form.is_valid():
            name = form.cleaned_data['name']
            if name != 'all':
                transients = Transient.objects.filter(tns_name__contains=name)
    else:
        form = TransientSearchForm()

    transients = transients.order_by('-public_timestamp')[:100]
    context = {'transients': transients, 'form': form}
    return render(request, 'transient_list.html', context)


def analytics(request):
    calls = ExternalResourceCall.objects.all()
    return render(request, 'analytics.html', {'resource_calls': calls})

# survey = survey_list('host/data/survey_metadata.yml')
# images = download_image_data(SkyCoord(ra=ra, dec=dec, unit='deg'), survey)
# apertures = construct_all_apertures(SkyCoord(ra=ra, dec=dec, unit='deg'), images)
# bokeh_cutout_dict = plot_image_grid(images, apertures=apertures)
# all_surveys = [sur.name for sur in survey]
# missing_surveys = list(set(all_surveys) - images.keys())
# bokeh_cutout_dict.update({'missing_data': missing_surveys})