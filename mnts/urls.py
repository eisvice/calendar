from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("dates", views.get_dates, name="dates")
]