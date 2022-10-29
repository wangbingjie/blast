# users/urls.py
from django.conf.urls import include
from django.conf.urls import url

urlpatterns = [url(r"^accounts/", include("django.contrib.auth.urls"))]
