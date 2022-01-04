


def ab_mag_to_jansky(ab_mag):
    """
    Converts AB magnitude to spectral flux density in units on Janskys.
    """
    return 10.0 ** (- (ab_mag + 48.60) / 2.5)


def jansky_to_maggies(flux_density_jansky):
    """
    Converts spectral flux density from Janskys to units of maggies.
    """
    return flux_density_jansky / 3631.0


def magnitude_to_flux_density(magnitude, survey):
    return 0.0