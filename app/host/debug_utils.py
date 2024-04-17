from host import tasks
from host.base_tasks import TransientTaskRunner
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


def get_failed_tasks(transient_name=None):

    if transient_name is None:
        failed_task_register = TaskRegister.objects.filter(status__message="failed")
    else:
        transient = Transient.objects.get(name=transient_name)
        failed_task_register = TaskRegister.objects.filter(
            transient=transient, status__message="failed"
        )

    return failed_task_register


def rerun_failed_task(task_register):

    task = task_register.task
    for ptask in tasks.periodic_tasks:
        if ptask.task_name == task.name:

            print(f"Running {task.name}")
            status = ptask._run_process(task_register.transient)
            print(f"Status: {status}")
    s = Status.objects.get(message=status)
    task_register.status = s
    task_register.save()
    return status


def set_tasks_unprocessed(transient_name):

    transient = Transient.objects.get(name=transient_name)
    all_tasks = TaskRegister.objects.filter(transient=transient)
    for t in all_tasks:
        s = Status.objects.get(message="not processed")
        t.status = s
        t.save()
