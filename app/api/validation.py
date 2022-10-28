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


def science_payload_valid(science_payload: dict, datamodel) -> bool:
    """
    Check if a science payload is valid under a given data model.

    parameters:
        science_payload: science payload to be validated.
        datamodel: datamodel used to construct the scicne payload
    returns:
        True if science payload is valid, False otherwise.
    """
    column_names = science_payload.keys()

    for compoment in datamodel:
        column_names = [name for name in column_names if compoment.prefix in name]
        record_names = [name.replace(compoment.prefix, "") for name in column_names]
        data = {record: science_payload[column] for column, record in zip(column_names, record_names)}

        if not compoment.serializer(data=data).is_valid():
            return False

    return True


