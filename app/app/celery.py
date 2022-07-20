from __future__ import absolute_import
from __future__ import unicode_literals

import os

from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")

app = Celery("app")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps.
app.autodiscover_tasks(settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")

"""
@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    for taskrunner in periodic_tasks:
        interval, created = IntervalSchedule.objects.get_or_create(
            every=taskrunner.task_frequency_seconds,
            period=IntervalSchedule.SECONDS)


        PeriodicTask.objects.create(interval=interval,
                                    name=taskrunner._task_name(),
                                    task=taskrunner.task_function_name)

    sender.add_periodic_task(taskrunner.task_frequency_seconds, test.s('test'), name='add every 10')
    sender.add_periodic_task(10.0, )
    sender.add_periodic_task(30.0, test.s(), expires=10)
"""