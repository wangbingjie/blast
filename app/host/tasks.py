from __future__ import absolute_import
from __future__ import unicode_literals

from celery import shared_task

from .processing import DeleteGHOSTFiles
from .processing import GhostRunner
from .processing import GlobalApertureConstructionRunner
from .processing import GlobalAperturePhotometry
from .processing import HostInformation
from .processing import HostSEDFitting
from .processing import ImageDownloadRunner
from .processing import IngestMissedTNSTransients
from .processing import InitializeTransientTasks
from .processing import LocalAperturePhotometry
from .processing import SnapshotTaskRegister
from .processing import TNSDataIngestion
from .processing import TransientInformation


periodic_tasks = [
    GhostRunner(),
    ImageDownloadRunner(),
    GlobalApertureConstructionRunner(),
    LocalAperturePhotometry(),
    GlobalAperturePhotometry(),
    TransientInformation(),
    HostInformation(),
    HostSEDFitting(),
    TNSDataIngestion(),
    InitializeTransientTasks(),
    IngestMissedTNSTransients(),
    DeleteGHOSTFiles(),
    SnapshotTaskRegister(),
]


for task in periodic_tasks:
    func_name = task._task_name().replace(" ", "_").lower()
    exec(f"@shared_task\ndef {func_name}(): {type(task).__name__}().run_process()")