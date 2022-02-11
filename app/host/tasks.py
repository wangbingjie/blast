from __future__ import absolute_import, unicode_literals
from celery import shared_task
from .models import Transient, Task, TransientProcessingStatus, Status
from .transient_name_server import get_transients_from_tns
from .transient_name_server import get_tns_credentials
from .ghost import run_ghost
from .cutouts import download_and_save_cutouts
import datetime
from django.utils import timezone
import glob
import shutil


def set_transient_processing_status(transient):
    tasks = Task.objects.all()
    not_processed = Status.objects.get(message__exact='not processed')

    for task in tasks:
        processing_status = TransientProcessingStatus(task=task,
                                                      transient=transient,
                                                      status=not_processed)
        processing_status.save()

@shared_task
def ingest_recent_tns_data(interval_minutes=1000):
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
    recent_transients = get_transients_from_tns(now-time_delta,
                                                tns_credentials=tns_credentials)
    saved_transients = Transient.objects.all()

    for transient in recent_transients:
        try:
            saved_transients.get(tns_name__exact=transient.tns_name)
        except Transient.DoesNotExist:
            transient.save()
            set_transient_processing_status(transient)




@shared_task
def match_transient_to_host():
    """
    Match a single transient in the database to a host galaxy.

    Returns:
        (None): Matches host to transient
    """
    unmatched = Transient.objects.filter(
        host_match_status__exact='not processed')

    if unmatched.exists():
        transient = unmatched.order_by('public_timestamp')[0]
        transient.host_match_status = 'processing'
        transient.save()

        try:
            host = run_ghost(transient)
        except:
            host = None
            transient.host_match_status = 'failed'
            transient.save()

        if host is not None:
            host.save()
            transient.host = host
            transient.host_match_status = 'processed'
            transient.save()
        else:
            transient.host_match_status = 'no match'
            transient.save()


@shared_task
def download_cutouts():
    """
    Downloads cutout data for a single transient
    """
    no_images = Transient.objects.filter(
        image_download_status__exact='not processed')

    if no_images.exists():
        transient = no_images.order_by('public_timestamp')[0]
        transient.image_download_status = 'processing'
        transient.save()

        try:
            download_and_save_cutouts(transient)
        except:
            transient.image_download_status = 'failed'
            transient.save()

        transient.image_download_status = 'processed'
        transient.save()


@shared_task
def download_host_catalog_photometry():
    """
    Downloads host catalog photometry
    """
    matched_transients = Transient.objects.filter(
        host_match_status__exact='processed',
        catalog_photometry_status__exact=' not processed'
        )

    if matched_transients.exists():
        transient = matched_transients.order_by('public_timestamp')[0]
        transient.image_download_status = 'processing'
        transient.save()

@shared_task
def delete_ghost_file_logs():
    """
    Removes GHOST files
    """
    dir_list = glob.glob('transients_*/')

    for dir in dir_list:
        try:
            shutil.rmtree(dir)
        except OSError as e:
            print("Error: %s : %s" % (dir, e.strerror))

    dir_list = glob.glob('quiverMaps/')

    for dir in dir_list:
        try:
            shutil.rmtree(dir)
        except OSError as e:
            print("Error: %s : %s" % (dir, e.strerror))










