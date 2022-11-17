"""
Helper functions to validate transient data uploads.
"""

from astropy.io import fits

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


def science_payload_valid(science_payload: dict, data_model) -> bool:
    """
    Check if a science payload is valid under a given data model.

    parameters:
        science_payload: science payload to be validated
        data_model: data model used to construct the science payload
    returns:
        True if science payload is valid, False otherwise.
    """
    all_column_names = science_payload.keys()

    for component in data_model:
        column_names = [name for name in all_column_names if component.prefix in name]
        record_names = [name.replace(component.prefix, "") for name in column_names]
        data = {
            record: science_payload[column]
            for column, record in zip(column_names, record_names)
        }
        serializer = component.serializer(data=data)
        if not serializer.is_valid():
            return False

    return True

def valid_fits_file(file) -> bool:
    """
    Test if file is valid fits file.

    parameters:
        file: file to be tested.

    returns:
        True if valid fits image file, False otherwise.
    """
    try:
        file = fits.open(file)
        is_valid = True
    except OSError:
        is_valid = False
    return is_valid
