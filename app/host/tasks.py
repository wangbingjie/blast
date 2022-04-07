from __future__ import absolute_import
from __future__ import unicode_literals

import datetime
import glob
import shutil

from celery import shared_task
from django.utils import timezone

from .cutouts import download_and_save_cutouts
from .ghost import run_ghost
from .models import Status
from .models import Task
from .models import TaskRegister
from .models import Transient
from .processing import GhostRunner
from .processing import ImageDownloadRunner
from .processing import initialise_all_tasks_status
from .processing import update_status
from .transient_name_server import get_tns_credentials
from .transient_name_server import get_transients_from_tns


@shared_task
def ingest_recent_tns_data(interval_minutes=100):
    """
    Download and save recent transients from the transient name server.

    Args:
        interval_minutes (int) : Minutes in the past from when the function is
            called to search the transient name server for new transients.
    Returns:
        (None): Transients are saved to the database backend.
    """
    now = timezone.now()
    time_delta = datetime.timedelta(minutes=interval_minutes)
    tns_credentials = get_tns_credentials()
    recent_transients = get_transients_from_tns(
        now - time_delta, tns_credentials=tns_credentials
    )
    saved_transients = Transient.objects.all()

    for transient in recent_transients:
        try:
            saved_transients.get(name__exact=transient.name)
        except Transient.DoesNotExist:
            transient.save()
            initialise_all_tasks_status(transient)


@shared_task
def match_transient_to_host():
    """
    Match a single transient in the database to a host galaxy.

    Returns:
        (None): Matches host to transient
    """

    GhostRunner().run_process()


@shared_task
def download_cutouts():
    """
    Downloads cutout data for a single transient
    """
    ImageDownloadRunner().run_process()


@shared_task
def download_host_catalog_photometry():
    """
    Downloads host catalog photometry
    """
    matched_transients = Transient.objects.filter(
        host_match_status__exact="processed",
        catalog_photometry_status__exact=" not processed",
    )

    if matched_transients.exists():
        transient = matched_transients.order_by("public_timestamp")[0]
        transient.image_download_status = "processing"
        transient.save()


@shared_task
def delete_ghost_file_logs():
    """
    Removes GHOST files
    """
    dir_list = glob.glob("transients_*/")

    for dir in dir_list:
        try:
            shutil.rmtree(dir)
        except OSError as e:
            print("Error: %s : %s" % (dir, e.strerror))

    dir_list = glob.glob("quiverMaps/")

    for dir in dir_list:
        try:
            shutil.rmtree(dir)
        except OSError as e:
            print("Error: %s : %s" % (dir, e.strerror))
