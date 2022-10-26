# users/urls.py

from django.conf.urls import include, url

urlpatterns = [
    url(r"^accounts/", include("django.contrib.auth.urls"))
    ]
