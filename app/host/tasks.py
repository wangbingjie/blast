from __future__ import absolute_import
from __future__ import unicode_literals

import datetime
import glob
import shutil

from celery import shared_task
from django.conf import settings
from django.utils import timezone

from .models import TaskRegisterSnapshot
from .models import Transient
from .processing import GhostRunner
from .processing import GlobalApertureConstructionRunner
from .processing import GlobalAperturePhotometry
from .processing import HostInformation
from .processing import HostSEDFitting
from .processing import ImageDownloadRunner
from .processing import initialise_all_tasks_status
from .processing import LocalAperturePhotometry
from .processing import TransientInformation
from .transient_name_server import get_daily_tns_staging_csv
from .transient_name_server import get_tns_credentials
from .transient_name_server import get_transients_from_tns
from .transient_name_server import tns_staging_blast_transient
from .transient_name_server import tns_staging_file_date_name
from .transient_name_server import update_blast_transient


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


@shared_task
def initialize_transient_tasks():
    """
    Initializes all task in the database to not processed for new transients.
    """

    uninitialized_transients = Transient.objects.filter(
        tasks_initialized__exact="False"
    )
    for transient in uninitialized_transients:
        initialise_all_tasks_status(transient)
        transient.tasks_initialized = "True"
        transient.save()


@shared_task
def snapshot_task_register():
    """
    Takes snapshot of task register for diagnostic purposes.
    """
    transients = Transient.objects.all()
    total, completed, waiting, not_completed = 0, 0, 0, 0

    for transient in transients:
        total += 1
        if transient.progress == 100:
            completed += 1
        if transient.progress == 0:
            waiting += 1
        if transient.progress < 100:
            not_completed += 1

    now = timezone.now()

    for aggregate, label in zip(
        [not_completed, total, completed, waiting],
        ["not completed", "total", "completed", "waiting"],
    ):

        TaskRegisterSnapshot.objects.create(
            time=now, number_of_transients=aggregate, aggregate_type=label
        )


@shared_task
def get_missed_and_update_transients_tns():
    """
    Gets missed transients from tns and update them using the daily staging csv
    """
    yesterday = timezone.now() - datetime.timedelta(days=1)
    date_string = tns_staging_file_date_name(yesterday)
    data = get_daily_tns_staging_csv(
        date_string,
        tns_credentials=get_tns_credentials(),
        save_dir=settings.TNS_STAGING_ROOT,
    )
    saved_transients = Transient.objects.all()

    for _, transient in data.iterrows():
        # if transient exists update it
        try:
            blast_transient = saved_transients.get(name__exact=transient["name"])
            update_blast_transient(blast_transient, transient)
        # if transient does not exist add it
        except Transient.DoesNotExist:
            blast_transient = tns_staging_blast_transient(transient)
            blast_transient.save()


# get_transient_information = TransientInformation().celery_task()


@shared_task
def host_information():
    """
    Get infotmation on the host
    """
    HostInformation().run_process()


@shared_task
def transient_information():
    """
    Get infotmation on the transient
    """
    TransientInformation().run_process()


@shared_task
def global_aperture_photometry():
    """ """
    GlobalAperturePhotometry().run_process()


@shared_task
def global_aperture_construction():
    """ """

    GlobalApertureConstructionRunner().run_process()


@shared_task
def local_aperture_photometry():
    """ """
    LocalAperturePhotometry().run_process()


@shared_task
def host_match():
    """
    Match a single transient in the database to a host galaxy.

    Returns:
        (None): Matches host to transient
    """

    GhostRunner().run_process()


@shared_task
def global_host_sed_inference():
    """
    Runs fits to global host aperture photometry
    """
    HostSEDFitting().run_process()


@shared_task
def cutout_download():
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
