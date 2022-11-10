"""
This module contains definitions of the science payload components. Functions
that turn blast database scheme into a flat science payload to be served through
the API.
"""
from typing import List

from api.datamodel import DataModelComponent
from api.datamodel import unpack_component_groups
from host import models

from . import serializers


def transient_component(transient_name) -> List[DataModelComponent]:
    """
    Transient model component defined what transient information is in the
    science payload.

    parameters:
        transient_name (str): name of the transient.
    returns:
        component (List[DataModelComponent]): data model component to be added
            to the blast science payload.

    """
    component = DataModelComponent(
        prefix="transient_",
        query={"name__exact": transient_name},
        model=models.Transient,
        serializer=serializers.TransientSerializer,
    )
    return [component]


def host_component(transient_name) -> List[DataModelComponent]:
    """
    Host model component defined what transient information is in the
    science payload.

    parameters:
        transient_name (str): name of the transient.
    returns:
        component (List[DataModelComponent]): data model component to be added
            to the blast science payload.
    """
    component = DataModelComponent(
        prefix="host_",
        query={"transient__name__exact": transient_name},
        model=models.Host,
        serializer=serializers.HostSerializer,
    )
    return [component]


def aperture_component(transient_name) -> List[DataModelComponent]:
    """
    Apeture model component defined what transient information is in the
    science payload.

    parameters:
        transient_name (str): name of the transient.
    returns:
        component (List[DataModelComponent]): data model component to be added
            to the blast science payload.
    """
    components = []
    for aperture_type in ["local", "global"]:
        components.append(
            DataModelComponent(
                prefix=f"aperture_{aperture_type}_",
                query={
                    "transient__name__exact": transient_name,
                    "type__exact": aperture_type,
                },
                model=models.Aperture,
                serializer=serializers.ApertureSerializer,
            )
        )

    return components


def photometry_component(transient_name) -> List[DataModelComponent]:
    """
    Photometry model component defined what transient information is in the
    science payload.

    parameters:
        transient_name (str): name of the transient.
    returns:
        component (List[DataModelComponent]): data model component to be added
            to the blast science payload.
    """
    components = []
    filters = models.Filter.objects.all()
    for aperture_type in ["local", "global"]:
        for filter in filters:
            components.append(
                DataModelComponent(
                    prefix=f"{aperture_type}_aperture_{filter.name}_",
                    query={
                        "transient__name__exact": transient_name,
                        "filter__name__exact": filter.name,
                        "aperture__type__exact": aperture_type,
                    },
                    model=models.AperturePhotometry,
                    serializer=serializers.AperturePhotometrySerializer,
                )
            )

    return components


def sed_fit_component(transient_name: str) -> List[DataModelComponent]:
    """
    SED fit component which defines what is in the blast science payload.

    parameter:
        transient_name (str): name of the transient
    returns:
        component (List[DataModelComponent]): data model component to be added
            to the blast science payload.
    """
    components = []
    for aperture_type in ["local", "global"]:
        components.append(
            DataModelComponent(
                prefix=f"{aperture_type}_aperture_host_",
                query={
                    "transient__name__exact": transient_name,
                    "aperture__type__exact": aperture_type,
                },
                model=models.SEDFittingResult,
                serializer=serializers.SEDFittingResultSerializer,
            )
        )
    return components


data_model_components = [
    transient_component,
    host_component,
    aperture_component,
    photometry_component,
    sed_fit_component,
]


def transient_data_model_components(
    transient_name: str, components=data_model_components
) -> List[DataModelComponent]:
    """
    Get all data model components for a transient.

    Parameters
        transient_name: Name of the transient e.g. 2022ann
        components: List of data model components for the transient
    Returns
        List of data model components
    """

    data_model = [component(transient_name) for component in components]
    return unpack_component_groups(data_model)
