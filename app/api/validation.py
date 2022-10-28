"""
Helper functions to validate transient data uploads.
"""


def ra_deg_valid(right_ascension_degrees: float) -> bool:
    """
    Check that right ascension in decimal degrees is valid

    parameters:
        right_ascension_degrees ins decimal degrees.
    returns:
        true if right ascension valid, false otherwise.

    """

    if type(right_ascension_degrees) != float:
        valid = False
    elif right_ascension_degrees < 0.0 or right_ascension_degrees > 360.0:
        valid = False
    else:
        valid = True
    return valid


def dec_deg_valid(declination_degrees: float) -> bool:
    """
    Check that declination in decimal degrees is valid.

    parameters:
        declination_degrees: ins decimal degrees.
    returns:
        true if declination valid, false otherwise.

    """
    if type(declination_degrees) != float:
        valid = False
    elif declination_degrees < -90.0 or declination_degrees > 90.0:
        valid = False
    else:
        valid = True
    return valid
