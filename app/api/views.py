import itertools

from django.http import Http404
from host.models import Transient
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from . import datamodel
from .components import data_model_components

class TransientSciencePayload(APIView):

    def get(self, request, slug):
        component_groups = [
            component_group(slug) for component_group in data_model_components
        ]
        components = datamodel.unpack_component_groups(component_groups)
        data = datamodel.serialize_blast_science_data(components)
        return Response(data)

    def post(self, request, slug):
        return 0.0
