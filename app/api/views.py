import itertools

from host.models import Transient
from rest_framework.decorators import api_view
from rest_framework.response import Response

from . import datamodel
from .components import data_model_components


@api_view(["Get"])
def transient_data(request, slug):
    component_groups = [
        component_group(slug) for component_group in data_model_components
    ]
    # flatten the component groups
    components = list(itertools.chain(component_groups))
    data = datamodel.serialize_blast_science_data(components)
    return Response(data)
