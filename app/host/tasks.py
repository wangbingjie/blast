from __future__ import absolute_import
from __future__ import unicode_literals

from celery import shared_task
from host.base_tasks import task_soft_time_limit
from host.base_tasks import task_time_limit
from host.workflow import transient_workflow
from .models import Transient
from host.system_tasks import DeleteGHOSTFiles
from host.system_tasks import IngestMissedTNSTransients
from host.system_tasks import InitializeTransientTasks
from host.system_tasks import LogTransientProgress
from host.system_tasks import SnapshotTaskRegister
from host.system_tasks import TNSDataIngestion
from .transient_name_server import get_transients_from_tns_by_name

periodic_tasks = [
    TNSDataIngestion(),
    InitializeTransientTasks(),
    SnapshotTaskRegister(),
    LogTransientProgress(),
    # DeleteGHOSTFiles(),
    # IngestMissedTNSTransients(),
]


@shared_task(
    name="Import transients from TNS",
    time_limit=task_time_limit,
    soft_time_limit=task_soft_time_limit,
)
def import_transient_list(transient_names):
    uploaded_transient_names = []
    blast_transients = get_transients_from_tns_by_name(transient_names)
    saved_transients = Transient.objects.all()
    for transient in blast_transients:
        try:
            saved_transients.get(name__exact=transient.name)
        except Transient.DoesNotExist:
            # transient.added_by = request.User
            transient.save()
            transient_workflow.delay(transient.name)

        uploaded_transient_names += [transient.name]
    return uploaded_transient_names
