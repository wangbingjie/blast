from __future__ import absolute_import, unicode_literals
from celery import shared_task
from host.transient_name_server import ingest_new_transients
import datetime

@shared_task()
def ingest_recent_tns_data():
    time_after = datetime.datetime.now() - datetime.timedelta(hours=3)
    ingest_new_transients(time_after)








