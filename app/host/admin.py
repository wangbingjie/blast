from django.contrib import admin
from .models import Task
from .models import Status

# Register your models here.
admin.site.register(Task)
admin.site.register(Status)