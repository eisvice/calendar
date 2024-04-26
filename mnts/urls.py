from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("dates", views.get_dates, name="dates"),
    path("add-event", views.add_event, name="add_event"),
    path("add-theme", views.add_theme, name="add_theme"),
]