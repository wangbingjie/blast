from django.urls import path
from . import views


urlpatterns = [
    path('', views.submit_transient),
    path('transients/', views.transient_list),
    path('analytics/', views.analytics)
]