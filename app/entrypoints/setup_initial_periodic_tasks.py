from django_celery_beat.models import IntervalSchedule
from django_celery_beat.models import PeriodicTask
from host.tasks import periodic_tasks
from django.core.exceptions import ValidationError

for taskrunner in periodic_tasks:
    task = taskrunner.task_name

    interval, created = IntervalSchedule.objects.get_or_create(
        every=taskrunner.task_frequency_seconds, period=IntervalSchedule.SECONDS
    )

    search = PeriodicTask.objects.filter(
        name=taskrunner.task_name,
    )
    if not search:
        PeriodicTask.objects.create(
            interval=interval,
            name=taskrunner.task_name,
            task=taskrunner.task_function_name,
            enabled=taskrunner.task_initially_enabled,
        )
