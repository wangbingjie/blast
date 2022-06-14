from django.urls import path

from . import views


urlpatterns = [
    path("transients/", views.transient_list),
    path("analytics/", views.analytics),
    path("transients/<slug:slug>/", views.results),
    path("acknowledgements/", views.acknowledgements),
]
