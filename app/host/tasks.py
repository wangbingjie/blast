from __future__ import absolute_import, unicode_literals
from celery import shared_task
import host.models as models
from host.transient_name_server import ingest_new_transients
import datetime

@shared_task
def ingest_recent_tns_data(interval_minutes):
    """
    Download and save recent transients from the transient name server.

    Args:
        interval_minutes (int) : Minutes in the past from when the function is
            called to search the transient name server for new transients.
    Returns:
        None: Transients are saved to the database backend.
    """
    now = datetime.datetime.now()
    ingest_new_transients(now-datetime.timedelta(minutes=interval_minutes))

@shared_task
def match_transient_to_host():
    """
    Match a single transient in the database to a host galaxy.
    """
    models.Transient()






