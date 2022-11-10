"""
Functions to help with the house keeping of uploading transient data
"""
import api.components as api_comp
import api.datamodel as datamodel
import host.models as models


def ingest_uploaded_transient(science_payload):
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

    transient_component = api_comp.transient_component(transient_name)

    transient_serializer = transient_component[0].serializer(data=transient_data)
    transient_serializer.is_valid()
    transient_serializer.save()

    create_transient_cutout_placeholders(transient_name)

    data_model = [
        api_comp.host_component,
        api_comp.aperture_component,
        api_comp.photometry_component,
        api_comp.sed_fit_component,
    ]
    component_groups = [
        component_group(transient_name) for component_group in data_model
    ]
    components = datamodel.unpack_component_groups(component_groups)

    for comp in components:
        print(comp)
        data = comp.serializer().science_payload_to_model_data(science_payload, comp)
        print(data)
        serializer = comp.serializer(data=data)
        serializer.is_valid()
        serializer.save()


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
