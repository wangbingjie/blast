import os

from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from . import serializers
from . import views

base_path = os.environ.get("BASE_PATH", "").strip("/")
if base_path != "":
    base_path = f"""{base_path}/"""

urlpatterns = [
    path(
        f"""{base_path}transient/<str:slug>/""", views.TransientSciencePayload.as_view()
    )
]
urlpatterns = format_suffix_patterns(urlpatterns)
