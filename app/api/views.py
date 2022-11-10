import itertools

import pandas as pd
from api import validation
from api import upload
from astropy.coordinates import SkyCoord
from host.models import Transient
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.decorators import parser_classes
from rest_framework.parsers import FileUploadParser
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

from . import datamodel
from .components import data_model_components


def transient_exists(transient_name: str) -> bool:
    """
    Checks if a transient exists in the database.

    Parameters:
        transient_name (str): transient_name.
    Returns:
        exisit (bool): True if the transient exists false otherwise.
    """
    try:
        Transient.objects.get(name__exact=transient_name)
        exists = True
    except Transient.DoesNotExist:
        exists = False
    return exists


def ra_dec_valid(ra: str, dec: str) -> bool:
    """
    Checks if a given ra and dec coordinate is valid

    Parameters:
        ra (str): Right
    """
    try:
        ra, dec = float(ra), float(dec)
        coord = SkyCoord(ra=ra, dec=dec, unit="deg")
        valid = True
    except:
        valid = False
    return valid


@api_view(["GET"])
def get_transient_science_payload(request, transient_name):
    if not transient_exists(transient_name):
        return Response(
            {"message": f"{transient_name} not in database"},
            status=status.HTTP_404_NOT_FOUND,
        )

    component_groups = [
        component_group(transient_name) for component_group in data_model_components
    ]
    components = datamodel.unpack_component_groups(component_groups)
    data = datamodel.serialize_blast_science_data(components)
    return Response(data, status=status.HTTP_200_OK)


@api_view(["POST"])
def post_transient(request, transient_name, transient_ra, transient_dec):
    if transient_exists(transient_name):
        return Response(
            {"message": f"{transient_name} already in database"},
            status=status.HTTP_409_CONFLICT,
        )

    if not ra_dec_valid(transient_ra, transient_dec):
        return Response(
            {"message": f"bad ra and dec: ra={transient_ra}, dec={transient_dec}"},
            status.HTTP_400_BAD_REQUEST,
        )

    data_string = (
        f"{transient_name}: ra = {float(transient_ra)}, dec= {float(transient_dec)}"
    )
    Transient.objects.create(
        name=transient_name,
        ra_deg=float(transient_ra),
        dec_deg=float(transient_dec),
        tns_id=1,
    )
    return Response(
        {"message": f"transient successfully posted: {data_string}"},
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@parser_classes([JSONParser])
def upload_transient_data(request):

    data_model = [component(request.data["transient_name"]) for component in data_model_components]
    data_model = datamodel.unpack_component_groups(data_model)
    print(request.data)
    if validation.science_payload_valid(request.data, data_model):
        upload.ingest_uploaded_transient(request.data)
        response = Response(
            request.data["transient_name"], status=status.HTTP_201_CREATED
        )
    else:
        response = Response(
            "Transient data not valid", status=status.HTTP_406_NOT_ACCEPTABLE
        )

    return response
