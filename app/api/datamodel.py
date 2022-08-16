from dataclasses import dataclass

import django
from host import models
from rest_framework import serializers


@dataclass
class DataModelComponent:
    prefix: str
    query: dict
    model: django.db.models.Model
    serializer: serializers.Serializer


def serialize_blast_science_data(datamodel) -> dict:
    """
    Serializes all data associated with a transient into a flat structure.
    """
    science_payload = {}
    for component in datamodel:
        prefix, serializer = component.prefix, component.serializer
        try:
            object = component.model.objects.get(**component.query)
            object_data = serializer(object).data
            object_dict = {prefix + name: value for name, value in object_data.items()}
        except:
            object_dict = {prefix + name: None for name in serializer().fields}

        science_payload = {**science_payload, **object_dict}
    return science_payload
