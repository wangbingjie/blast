import glob
import math
import os
import time
import warnings
from collections import namedtuple

import astropy.units as u
import extinction
import numpy as np
import yaml
from astropy.convolution import Gaussian2DKernel
from astropy.coordinates import SkyCoord
from astropy.cosmology import FlatLambdaCDM
from astropy.io import fits
from astropy.stats import gaussian_fwhm_to_sigma
from astropy.units import Quantity
from astropy.wcs import WCS
from astroquery.hips2fits import hips2fits
from astroquery.ipac.ned import Ned
from astroquery.sdss import SDSS

cosmo = FlatLambdaCDM(H0=70, Om0=0.315)

from django.conf import settings
from dustmaps.sfd import SFDQuery
from photutils.aperture import aperture_photometry
from photutils.aperture import EllipticalAperture
from photutils.background import Background2D
from photutils.segmentation import deblend_sources
from photutils.segmentation import detect_sources
from photutils.segmentation import detect_threshold
from photutils.segmentation import SourceCatalog
from photutils.utils import calc_total_error

from .photometric_calibration import ab_mag_to_mJy
from .photometric_calibration import flux_to_mag
from .photometric_calibration import flux_to_mJy_flux
from .photometric_calibration import fluxerr_to_magerr
from .photometric_calibration import fluxerr_to_mJy_fluxerr

from .models import Cutout
from .models import Aperture


def survey_list(survey_metadata_path):
    """
    Build a list of survey objects from a metadata file.
    Parameters
    ----------
    :survey_metadata_path : str
        Path to a yaml data file containing survey metadata
    Returns
    -------
    :list of surveys: list[Survey]
        List of survey objects
    """
    with open(survey_metadata_path, "r") as stream:
        survey_metadata = yaml.safe_load(stream)

    # get first survey from the metadata in order to infer the data field names
    survey_name = list(survey_metadata.keys())[0]
    data_fields = list(survey_metadata[survey_name].keys())

    # create a named tuple class with all the survey data fields as attributes
    # including the survey name
    Survey = namedtuple("Survey", ["name"] + data_fields)

    survey_list = []
    for name in survey_metadata:
        field_dict = {field: survey_metadata[name][field] for field in data_fields}
        field_dict["name"] = name
        survey_list.append(Survey(**field_dict))

    return survey_list


def build_source_catalog(image, background, threshhold_sigma=3.0, npixels=10):
    """
    Constructs a source catalog given an image and background estimation
    Parameters
    ----------
    :image :  :class:`~astropy.io.fits.HDUList`
        Fits image to construct source catalog from.
    :background : :class:`~photutils.background.Background2D`
        Estimate of the background in the image.
    :threshold_sigma : float default=2.0
        Threshold sigma above the baseline that a source has to be to be
        detected.
    :n_pixels : int default=10
        The length of the size of the box in pixels used to perform segmentation
        and de-blending of the image.
    Returns
    -------
    :source_catalog : :class:`photutils.segmentation.SourceCatalog`
        Catalog of sources constructed from the image.
    """

    image_data = image[0].data
    background_subtracted_data = image_data - background.background
    threshold = threshhold_sigma * background.background_rms

    segmentation = detect_sources(
        background_subtracted_data, threshold, npixels=npixels
    )
    if segmentation is None:
        return None
    deblended_segmentation = deblend_sources(
        background_subtracted_data, segmentation, npixels=npixels
    )
    print(segmentation)
    return SourceCatalog(background_subtracted_data, segmentation)


def match_source(position, source_catalog, wcs):
    """
    Match the source in the source catalog to the host position
    Parameters
    ----------
    :position : :class:`~astropy.coordinates.SkyCoord`
        On Sky position of the source to be matched.
    :source_catalog : :class:`~photutils.segmentation.SourceCatalog`
        Catalog of sources.
    :wcs : :class:`~astropy.wcs.WCS`
        World coordinate system to match the sky position to the
        source catalog.
    Returns
    -------
    :source : :class:`~photutils.segmentation.SourceCatalog`
        Catalog containing the one matched source.
    """

    host_x_pixel, host_y_pixel = wcs.world_to_pixel(position)
    source_x_pixels, source_y_pixels = (
        source_catalog.xcentroid,
        source_catalog.ycentroid,
    )
    closest_source_index = np.argmin(
        np.hypot(host_x_pixel - source_x_pixels, host_y_pixel - source_y_pixels)
    )

    return source_catalog[closest_source_index]


def elliptical_sky_aperture(source_catalog, wcs, aperture_scale=3.0):
    """
    Constructs an elliptical sky aperture from a source catalog
    Parameters
    ----------
    :source_catalog: :class:`~photutils.segmentation.SourceCatalog`
        Catalog containing the source to get aperture information from.
    :wcs : :class:`~astropy.wcs.WCS`
        World coordinate system of the source catalog.
    :aperture_scale: float default=3.0
        Scale factor to increase the size of the aperture
    Returns
    -------
    :sky_aperture: :class:`~photutils.aperture.SkyEllipticalAperture`
        Elliptical sky aperture of the source in the source catalog.
    """
    center = (source_catalog.xcentroid, source_catalog.ycentroid)
    semi_major_axis = source_catalog.semimajor_sigma.value * aperture_scale
    semi_minor_axis = source_catalog.semiminor_sigma.value * aperture_scale
    orientation_angle = source_catalog.orientation.to(u.rad).value
    pixel_aperture = EllipticalAperture(
        center, semi_major_axis, semi_minor_axis, theta=orientation_angle
    )
    pixel_aperture = source_catalog.kron_aperture
    return pixel_aperture.to_sky(wcs)


def do_aperture_photometry(image, sky_aperture, filter):
    """
    Performs Aperture photometry
    """
    image_data = image[0].data
    wcs = WCS(image[0].header)

    # get the background
    try:
        background = estimate_background(image)
    except ValueError:
        # indicates poor image data
        return {
            "flux": None,
            "flux_error": None,
            "magnitude": None,
            "magnitude_error": None,
        }

    background_subtracted_data = image_data - background.background

    if filter.image_pixel_units == "counts/sec":
        error = calc_total_error(
            background_subtracted_data,
            background.background_rms,
            float(image[0].header["EXPTIME"]),
        )

    else:
        error = calc_total_error(
            background_subtracted_data, background.background_rms, 1.0
        )

    phot_table = aperture_photometry(
        background_subtracted_data, sky_aperture, wcs=wcs, error=error
    )
    uncalibrated_flux = phot_table["aperture_sum"].value[0]
    uncalibrated_flux_err = phot_table["aperture_sum_err"].value[0]

    if filter.magnitude_zero_point_keyword is not None:
        zpt = image[0].header[filter.magnitude_zero_point_keyword]
    elif filter.image_pixel_units == "counts/sec":
        zpt = filter.magnitude_zero_point
    else:
        zpt = filter.magnitude_zero_point + 2.5 * np.log10(image[0].header["EXPTIME"])

    flux = flux_to_mJy_flux(uncalibrated_flux, zpt)
    flux_error = fluxerr_to_mJy_fluxerr(uncalibrated_flux_err, zpt)
    magnitude = flux_to_mag(uncalibrated_flux, zpt)
    magnitude_error = fluxerr_to_magerr(uncalibrated_flux, uncalibrated_flux_err)
    if magnitude != magnitude:
        magnitude, magnitude_error = None, None
    if flux != flux or flux_error != flux_error:
        flux, flux_error = None, None

    wave_eff = filter.transmission_curve().wave_effective

    return {
        "flux": flux,
        "flux_error": flux_error,
        "magnitude": magnitude,
        "magnitude_error": magnitude_error,
    }


def get_dust_maps(position, media_root=settings.MEDIA_ROOT):
    """Gets milkyway reddening value"""

    ebv = SFDQuery()(position)
    # see Schlafly & Finkbeiner 2011 for the 0.86 correction term
    return 0.86 * ebv


def get_local_aperture_size(redshift):
    """find the size of a 2 kpc radius in arcsec"""

    dadist = cosmo.angular_diameter_distance(redshift).value
    apr_arcsec = 2 / (
        dadist * 1000 * (np.pi / 180.0 / 3600.0)
    )  # 2 kpc aperture radius is this many arcsec

    return apr_arcsec


def check_local_radius(redshift, image_fwhm_arcsec):
    """Checks whether filter image FWHM is larger than
    the aperture size"""

    dadist = cosmo.angular_diameter_distance(redshift).value
    apr_arcsec = 2 / (
        dadist * 1000 * (np.pi / 180.0 / 3600.0)
    )  # 2 kpc aperture radius is this many arcsec

    return apr_arcsec > image_fwhm_arcsec


def check_global_contamination(global_aperture_phot, aperture_primary):
    """Checks whether aperture is contaminated by multiple objects"""
    warnings.simplefilter("ignore")
    is_contam = False
    aperture = global_aperture_phot.aperture
    # check both the image used to generate aperture
    # and the image used to measure photometry
    for cutout_name in [
        global_aperture_phot.aperture.cutout.fits.name,
        aperture_primary.cutout.fits.name,
    ]:
        # UV photons are too sparse, segmentation map
        # builder cannot easily handle these
        if "/GALEX/" in cutout_name:
            continue

        # copy the steps to build segmentation map
        image = fits.open(cutout_name)
        wcs = WCS(image[0].header)
        background = estimate_background(image)
        catalog = build_source_catalog(
            image, background, threshhold_sigma=5, npixels=15
        )

        # catalog is None is no sources are detected in the image
        # so we don't have to worry about contamination in that case
        if catalog is None:
            continue

        source_data = match_source(aperture.sky_coord, catalog, wcs)

        mask_image = (
            aperture.sky_aperture.to_pixel(wcs)
            .to_mask()
            .to_image(np.shape(image[0].data))
        )
        obj_ids = catalog._segment_img.data[np.where(mask_image == True)]
        source_obj = source_data._labels

        # let's look for contaminants
        unq_obj_ids = np.unique(obj_ids)
        if len(unq_obj_ids[(unq_obj_ids != 0) & (unq_obj_ids != source_obj)]):
            is_contam = True

    return is_contam


def select_cutout_aperture(cutouts):
    """
    Select cutout for aperture
    """
    filter_names = [
        "PanSTARRS_g",
        "PanSTARRS_r",
        "PanSTARRS_i",
        "SDSS_r",
        "SDSS_i",
        "SDSS_g",
        "DES_r",
        "DES_i",
        "DES_g",
        "2MASS_H",
    ]

    choice = 0
    filter_choice = filter_names[choice]

    while not cutouts.filter(filter__name=filter_choice).exists():
        choice += 1
        filter_choice = filter_names[choice]

    return cutouts.filter(filter__name=filter_choice)


def select_aperture(transient):
    cutouts = Cutout.objects.filter(transient=transient)
    if len(cutouts):
        cutout_for_aperture = select_cutout_aperture(cutouts)
    if len(cutouts) and len(cutout_for_aperture):
        global_aperture = Aperture.objects.filter(
            type__exact="global", transient=transient, cutout=cutout_for_aperture[0]
        )
    else:
        global_aperture = Aperture.objects.none()

    return global_aperture


# def find_host_data(position, name='No name'):
#    """
#    Finds the information about the host galaxy given the position of the supernova.
#    Parameters
#    ----------
#    :position : :class:`~astropy.coordinates.SkyCoord`
#        On Sky position of the source to be matched.
#    :name : str, default='No name'
#        Name of the the object.
#    Returns
#    -------
#    :host_information : ~astropy.coordinates.SkyCoord`
#        Host position
#    """
#    #getGHOST(real=False, verbose=0)
#    host_data = getTransientHosts(snCoord=[position],
#                                         snName=[name],
#                                         verbose=1, starcut='gentle', ascentMatch=True)

# clean up after GHOST...
#    dir_list = glob.glob('transients_*/*/*')
#    for dir in dir_list: os.remove(dir)

#    for level in ['*/*/', '*/']:
#        dir_list = glob.glob('transients_' + level)
#        for dir in dir_list: os.rmdir(dir)


#    if len(host_data) == 0:
#        host_position = None
#    else:
#        host_position = SkyCoord(ra=host_data['raMean'][0],
#                             dec=host_data['decMean'][0],
#                             unit='deg')


#    return host_position


def estimate_background(image):
    """
    Estimates the background of an image
    Parameters
    ----------
    :image : :class:`~astropy.io.fits.HDUList`
        Image to have the background estimated of.
    Returns
    -------
    :background : :class:`~photutils.background.Background2D`
        Background estimate of the image
    """
    image_data = image[0].data
    box_size = int(0.1 * np.sqrt(image_data.size))
    try:
        return Background2D(image_data, box_size=box_size)
    except ValueError:
        return Background2D(image_data, box_size=box_size, exclude_percentile=50)


def construct_aperture(image, position):
    """
    Construct an elliptical aperture at the position in the image
    Parameters
    ----------
    :image : :class:`~astropy.io.fits.HDUList`
    Returns
    -------
    """
    wcs = WCS(image[0].header)
    background = estimate_background(image)

    ### found an edge case where deblending isn't working how I'd like it to
    ### so if it's not finding the host, play with the default threshold
    iter = 0
    source_separation_arcsec = 100
    while source_separation_arcsec > 5 and iter < 5:
        catalog = build_source_catalog(
            image, background, threshhold_sigma=5 * (iter + 1)
        )
        source_data = match_source(position, catalog, wcs)

        source_ra, source_dec = wcs.wcs_pix2world(
            source_data.xcentroid, source_data.ycentroid, 0
        )
        source_position = SkyCoord(source_ra, source_dec, unit=u.deg)
        source_separation_arcsec = position.separation(source_position).arcsec

        iter += 1

    return elliptical_sky_aperture(source_data, wcs)


def query_ned(position):
    """Get a Galaxy's redshift from ned if it is available."""

    result_table = Ned.query_region(position, radius=1.0 * u.arcsec)
    result_table = result_table[result_table["Redshift"].mask == False]

    redshift = result_table["Redshift"].value

    if len(redshift):
        galaxy_data = {"redshift": redshift[0]}
    else:
        galaxy_data = {"redshift": None}

    return galaxy_data


def query_sdss(position):
    """Get a Galaxy's redshift from SDSS if it is available"""
    result_table = SDSS.query_region(position, spectro=True, radius=1.0 * u.arcsec)

    if result_table is not None and "z" in result_table.keys():
        redshift = result_table["z"].value
        if len(redshift) > 0:
            if not math.isnan(redshift[0]):
                galaxy_data = {"redshift": redshift[0]}
            else:
                galaxy_data = {"redshift": None}
        else:
            galaxy_data = {"redshift": None}
    else:
        galaxy_data = {"redshift": None}

    return galaxy_data


def construct_all_apertures(position, image_dict):
    apertures = {}

    for name, image in image_dict.items():
        try:
            aperture = construct_aperture(image, position)
            apertures[name] = aperture
        except:
            print(f"Could not fit aperture to {name} imaging data")

    return apertures


def pick_largest_aperture(position, image_dict):
    """
    Parameters
    ----------
    :position : :class:`~astropy.coordinates.SkyCoord`
        On Sky position of the source which aperture is to be measured.
    :image_dic: dict[str:~astropy.io.fits.HDUList]
        Dictionary of images from different surveys, key is the the survey
        name.
    Returns
    -------
    :largest_aperture: dict[str:~photutils.aperture.SkyEllipticalAperture]
        Dictionary of contain the image with the largest aperture, key is the
         name of the survey.
    """

    apertures = {}

    for name, image in image_dict.items():
        try:
            aperture = construct_aperture(image, position)
            apertures[name] = aperture
        except:
            print(f"Could not fit aperture to {name} imaging data")

    aperture_areas = {}
    for image_name in image_dict:
        aperture_semi_major_axis = apertures[image_name].a
        aperture_semi_minor_axis = apertures[image_name].b
        aperture_area = np.pi * aperture_semi_minor_axis * aperture_semi_major_axis
        aperture_areas[image_name] = aperture_area

    max_size_name = max(aperture_areas, key=aperture_areas.get)
    return {max_size_name: apertures[max_size_name]}
