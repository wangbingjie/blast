from host.models import Transient
from rest_framework.decorators import api_view
from rest_framework.response import Response

from . import serializers


@api_view(["Get"])
def transient_data(request, slug):
    data = serializers.serialize_blast_science_data(slug)
    return Response(data)
