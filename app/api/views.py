from rest_framework.decorators import api_view
from rest_framework.response import Response
from . import serializers
from host.models import Transient


@api_view(["Get"])
def transient_data(request, slug):

    try:
        transient = Transient.objects.get(name__exact=slug)
        data = serializers.serialize_transient_data(transient)
    except:
        data = {"Transient not in blast database"}

    return Response(data)