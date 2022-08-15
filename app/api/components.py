from datamodel import DataModelComponent
import serializers
from host import models


def transient_component(transient_name) -> list[DataModelComponent]:
    component = DataModelComponent(prefix="transient_",
                                   query={"name__exact": transient_name},
                                   model=models.Transient,
                                   serializer=serializers.TransientSerializer)
    return [component]


def host_component(transient_name) -> list[DataModelComponent]:
    component = DataModelComponent(prefix="host_",
                                   query={"transient__name__exact": transient_name},
                                   model=models.Host,
                                   serializer=serializers.HostSerializer)
    return [component]


def aperture_component(transient_name) -> list[DataModelComponent]:
    components = []
    for aperture_type in ["local", "global"]:
        components.append(
            DataModelComponent(prefix=f"{aperture_type}_",
                               query={"transient__name__exact": transient_name, "type__exact": aperture_type},
                               model=models.Apertuere,
                               serializer=serializers.ApertureSerializer)
        )

    return components


def photometry_component(transient_name) -> list[DataModelComponent]:
    components = []
    filters = models.Filter.objects.all()
    for aperture_type in ["local", "global"]:
        for filter in filters:
            components.append(DataModelComponent(prefix=f"{aperture_type}_{filter.name}_",
                                                 query={
                                                     "transient__name__exact": transient_name,
                                                     "filter__name__exact": filter.name,
                                                     "aperture__type__exact": aperture_type,
                                                 },
                                                 model=models.AperturePhotometry,
                                                 serializer=serializers.AperturePhotometrySerializer
                                                 ))

    return components


data_model_components = [transient_component,
                         host_component,
                         aperture_component,
                         photometry_component]
