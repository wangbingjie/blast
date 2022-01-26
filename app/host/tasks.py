from __future__ import absolute_import, unicode_literals
from celery import shared_task
from .models import Transient
from .transient_name_server import get_recent_transients
import datetime
import os


@shared_task
def ingest_recent_tns_data(interval_minutes=10):
    """
    Download and save recent transients from the transient name server.

    Args:
        interval_minutes (int) : Minutes in the past from when the function is
            called to search the transient name server for new transients.
    Returns:
        None: Transients are saved to the database backend.
    """
    now = datetime.datetime.now()
    time_delta = datetime.timedelta(minutes=interval_minutes)
    recent_transients = get_recent_transients(now-time_delta)
    saved_transients = Transient.objects.all()

    for transient in recent_transients:
        try:
            saved_transients.get(tns_id__exact=transient.tns_id)
        except Transient.DoesNotExist:
            transient.save()

@shared_task
def match_transient_to_host():
    """
    Match a single transient in the database to a host galaxy.
    """
    return None







