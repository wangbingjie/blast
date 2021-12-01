from collections import namedtuple
import yaml
import numpy as np
from astropy.units import Quantity
import astropy.units as u
from astroquery.hips2fits import hips2fits
from photutils.segmentation import detect_threshold, detect_sources,deblend_sources,SourceCatalog
from photutils.aperture import EllipticalAperture
from astropy.coordinates import SkyCoord
#from astro_ghost.ghostHelperFunctions import getTransientHosts
import os
import glob
from photutils.background import Background2D
from astropy.wcs import WCS

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
    Survey = namedtuple('Survey', ['name'] + data_fields)

    survey_list = []
    for name in survey_metadata:
        field_dict = {field: survey_metadata[name][field] for field in data_fields}
        field_dict['name'] = name
        survey_list.append(Survey(**field_dict))

    return survey_list


def image_contains_data(image):
    """
    Checks if a fits image contains data and is not empty
    Parameters
    ----------
    :image : :class:`~astropy.io.fits.HDUList`
        Fits image to check.
    Returns
    -------
    : contains data: bool
        True if the image contains some non-nan data, false otherwise.
    """
    return not np.all(np.isnan(image[0].data))


def cutout(position, survey, fov=Quantity(0.2, unit='deg')):
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
    num_pixels = fov.to(u.arcsec).value / survey.pixel_size_arcsec
    try:
        fits = hips2fits.query(hips=survey.hips_id, ra=position.ra,
                               dec=position.dec, width=int(num_pixels),
                               height=int(num_pixels), fov=fov,
                               projection='TAN', format='fits')
        print(f'Successfully downloaded {survey.name} data')
    except:
        print(f'Conection timed out, could not download {survey.name} data')
        fits = None
    return fits


def download_image_data(position, survey_list, fov=Quantity(0.2, unit='deg')):
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
    images = [cutout(position, survey, fov=fov) for survey in survey_list]
    return {survey.name: image for survey, image in zip(survey_list, images)
              if image is not None and image_contains_data(image)}


def build_source_catalog(image, background, threshhold_sigma=2.0, npixels=10):
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
    segmentation = detect_sources(background_subtracted_data, threshold, npixels=npixels)
    deblended_segmentation = deblend_sources(background_subtracted_data, segmentation, npixels=npixels)
    return SourceCatalog(background_subtracted_data, deblended_segmentation)

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
    source_x_pixels, source_y_pixels = source_catalog.xcentroid, source_catalog.ycentroid
    closest_source_index = np.argmin(np.hypot(host_x_pixel - source_x_pixels,
                                              host_y_pixel - source_y_pixels))

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
    print(source_catalog)
    semi_major_axis = source_catalog.semimajor_sigma.value * aperture_scale
    semi_minor_axis = source_catalog.semiminor_sigma.value * aperture_scale
    orientation_angle = source_catalog.orientation.to(u.rad).value
    pixel_aperture = EllipticalAperture(center, semi_major_axis,
                                        semi_minor_axis, theta=orientation_angle)
    return pixel_aperture.to_sky(wcs)


#def find_host_data(position, name='No name'):
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
    box_size = int(0.01 * np.sqrt(image_data.size))
    return Background2D(image_data, box_size=box_size)


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
    catalog = build_source_catalog(image, background)
    source_data = match_source(position, catalog, wcs)
    print(f'source data: {source_data}')
    return elliptical_sky_aperture(source_data, wcs)

def construct_all_apertures(position, image_dict):
    apertures = {}

    for name, image in image_dict.items():
        try:
            aperture = construct_aperture(image, position)
            apertures[name] = aperture
        except:
            print(f'Could not fit aperture to {name} imaging data')

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
            print(f'Could not fit aperture to {name} imaging data')


    aperture_areas = {}
    for image_name in image_dict:
        aperture_semi_major_axis = apertures[image_name].a
        aperture_semi_minor_axis = apertures[image_name].b
        aperture_area = np.pi * aperture_semi_minor_axis * aperture_semi_major_axis
        aperture_areas[image_name] = aperture_area

    max_size_name = max(aperture_areas, key = aperture_areas.get)
    return {max_size_name : apertures[max_size_name]}