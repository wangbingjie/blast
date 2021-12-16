from astroquery.vizier import Vizier
from astropy.coordinates import Angle, SkyCoord


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
    # hence why we index at 0 below to get the cloeset match
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
