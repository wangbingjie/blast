import pandas as pd
from astropy.coordinates import SkyCoord
from astropy.io import fits

def panstarrs_image_filename(position ,image_size=None, filter=None):
    """Query panstarrs service to get a list of image names

    Parameters
    ----------
    :position : :class:`~astropy.coordinates.SkyCoord`
        Target centre position of the cutout image to be downloaded.
    :size : int: cutout image size in pixels.
    :filter: str: Panstarrs filter (g r i z y)
    Returns
    -------
    :filename: str: file name of the cutout
    """

    service = 'https://ps1images.stsci.edu/cgi-bin/ps1filenames.py'
    url = (f'{service}?ra={position.ra.degree}&dec={position.dec.degree}'
           f'&size={image_size}&format=fits&filters={filter}')
    return pd.read_csv(url, delim_whitespace=True)['filename'][0]

def panstarrs_cutout(position, image_size=None, filter=None):
    """
    Download Panstarrs cutout from their own service

    Parameters
    ----------
    :position : :class:`~astropy.coordinates.SkyCoord`
        Target centre position of the cutout image to be downloaded.
    :image_size: int: size of cutout image in pixels
    :filter: str: Panstarrs filter (g r i z y)
    Returns
    -------
    :cutout : :class:`~astropy.io.fits.HDUList` or None
    """
    filename = panstarrs_image_filename(position,
                                        image_size=image_size,
                                        filter=filter)
    service = 'https://ps1images.stsci.edu/cgi-bin/fitscut.cgi?'
    fits_url = (f'{service}ra={position.ra.degree}&dec={position.dec.degree}'
           f'&size={image_size}&format=fits&red={filename}')
    return fits.open(fits_url)




print(panstarrs_cutout(SkyCoord(ra=83.633210, dec=22.014460, unit='deg'), image_size=250, filter='g'))