# Modelus to manage to processing of tasks for transients
from abc import ABC
from abc import abstractmethod

from django.db.models import Q
from django.utils import timezone

from .ghost import run_ghost
from .models import Status
from .models import Task
from .models import TaskRegister
from .models import Transient


class TaskRunner(ABC):
    def __init__(self):
        self.processing_status = Status.objects.get(message__exact="processing")
        self.task_register = TaskRegister.objects.all()
        self.failed_status = Status.objects.get(
            message__exact=self._failed_status_message()
        )
        self.prerequisites = self._prerequisites()
        self.task = Task.objects.get(name__exact=self._task_name())

    def find_register_items_meeting_prerequisites(self):

        current_transients = Transient.objects.all()

        for task_name, status_message in self.prerequisites.items():
            task = Task.objects.get(name__exact=task_name)
            status = Status.objects.get(message__exact=status_message)

            current_transients = current_transients & \
                                 Transient.objects.filter(taskregister__task=task,
                                         taskregister__status=status)

        return self.task_register.filter(transient__in=list(current_transients), task=self.task)


    def _select_highest_priority(self, register):
        return register.order_by("transient__public_timestamp")[0]

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

    @abstractmethod
    def _task_name(self):
        pass

    @abstractmethod
    def _failed_status_message(self):
        pass


class GhostRunner(TaskRunner):
    def _prerequisites(self):
        return {"Host Match": "not processed"}

    def _task_name(self):
        return "Cutout download"

    def _failed_status_message(self):
        return "no GHOST match"

    def _run_process(self, transient):
        host = run_ghost(transient)

        if host is not None:
            host.save()
            transient.host = host
            transient.save()
            status = Status.objects.get(message__exact="processed")
        else:
            status = Status.objects.get(message__exact="no ghost match")

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
    not_processed = Status.objects.get(message__exact="not processed")

    for task in tasks:
        task_status = TaskRegister(task=task, transient=transient)
        update_status(task_status, not_processed)
