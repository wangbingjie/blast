from astro_ghost.ghostHelperFunctions import getGHOST
from astro_ghost.ghostHelperFunctions import getTransientHosts
from astropy.coordinates import SkyCoord


def ghost(transient_position, output_dir=""):
    """
    Finds the information about the host galaxy given the position of the supernova.
    Parameters
    ----------
    :position : :class:`~astropy.coordinates.SkyCoord`
        On Sky position of the source to be matched.
    :name : str, default='No name'
        Name of the the object.
    Returns
    -------
    :host_information : ~astropy.coordinates.SkyCoord`
        Host position
    """
    getGHOST(real=False, verbose=1)
    host_data = getTransientHosts(
        snCoord=[transient_position],
        snName=["name"],
        verbose=1,
        savepath=output_dir,
        starcut="gentle",
        # ascentMatch=False,
    )

    if len(host_data) == 0:
        host_position, host_name = None, None
    else:
        host_position = SkyCoord(
            ra=host_data["raMean"][0], dec=host_data["decMean"][0], unit="deg"
        )
        host_name = host_data["objName"][0]

    return {"host_position": host_position, "host_name": host_name}
