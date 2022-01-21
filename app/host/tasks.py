from celery import shared_task

@shared_task
def test_task(x,y):
    return x + y

@shared_task
def ingest_recent_tns_data():


