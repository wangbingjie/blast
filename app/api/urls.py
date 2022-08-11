import os

from django.urls import path

from . import views

base_path = os.environ.get("BASE_PATH", "").strip("/")
if base_path != "":
    base_path = f"""{base_path}/"""

urlpatterns = [
    path(f"""{base_path}<slug:slug>""", views.api_info)
]