import os

from django.urls import path

from . import serializers
from . import views

base_path = os.environ.get("BASE_PATH", "").strip("/")
if base_path != "":
    base_path = f"""{base_path}/"""

urlpatterns = [path(f"""{base_path}transient/<slug:slug>""", views.transient_data)]
