# Modelus to manage to processing of tasks for transients
from django.utils import timezone
from .models import Task, TaskRegister, Status
from abc import ABC, abstractmethod
from .ghost import run_ghost

class TaskRunner(ABC):

    def __init__(self, failed_status):
        self.processing_status = Status.objects.get(message__exact='processing')
        self.task_register = TaskRegister.objects.all()
        self.failed_status = failed_status
        self.prerequsits = self._prerequisites()

    def find_register_items_meeting_prerequisites(self):

        current_register = self.task_register

        for task_name, status_message in self.prerequsits.items():
            task = Task.objects.get(name__exact=task_name)
            status = Status.objects.get(message__exact=status_message)
            current_register = current_register.filter(task=task, status=status)

        return current_register

    def _select_highest_priority(self, register):
        return register.order_by('transient__public_timestamp')[0]

    def select_register_item(self):
        register = self.find_register_items_meeting_prerequisites()
        return self._select_highest_priority(register) if register.exists() else None


    def run_process(self):
        task_register_item = self.select_register_item()

        if task_register_item is not None:
            update_status(task_register_item, self.processing_status)
            transient = task_register_item.transient

            try:
                status = self._run_process(transient)
                update_status(task_register_item, status)
            except:
                update_status(task_register_item, self.failed_status)

    @abstractmethod
    def _run_process(self, transient):
        pass

    @abstractmethod
    def _prerequisites(self):
        pass

class GhostRunner(TaskRunner):

    def __init__(self):
        super(GhostRunner, self).__init__(
            Status.objects.get(message__exact='no GHOST match'))

    def _prerequisites(self):
        return {'Host Match': 'not processed'}

    def _run_process(self, transient):
        host = run_ghost(transient)

        if host is not None:
            host.save()
            transient.host = host
            transient.save()
            status = Status.objects.get(message__exact='processed')
        else:
            status = Status.objects.get(message__exact='no ghost match')

        return status

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
        task_status = TaskRegister(task=task, transient=transient)
        update_status(task_status, not_processed)
