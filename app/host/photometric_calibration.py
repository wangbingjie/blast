import numpy as np


def ab_mag_to_jansky(ab_mag):
    """
    Converts AB magnitude to spectral flux density in units on Janskys.
    """
    return 10.0 ** (-(ab_mag + 48.60) / 2.5)


def ab_mag_to_mJy(ab_mag):
    """
    Converts AB magnitude to spectral flux density in units of microJanskys.
    """
    return 10.0 ** (-(ab_mag + 23.90) / 2.5)


def flux_to_mag(flux, zero_point_mag):
    """
    Converts flux to magnitude
    """
    return -2.5 * np.log10(flux) + zero_point_mag


def fluxerr_to_magerr(flux, fluxerr):
    """
    Converts flux to magnitude
    """
    return 1.0857 * fluxerr / flux


def flux_to_mJy_flux(flux, zero_point_mag_in):
    """
    Converts flux to magnitude
    """
    return flux * 10 ** (-0.4 * (zero_point_mag_in - 23.9))


def fluxerr_to_mJy_fluxerr(fluxerr, zero_point_mag_in):
    """
    Converts flux to magnitude
    """
    return fluxerr * 10 ** (-0.4 * (zero_point_mag_in - 23.9))


def counts_to_flux(counts, exposure_time):
    """
    Converts raw counts to flux data
    """
    return counts / exposure_time


def jansky_to_maggies(flux_density_jansky):
    """
    Converts spectral flux density from Janskys to units of maggies.
    """
    return flux_density_jansky / 3631.0


def mJy_to_maggies(flux_mJy):
    """
    Converts spectral flux density from mJy to units of maggies.
    """
    return flux_mJy * 10 ** (-0.4 * 23.9)


def magnitude_to_flux_density(magnitude, survey):
    return 0.0
