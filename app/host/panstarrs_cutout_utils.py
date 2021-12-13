import pandas as pd
from astropy.coordinates import SkyCoord
from astropy.io import fits

def panstarrs_image_filename(position ,image_size=None, filter=None):

    """Query ps1filenames.py service to get a list of images

    ra, dec = position in degrees
    size = image size in pixels (0.25 arcsec/pixel)
    filters = string with filters to include
    Returns a string with with filename
    """

    service = 'https://ps1images.stsci.edu/cgi-bin/ps1filenames.py'
    url = (f'{service}?ra={position.ra.degree}&dec={position.dec.degree}'
           f'&size={image_size}&format=fits&filters={filter}')
    return pd.read_csv(url, delim_whitespace=True)['filename'][0]

def panstarrs_cutout(position, image_size=None, filter=None):
    """
    Download Panstarrs cutout from their own service

    Return HDU list
    """
    filename = panstarrs_image_filename(position,
                                        image_size=image_size,
                                        filter=filter)
    service = 'https://ps1images.stsci.edu/cgi-bin/fitscut.cgi?'
    fits_url = (f'{service}ra={position.ra.degree}&dec={position.dec.degree}'
           f'&size={image_size}&format=fits&red={filename}')

    return fits.open(fits_url)




print(panstarrs_cutout(SkyCoord(ra=83.633210, dec=22.014460, unit='deg'), image_size=250, filter='g'))