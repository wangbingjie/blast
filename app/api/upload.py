"""
Functions to help with the house keeping of uploading transient data
"""
import host.models as models


def ingest_uploaded_transient(sciennce_payload, transient_data_model_component):
    """

    parameters
        sciennce_payload
        transient_data_model_component
    Returns
        None, initialized transient so data can be uploaded.

    """
    pass


def remove_transient_data(transient_name):
    """
    Remove all data association with transient.

    parameters
        transient_name: Name of the transient (e.g. 2022ann)
    returns
        None, removes all data associated with tranisent
    """
    models.Transient.objects.filter(name__exact=transient_name).delete()
    related_objects = [
        models.TaskRegister,
        models.Aperture,
        models.Cutout,
        models.Host,
        models.AperturePhotometry,
        models.SEDFittingResult,
        models.TaskRegisterSnapShot,
    ]

    for object in related_objects:
        object.objects.filter(transient__name___exact=transient_name).delete()
