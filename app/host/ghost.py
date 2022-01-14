from astro_ghost.ghostHelperFunctions import getTransientHosts, getGHOST
from astropy.coordinates import SkyCoord
import glob
import os
from .models import Host


def run_ghost(transient):
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
    transient_position = SkyCoord(ra=transient.ra_deg,
                                  dec=transient.dec_deg,
                                  unit='deg')
    host_data = getTransientHosts(snCoord=[transient_position],
                                  snName=[transient.name],
                                  verbose=1,
                                  starcut='gentle',
                                  ascentMatch=True)

    # clean up after GHOST...
    dir_list = glob.glob('transients_*/*/*')
    for dir in dir_list: os.remove(dir)

    for level in ['*/*/', '*/']:
        dir_list = glob.glob('transients_' + level)
        for dir in dir_list: os.rmdir(dir)

    if len(host_data) == 0:
        host = None
    else:
        host = Host(ra_deg=host_data['raMean'][0],
                    dec_deg=host_data['raMean'][0],
                    name='test')

    return host


def find_and_save_host(transient):
    """
    Runs matching algorthim to find host save it to the database.
    """
    getGHOST(real=False, verbose=1)
    host = run_ghost(transient)
    if host is not None:
        host.save()
        transient.host = host
        transient.save()
    return host


