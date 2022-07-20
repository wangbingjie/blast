from __future__ import absolute_import
from __future__ import unicode_literals


from celery import shared_task

from .processing import GhostRunner
from .processing import GlobalApertureConstructionRunner
from .processing import GlobalAperturePhotometry
from .processing import HostInformation
from .processing import HostSEDFitting
from .processing import ImageDownloadRunner
from .processing import LocalAperturePhotometry
from .processing import TransientInformation
from .processing import TNSDataIngestion
from .processing import InitializeTransientTasks
from .processing import IngestMissedTNSTransients
from .processing import DeleteGHOSTFiles
from .processing import SnapshotTaskRegister


periodic_tasks = [GhostRunner(),ImageDownloadRunner(),
                  GlobalApertureConstructionRunner(), LocalAperturePhotometry(),
                  GlobalAperturePhotometry(),TransientInformation(), HostInformation(),
                  HostSEDFitting(), TNSDataIngestion(), InitializeTransientTasks(),
                  IngestMissedTNSTransients(), DeleteGHOSTFiles(), SnapshotTaskRegister()]


for task in periodic_tasks:
    func_name = task._task_name().replace(" ", "_").lower()
    exec(f"@shared_task\ndef {func_name}(): {type(task).__name__}().run_process()")


#@shared_task
#def tns_data_ingestion(interval_minutes=100):
#    TNSDataIngestion().run_process(interval_minutes=interval_minutes)


#@shared_task
#def initialize_transient_tasks():
#    """
#    Initializes all task in the database to not processed for new transients.
#    """

#    InitializeTransientTasks().run_process()


#@shared_task
#def snapshot_task_register():
#    SnapshotTaskRegister().run_process()


#@shared_task
#def ingest_missed_tns_transients():
#    IngestMissedTNSTransients().run_process()


#@shared_task
#def host_information():
#    """
#    Get infotmation on the host
#    """
#    HostInformation().run_process()


#@shared_task
#def transient_information():
#    """
#    Get infotmation on the transient
#    """
#    TransientInformation().run_process()


#@shared_task
#def global_aperture_photometry():
#    """ """
#    GlobalAperturePhotometry().run_process()


##@shared_task
#def global_aperture_construction():
 #   """ """

#    GlobalApertureConstructionRunner().run_process()


#@shared_task
#def local_aperture_photometry():
#    """ """
#    LocalAperturePhotometry().run_process()


#@shared_task
#def host_match():
#    """
#    Match a single transient in the database to a host galaxy.
#
#    Returns:
#        (None): Matches host to transient
#    """

#    GhostRunner().run_process()


#@shared_task
#def global_host_sed_inference():
#    """
#    Runs fits to global host aperture photometry
#    """
#    HostSEDFitting().run_process()


#@shared_task
#def cutout_download():
#    """
#    Downloads cutout data for a single transient
#    """
#    ImageDownloadRunner().run_process()


#@shared_task
#def delete_ghost_files():
#    DeleteGHOSTFiles().run_process()

