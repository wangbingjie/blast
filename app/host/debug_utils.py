from host import tasks
from host.models import *
from host.transient_tasks import *


def _overwrite_or_create_object(model, unique_object_query, object_data):
    """
    Overwrites or creates new objects in the blast database.

    Parameters
        model (dango.model): blast model of the object that needs to be updated
        unique_object_query (dict): query to be passed to model.objects.get that will
            uniquely identify the object of interest
        object_data (dict): data to be saved or overwritten for the object.
    """

    try:
        object = model.objects.get(**unique_object_query)
        object.delete()
        model.objects.create(**object_data)
    except model.DoesNotExist:
        model.objects.create(**object_data)


def get_failed_tasks(transient_name):

    transient = Transient.objects.get(name=transient_name)
    failed_task_register = TaskRegister.objects.filter(
        transient=transient, status__message="failed"
    )

    return failed_task_register


def rerun_failed_task(task_register):

    task = task_register.task
    for ptask in periodic_task:
        if ptask.task_name == task.name:
            ptask._run_process(task_register.transient)
