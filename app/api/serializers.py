from host.models import Transient


def serialize_transient_data(transient) -> dict:
    """
    Serializes all data associated with a transient
    """

    return {"transient_name": transient.name,
            "transient_ra": transient.ra_deg,
            "transient_dec": transient.dec_deg,
            "host_name": transient.host.name,
            "host_ra": transient.host.ra_deg,
            "host_dec": transient.host.dec_deg,
            }



