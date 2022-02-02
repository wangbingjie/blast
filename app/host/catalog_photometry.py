from astroquery.vizier import Vizier
from astropy.coordinates import Angle, SkyCoord
from astropy.io.votable import parse


def catalog_photometry(position, catalog, search_radius=Angle(1.0, unit='arcsec')):
    """
    Downloads catalog photometry for the closest match within a given search
    radius.

    Parameters
    ---------
    :position : :class:`~astropy.coordinates.SkyCoord`
        On Sky position of to be queried
    : catalog: object containing data about the a given catalog
    :search_radius:class:`~astropy.units.Quantity`,
    default=Quantity(1.0,unit='arsec'). Angular search radius.
    Returns
    -------
    :photometry: dictionary of photometry, or None if there is no
    photometry available.
    """
    columns = [catalog.ra, catalog.dec, catalog.id, catalog.mag,
               catalog.mag_error]

    # _r is the separation between matches, + sorts the table by closest match
    # hence why we index at 0 below to get the closet match
    vizier = Vizier(columns=columns + ["+_r"])
    results = vizier.query_region(position,
                                  radius=search_radius,
                                  catalog=catalog.vizier_id)

    if len(results) == 0:
        photometry_dict = None
    else:
        result = results[0][0]
        photometry_dict = {'catalog_name': catalog.name,
                           'ra': result[catalog.ra],
                           'dec': result[catalog.dec],
                           'mag': result[catalog.mag],
                           'mag_error': result[catalog.mag_error]}
    return photometry_dict


def filter_information(catalog):
    """
    Downloads characteristics of the the photometric filter of a catalog
    from the VOSA filter profile service

    Parameters
    ----------
    catalog: caltalog object: contains information on the catalog
    Returns
    -------
    filter_profile: dictionary that contains filter information
    """
    filter = catalog.vosa_filter_id
    votable = parse(f'http://svo2.cab.inta-csic.es/theory/fps/fps.php?ID={filter}')
    params = votable.get_first_table().params
    param_dict = {param.name: param.value for param in params}
    param_dict['name'] = catalog.name
    return param_dict


def download_catalog_data(position, catalog_list):
    """
    Downloads all available matched catalog data for the position
    """
    catalog_data = [catalog_photometry(position, catalog)
                    for catalog in catalog_list]
    return {catalog.name: data for
            catalog, data in zip(catalog_list, catalog_data)
            if data is not None}















