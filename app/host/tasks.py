from __future__ import absolute_import
from __future__ import unicode_literals

import os

from celery import shared_task

from .system_tasks import DeleteGHOSTFiles
from .system_tasks import IngestMissedTNSTransients
from .system_tasks import InitializeTransientTasks
from .system_tasks import LogTransientProgress
from .system_tasks import SnapshotTaskRegister
from .system_tasks import TNSDataIngestion
from .transient_tasks import Ghost
from .transient_tasks import GlobalApertureConstruction
from .transient_tasks import GlobalAperturePhotometry
from .transient_tasks import GlobalHostSEDFitting
from .transient_tasks import HostInformation
from .transient_tasks import ImageDownload
from .transient_tasks import LocalAperturePhotometry
from .transient_tasks import LocalHostSEDFitting
from .transient_tasks import MWEBV_Host
from .transient_tasks import MWEBV_Transient
from .transient_tasks import TransientInformation
from .transient_tasks import ValidateGlobalPhotometry
from .transient_tasks import ValidateLocalPhotometry

periodic_tasks = [
    TNSDataIngestion(),
    MWEBV_Transient(),
    Ghost(),
    MWEBV_Host(),
    ImageDownload(),
    GlobalApertureConstruction(),
    LocalAperturePhotometry(),
    GlobalAperturePhotometry(),
    ValidateLocalPhotometry(),
    ValidateGlobalPhotometry(),
    TransientInformation(),
    HostInformation(),
    GlobalHostSEDFitting(),
    LocalHostSEDFitting(),
    InitializeTransientTasks(),
    IngestMissedTNSTransients(),
    DeleteGHOSTFiles(),
    SnapshotTaskRegister(),
    LogTransientProgress(),
]

task_time_limit = int(os.environ.get("TASK_TIME_LIMIT", "3800"))
task_soft_time_limit = int(os.environ.get("TASK_SOFT_TIME_LIMIT", "3600"))
for task in periodic_tasks:
    func_name = task.task_name.replace(" ", "_").lower()
    exec(
        f"""
@shared_task(time_limit={task_time_limit},soft_time_limit={task_soft_time_limit})
def {func_name}():

    {type(task).__name__}().run_process()

    return
"""
    )
