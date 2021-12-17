from django.shortcuts import render
from .forms import TransientForm
from astropy.coordinates import SkyCoord
from .host_utils import survey_list, construct_all_apertures
from .cutouts import download_image_data
from.plotting_utils import plot_image_grid

def submit_transient(request):

    if request.method == 'POST':
        form = TransientForm(request.POST)
        if form.is_valid():
            ra, dec = form.cleaned_data['ra'], form.cleaned_data['dec']
            survey = survey_list('host/data/survey_metadata.yml')
            images = download_image_data(SkyCoord(ra=ra, dec=dec, unit='deg'), survey)
            apertures = construct_all_apertures(SkyCoord(ra=ra, dec=dec, unit='deg'), images)
            bokeh_cutout_dict = plot_image_grid(images, apertures=apertures)
            all_surveys = [sur.name for sur in survey]
            missing_surveys = list(set(all_surveys) - images.keys())
            bokeh_cutout_dict.update({'missing_data': missing_surveys})
            return render(request, 'results.html', bokeh_cutout_dict)


    form = TransientForm()
    return render(request, 'form.html', {'form': form})


