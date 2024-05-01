import itertools

import django_filters
from astropy.coordinates import SkyCoord
from django_filters.rest_framework import DjangoFilterBackend
from host.models import *
from host.models import Transient
from rest_framework import generics
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from . import datamodel
from . import serializers
from .components import data_model_components


### Filter Sets ###
class TransientFilter(django_filters.FilterSet):
    redshift_lte = django_filters.NumberFilter(field_name="redshift", lookup_expr="lte")
    redshift_gte = django_filters.NumberFilter(field_name="redshift", lookup_expr="gte")

    class Meta:
        model = Transient
        fields = ("name",)


### Filter Sets ###
class HostFilter(django_filters.FilterSet):
    redshift_lte = django_filters.NumberFilter(field_name="redshift", lookup_expr="lte")
    redshift_gte = django_filters.NumberFilter(field_name="redshift", lookup_expr="gte")
    photometric_redshift_lte = django_filters.NumberFilter(
        field_name="photometric_redshift", lookup_expr="lte"
    )
    photometric_redshift_gte = django_filters.NumberFilter(
        field_name="photometric_redshift", lookup_expr="gte"
    )

    class Meta:
        model = Host
        fields = ("name",)


class ApertureFilter(django_filters.FilterSet):
    transient = django_filters.Filter(field_name="transient__name")

    class Meta:
        model = Aperture
        fields = ()


class TaskRegisterFilter(django_filters.FilterSet):
    transient = django_filters.Filter(field_name="transient__name")
    status = django_filters.Filter(field_name="status__message")
    task = django_filters.Filter(field_name="task__name")

    class Meta:
        model = TaskRegister
        fields = ()


class FilterFilter(django_filters.FilterSet):
    class Meta:
        model = Filter
        fields = ("name",)


class CutoutFilter(django_filters.FilterSet):
    filter = django_filters.Filter(field_name="filter__name")
    transient = django_filters.Filter(field_name="transient__name")

    class Meta:
        model = Cutout
        fields = ("name",)


class AperturePhotometryFilter(django_filters.FilterSet):
    filter = django_filters.Filter(field_name="filter__name")
    transient = django_filters.Filter(field_name="transient__name")

    class Meta:
        model = AperturePhotometry
        fields = ()


class SEDFittingResultFilter(django_filters.FilterSet):
    transient = django_filters.Filter(field_name="transient__name")
    aperture_type = django_filters.Filter(field_name="aperture__type")

    class Meta:
        model = SEDFittingResult
        fields = ()


### ViewSets ###
class TransientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Transient.objects.all()
    serializer_class = serializers.TransientSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = TransientFilter


class ApertureViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Aperture.objects.all()
    serializer_class = serializers.ApertureSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ApertureFilter


class CutoutViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Cutout.objects.all()
    serializer_class = serializers.CutoutSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = CutoutFilter


class FilterViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Filter.objects.all()
    serializer_class = serializers.FilterSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = FilterFilter


class AperturePhotometryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AperturePhotometry.objects.all()
    serializer_class = serializers.AperturePhotometrySerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = AperturePhotometryFilter


class SEDFittingResultViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SEDFittingResult.objects.all()
    serializer_class = serializers.SEDFittingResultSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = SEDFittingResultFilter


class TaskRegisterViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TaskRegister.objects.all()
    serializer_class = serializers.TaskRegisterSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TaskRegisterFilter


class TaskViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Task.objects.all()
    serializer_class = serializers.TaskSerializer


class HostViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Host.objects.all()
    serializer_class = serializers.HostSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = HostFilter


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


@api_view(["PUT"])
def launch_workflow(request, transient_name):
    # transient_name = request.data['transient_name']
    print(f'''Launching workflow for "{transient_name}..."''')
    from host.transient_tasks import first, second
    sig = first.s(transient_name)
    result = sig()
    return Response({'message': f'''You launched a workflow for transient "{transient_name}": {sig}, {result}.'''}, status=status.HTTP_200_OK)


from host.tasks import initialize_transient_task
from host.tasks import snapshot_task_register
from host.tasks import log_transient_processing_status
from host.tasks import transient_mwebv
from host.tasks import host_match
from host.tasks import host_mwebv
from host.tasks import cutout_download
from host.tasks import transient_information
from host.tasks import host_information
from host.tasks import local_host_sed_inference
from host.tasks import global_host_sed_inference
from host.tasks import local_aperture_photometry
from host.tasks import validate_local_photometry
from host.tasks import global_aperture_construction
from host.tasks import global_aperture_photometry
from host.tasks import validate_global_photometry


@api_view(["PUT"])
def launch_tasks(request):
    # transient_name = request.data['transient_name']
    print('Launching tasks...')
    # General tasks
    initialize_transient_task.delay()
    snapshot_task_register.delay()
    log_transient_processing_status.delay()
    # Transient workflow tasks
    transient_information.delay()
    transient_mwebv.delay()
    cutout_download.delay()
    host_match.delay()
    host_mwebv.delay()
    host_information.delay()
    global_aperture_construction.delay()
    global_aperture_photometry.delay()
    validate_global_photometry.delay()
    local_aperture_photometry.delay()
    validate_local_photometry.delay()
    local_host_sed_inference.delay()
    global_host_sed_inference.delay()
    return Response({'message': ''}, status=status.HTTP_200_OK)


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
