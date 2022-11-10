"""
Functions to help with the house keeping of uploading transient data
"""
import api.components as api_comp
import api.datamodel as datamodel
import host.models as models
from host.base_tasks import initialise_all_tasks_status

def ingest_uploaded_transient(science_payload, data_model):
    """
    Upload science payload to the database, overwrites transient if
    it already exists.

    parameters:
        science_payload

    returns:
        None, initialized transient so data can be uploaded.
    """
    transient_name = science_payload["transient_name"]

    if models.Transient.objects.filter(name__exact=transient_name).exists():
        remove_transient_data(transient_name)

    components = components_with_model(data_model, models.Transient)
    for component in components:
        serializer = component.serializer()
        serializer.save(science_payload, component)

    transient = models.Transient.objects.get(name__exact=transient_name)
    initialise_all_tasks_status(transient, status_message="processed")
    create_transient_cutout_placeholders(transient_name)

    models_in_order = [models.Host, models.Aperture, models.AperturePhotometry, models.SEDFittingResult]

    for model in models_in_order:
        components = components_with_model(data_model, model)
        for component in components:
            serializer = component.serializer()
            serializer.save(science_payload, component)



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
    ]

    for object in related_objects:
        object.objects.filter(transient__name__exact=transient_name).delete()


def create_transient_cutout_placeholders(transient_name: str):
    """
    Creates cutouts objects in the database so transients can be ingested.

    parameters:
        transient_name: transient to create cutout data placeholders for.
    returns:
        None, saves cutout placeholders to the database.
    """
    transient = models.Transient.objects.get(name__exact=transient_name)
    for filter in models.Filter.objects.all():
        models.Cutout.objects.create(
            filter=filter, transient=transient, name=f"{transient_name}_{filter.name}"
        )


def components_with_model(data_model, django_model):
    """
    Get components from the data_model which correspond to a particular dango model.

    parameters:
        data_model: Full data model
        model: Django model to be searched for

    returns:
        List of Data model components with correspond to the django model.
    """
    return [component for component in data_model if component.model == django_model]