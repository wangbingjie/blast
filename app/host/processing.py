# Modelus to manage to processing of tasks for transients
from django.utils import timezone
from models import Task, TaskProcessingStatus, Status


def update_status(task_status, updated_status):
    """
    Update the processing status of a task.

    Parameters:
        task_status (models.TaskProcessingStatus): task processing status to be
            updated.
        updated_status (models.Status): new status to update the task with.
    Returns:
        None: Saves the new updates to the backend.
    """
    task_status.status = updated_status
    task_status.last_modified = timezone.now()
    task_status.save()

def initialise_all_tasks_status(transient):
    """
    Set all available tasks for a transient to not processed.

    Parameters:
        transient (models.Transient): Transient to have all of its task status
            initialized.
    Returns:
        None: Saves the new updates to the backend.
    """
    tasks = Task.objects.all()
    not_processed = Status.objects.get(message__exact='not processed')

    for task in tasks:
        task_status = TaskProcessingStatus(task=task, transient=transient)
        update_status(task_status, not_processed)

def oldest_transient_with_task_status(task, status):
    """
    Get the transient with the oldest timestamp with task with a particular
    processing status.

    Parameters:
        task (models.Task): task of interest
        status (models.Status): status of the task of interest
    Returns:
        transient (models.Transient) or None.
    """
    task_processing = TaskProcessingStatus.obejcts.filter(task=task, status=status)

    if task_processing.exists():
        oldest_task = task_processing.order_by('transient__public_timestamp')[0]
        transient = oldest_task.transient
    else:
        transient = None

    return transient
