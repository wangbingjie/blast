import os

from django.urls import path

from . import views

base_path = os.environ.get("BASE_PATH", "").strip("/")
if base_path != "":
    base_path = f"""{base_path}/"""

urlpatterns = [
    path(
        f"""{base_path}transient/get/<str:transient_name>""",
        views.get_transient_science_payload,
    ),
    path(
        f"""{base_path}upload/transient/""",
        views.upload_transient_data,
    ),
    path(
        f"""{base_path}upload/cutout/transient_name=<str:transient_name>&cutout_filter=<str:cutout_filter_name>""",
        views.upload_cutout_data,
    ),
    path(
        f"""{base_path}upload/posterior/transient_name=<str:transient_name>&aperture_type=<str:aperture_type>""",
        views.upload_posterior_data,
    ),
]

if os.environ.get("ALLOW_API_POST") == "YES":
    urlpatterns.append(
        path(
            f"""{base_path}transient/post/name=<str:transient_name>&ra=<str:transient_ra>&dec=<str:transient_dec>""",
            views.post_transient,
        )
    )
