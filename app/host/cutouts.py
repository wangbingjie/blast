import os
import re

import astropy.table as at
import astropy.units as u
import numpy as np
import pandas as pd
import requests
from astropy.coordinates import SkyCoord
from astropy.io import fits
from astropy.nddata import Cutout2D
from astropy.units import Quantity
from astropy.wcs import WCS
from astroquery.hips2fits import hips2fits
from astroquery.mast import Observations
from astroquery.sdss import SDSS
from astroquery.skyview import SkyView
from django.conf import settings
from dl import authClient as ac
from dl import queryClient as qc
from dl import storeClient as sc
from pyvo.dal import sia

from .models import Cutout
from .models import Filter


def download_and_save_cutouts(
    transient,
    fov=Quantity(0.1, unit="deg"),
    media_root=settings.MEDIA_ROOT,
    overwrite=settings.CUTOUT_OVERWRITE,
):
    """
    Download all available imaging from a list of surveys
    Parameters
    ----------
    :position : :class:`~astropy.coordinates.SkyCoord`
        Target centre position of the cutout image to be downloaded.
    :survey_list : list[Survey]
        List of surveys to download data from
    :fov : :class:`~astropy.units.Quantity`,
    default=Quantity(0.1,unit='deg')
        Field of view of the cutout image, angular length of one of the sides
        of the square cutout. Angular astropy quantity. Default is angular
        length of 0.2 degrees.
    Returns
    -------
    :images dictionary : dict[str: :class:`~astropy.io.fits.HDUList`]
        Dictionary of images with the survey names as keys and fits images
        as values.
    """

    for filter in Filter.objects.all():
        save_dir = f"{media_root}/{transient.name}/{filter.survey.name}/"
        path_to_fits = save_dir + f"{filter.name}.fits"
        file_exists = os.path.exists(path_to_fits)

        if file_exists and overwrite == "False":
            cutout_name = f"{transient.name}_{filter.name}"
            cutout_object = Cutout(name=cutout_name, filter=filter, transient=transient)
            cutout_object.fits.name = path_to_fits
            cutout_object.save()
        else:
            fits = cutout(transient.sky_coord, filter, fov=fov)
            if fits:
                save_dir = f"{media_root}/{transient.name}/{filter.survey.name}/"
                os.makedirs(save_dir, exist_ok=True)
                path_to_fits = save_dir + f"{filter.name}.fits"
                fits.writeto(path_to_fits, overwrite=True)
                cutout_name = f"{transient.name}_{filter.name}"
                cutout_object = Cutout(
                    name=cutout_name, filter=filter, transient=transient
                )
                cutout_object.fits.name = path_to_fits
                cutout_object.save()


def panstarrs_image_filename(position, image_size=None, filter=None):
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

    service = "https://ps1images.stsci.edu/cgi-bin/ps1filenames.py"
    url = (
        f"{service}?ra={position.ra.degree}&dec={position.dec.degree}"
        f"&size={image_size}&format=fits&filters={filter}"
    )

    filename_table = pd.read_csv(url, delim_whitespace=True)["filename"]
    return filename_table[0] if len(filename_table) > 0 else None


def hips_cutout(position, survey, image_size=None):
    """
    Download fits image from hips2fits service.

    Parameters
    ----------
    :position : :class:`~astropy.coordinates.SkyCoord`
        Target centre position of the cutout image to be downloaded.
    :image_size : int: cutout image size in pixels.
    Returns
    -------
    :cutout : :class:`~astropy.io.fits.HDUList` or None
    """
    fov = Quantity(survey.pixel_size_arcsec * image_size, unit="arcsec")

    fits_image = hips2fits.query(
        hips=survey.hips_id,
        ra=position.ra,
        dec=position.dec,
        width=image_size,
        height=image_size,
        fov=fov,
        projection="TAN",
        format="fits",
    )

    # if the position is outside of the survey footprint
    if np.all(np.isnan(fits_image[0].data)):
        fits_image = None
    return fits_image


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
    filename = panstarrs_image_filename(position, image_size=image_size, filter=filter)
    if filename is not None:
        service = "https://ps1images.stsci.edu/cgi-bin/fitscut.cgi?"
        fits_url = (
            f"{service}ra={position.ra.degree}&dec={position.dec.degree}"
            f"&size={image_size}&format=fits&red={filename}"
        )
        fits_image = fits.open(fits_url)
    else:
        fits_image = None

    return fits_image


def galex_cutout(position, image_size=None, filter=None):
    """
    Download GALEX cutout from MAST

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

    obs = Observations.query_region(position)
    obs = obs[
        (obs["obs_collection"] == "GALEX")
        & (obs["filters"] == filter)
        & (obs["distance"] == 0)
    ]
    if len(obs) > 1:
        obs = obs[obs["t_exptime"] == max(obs["t_exptime"])]

    if len(obs):
        ### stupid MAST thinks we want the exposure time map

        fits_image = fits.open(
            obs["dataURL"][0]
            .replace("-exp.fits.gz", "-int.fits.gz")
            .replace("-gsp.fits.gz", "-int.fits.gz")
            .replace("-rr.fits.gz", "-int.fits.gz")
            .replace("-cnt.fits.gz", "-int.fits.gz")
            .replace("-xd-mcat.fits.gz", f"-{filter[0].lower()}d-int.fits.gz")
        )

        wcs = WCS(fits_image[0].header)
        cutout = Cutout2D(fits_image[0].data, position, image_size, wcs=wcs)
        fits_image[0].data = cutout.data
        fits_image[0].header.update(cutout.wcs.to_header())
        if not np.any(fits_image[0].data):
            fits_image = None
    else:
        fits_image = None

    return fits_image


def WISE_cutout(position, image_size=None, filter=None):
    """
    Download WISE image cutout from IRSA

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

    band_to_wavelength = {
        "W1": "3.4e-6",
        "W2": "4.6e-6",
        "W3": "1.2e-5",
        "W4": "2.2e-5",
    }

    url = f"https://irsa.ipac.caltech.edu/SIA?COLLECTION=wise_allwise&POS=circle+{position.ra.deg}+{position.dec.deg}+0.002777&RESPONSEFORMAT=CSV&BAND={band_to_wavelength[filter]}&FORMAT=image/fits"
    r = requests.get(url)
    url = None
    for t in r.text.split(","):
        if t.startswith("https"):
            url = t[:]
            break
    data = at.Table.read(r.text, format="ascii.csv")
    exptime = data["t_exptime"][0]

    if url is not None:
        fits_image = fits.open(url)

        wcs = WCS(fits_image[0].header)
        cutout = Cutout2D(fits_image[0].data, position, image_size, wcs=wcs)
        fits_image[0].data = cutout.data
        fits_image[0].header.update(cutout.wcs.to_header())
        fits_image[0].header["EXPTIME"] = exptime

    else:
        fits_image = None

    return fits_image


def DES_cutout(position, image_size=None, filter=None):
    """
    Download DES image cutout from NOIRLab

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

    DEF_ACCESS_URL = "https://datalab.noirlab.edu/sia/ls_dr9"
    svc_ls_dr9 = sia.SIAService(DEF_ACCESS_URL)

    imgTable = svc_ls_dr9.search(
        (position.ra.deg, position.dec.deg),
        (image_size / np.cos(position.dec.deg * np.pi / 180), image_size),
        verbosity=2,
    ).to_table()

    valid_urls = []
    for img in imgTable:
        if "-depth-" in img["access_url"] and img["obs_bandpass"].startswith(filter):
            valid_urls += [img["access_url"]]

    if len(valid_urls):
        # we need both the depth and the image

        fits_image = fits.open(valid_urls[0].replace("-depth-", "-image-"))
        if np.shape(fits_image[0].data)[0] == 1 or np.shape(fits_image[0].data)[1] == 1:
            # no idea what's happening here but this is a mess
            return None

        depth_image = fits.open(valid_urls[0])
        wcs_depth = WCS(depth_image[0].header)
        xc, yc = wcs_depth.wcs_world2pix(position.ra.deg, position.dec.deg, 0)

        # this is ugly - just assuming the exposure time at the
        # location of interest is uniform across the image
        if np.shape(depth_image[0].data) == (1, 1):
            exptime = depth_image[0].data[0][0]
        else:
            exptime = depth_image[0].data[int(yc), int(xc)]

        wcs = WCS(fits_image[0].header)
        cutout = Cutout2D(fits_image[0].data, position, image_size, wcs=wcs)
        fits_image[0].data = cutout.data
        fits_image[0].header.update(cutout.wcs.to_header())
        fits_image[0].header["EXPTIME"] = exptime

    else:
        fits_image = None

    return fits_image


def TWOMASS_cutout(position, image_size=None, filter=None):
    """
    Download 2MASS image cutout from IRSA

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

    irsaquery = f"https://irsa.ipac.caltech.edu/cgi-bin/2MASS/IM/nph-im_sia?POS={position.ra.deg},{position.dec.deg}&SIZE=0.01"
    response = requests.get(url=irsaquery)

    fits_image = None
    for line in response.content.decode("utf-8").split("<TD><![CDATA["):
        if re.match(f"https://irsa.*{filter.lower()}i.*fits", line.split("]]>")[0]):
            fitsurl = line.split("]]")[0]

            fits_image = fits.open(fitsurl)
            wcs = WCS(fits_image[0].header)

            if position.contained_by(wcs):
                break

    if fits_image is not None:

        cutout = Cutout2D(fits_image[0].data, position, image_size, wcs=wcs)
        fits_image[0].data = cutout.data
        fits_image[0].header.update(cutout.wcs.to_header())

    else:
        fits_image = None

    return fits_image


def SDSS_cutout(position, image_size=None, filter=None):
    """
    Download SDSS image cutout from astroquery

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

    sdss_baseurl = "https://dr14.sdss.org/sas"
    print(position)

    xid = SDSS.query_region(position, radius=0.05 * u.deg)
    if xid is not None and 'titleSkyserver_Errortitle' in xid.keys():
        RuntimeWarning(f'SDSS query fail for position {position.ra.deg},{position.dec.deg}')
        return None

    if xid is not None:
        sc = SkyCoord(xid["ra"], xid["dec"], unit=u.deg)
        sep = position.separation(sc).arcsec
        iSep = np.where(sep == min(sep))[0][0]

        link = SDSS.IMAGING_URL_SUFFIX.format(
            base=sdss_baseurl,
            run=xid[iSep]["run"],
            dr=14,
            instrument="eboss",
            rerun=xid[iSep]["rerun"],
            camcol=xid[iSep]["camcol"],
            field=xid[iSep]["field"],
            band=filter,
        )

        fits_image = fits.open(link)

        wcs = WCS(fits_image[0].header)
        cutout = Cutout2D(fits_image[0].data, position, image_size, wcs=wcs)
        fits_image[0].data = cutout.data
        fits_image[0].header.update(cutout.wcs.to_header())

    else:
        fits_image = None

    return fits_image


download_function_dict = {
    "PanSTARRS": panstarrs_cutout,
    "GALEX": galex_cutout,
    "2MASS": TWOMASS_cutout,
    "WISE": WISE_cutout,
    "DES": DES_cutout,
    "SDSS": SDSS_cutout,
}


def cutout(transient, survey, fov=Quantity(0.1, unit="deg")):
    """
    Download image cutout data from a survey.
    Parameters
    ----------
    :position : :class:`~astropy.coordinates.SkyCoord`
        Target centre position of the cutout image to be downloaded.
    :survey : :class: Survey
        Named tuple containing metadata for the survey the image is to be
        downloaded from.
    :fov : :class:`~astropy.units.Quantity`,
    default=Quantity(0.2,unit='deg')
        Field of view of the cutout image, angular length of one of the sides
        of the square cutout. Angular astropy quantity. Default is angular
        length of 0.2 degrees.
    Returns
    -------
    :cutout : :class:`~astropy.io.fits.HDUList` or None
        Image cutout in fits format or if the image cannot be download due to a
        `ReadTimeoutError` None will be returned.
    """
    num_pixels = int(fov.to(u.arcsec).value / survey.pixel_size_arcsec)

    if survey.image_download_method == "hips":
        try:
            fits = hips_cutout(transient, survey, image_size=num_pixels)
        except:
            print(f"Conection timed out, could not download {survey.name} data")
            fits = None
    else:
        survey_name, filter = survey.name.split("_")
        fits = download_function_dict[survey_name](
            transient, filter=filter, image_size=num_pixels
        )

    return fits
