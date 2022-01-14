from django.shortcuts import render
from .forms import TransientForm
from astropy.coordinates import SkyCoord
from .host_utils import survey_list, construct_all_apertures
from .catalog_photometry import download_catalog_data
from .cutouts import download_and_save_cutouts
from.plotting_utils import plot_image_grid, plot_catalog_sed
from .models import Filter, Host, Transient
from .ghost import find_and_save_host

def submit_transient(request):

    if request.method == 'POST':
        form = TransientForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            ra, dec = form.cleaned_data['ra'], form.cleaned_data['dec']
            transient = Transient(name=name, ra_deg=ra, dec_deg=dec)
            host = find_and_save_host(transient)
            download_and_save_cutouts(host)



            catalog = survey_list('host/data/catalog_metadata.yml')
            position = SkyCoord(ra=ra, dec=dec, unit='deg')
            catalog_data = download_catalog_data(position, catalog)
            bokeh_cutout_dict = plot_catalog_sed(catalog_data)
            bokeh_cutout_dict['transient_name'] = form.cleaned_data['name']
            return render(request, 'results.html', bokeh_cutout_dict)


    form = TransientForm()
    return render(request, 'form.html', {'form': form})


def transient_list(request):
    transients = Transient.objects.all()
    return render(request, 'transient_list.html', {'transients': transients})


# survey = survey_list('host/data/survey_metadata.yml')
# images = download_image_data(SkyCoord(ra=ra, dec=dec, unit='deg'), survey)
# apertures = construct_all_apertures(SkyCoord(ra=ra, dec=dec, unit='deg'), images)
# bokeh_cutout_dict = plot_image_grid(images, apertures=apertures)
# all_surveys = [sur.name for sur in survey]
# missing_surveys = list(set(all_surveys) - images.keys())
# bokeh_cutout_dict.update({'missing_data': missing_surveys})