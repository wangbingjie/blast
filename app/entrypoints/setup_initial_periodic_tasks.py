from django_celery_beat.models import IntervalSchedule
from django_celery_beat.models import PeriodicTask
from host.tasks import periodic_tasks
from host.models import Task

for taskrunner in periodic_tasks:

    interval, created = IntervalSchedule.objects.get_or_create(
        every=taskrunner.task_frequency_seconds, period=IntervalSchedule.SECONDS
    )

    PeriodicTask.objects.create(
        interval=interval,
        name=taskrunner.task_name,
        task=taskrunner.task_function_name,
    )

    #if taskrunner.task_type == 'transient':
    #    Task.objects.create(name=taskrunner.task_name)

