from django.shortcuts import render
from .forms import TransientForm
from astropy.coordinates import SkyCoord
from .host_utils import survey_list, construct_all_apertures
from .catalog_photometry import download_catalog_data
from .cutouts import download_image_data
from.plotting_utils import plot_image_grid, plot_catalog_sed

def submit_transient(request):

    if request.method == 'POST':
        form = TransientForm(request.POST)
        if form.is_valid():
            ra, dec = form.cleaned_data['ra'], form.cleaned_data['dec']
            #survey = survey_list('host/data/survey_metadata.yml')
            catalog = survey_list('host/data/catalog_metadata.yml')
            position = SkyCoord(ra=ra, dec=dec, unit='deg')
            catalog_data = download_catalog_data(position, catalog)
            #images = download_image_data(SkyCoord(ra=ra, dec=dec, unit='deg'), survey)
            #apertures = construct_all_apertures(SkyCoord(ra=ra, dec=dec, unit='deg'), images)
            #bokeh_cutout_dict = plot_image_grid(images, apertures=apertures)
            bokeh_cutout_dict = plot_catalog_sed(catalog_data)

            #all_surveys = [sur.name for sur in survey]
            #missing_surveys = list(set(all_surveys) - images.keys())

            #bokeh_cutout_dict.update({'missing_data': missing_surveys})
            return render(request, 'results.html', bokeh_cutout_dict)


    form = TransientForm()
    return render(request, 'form.html', {'form': form})


