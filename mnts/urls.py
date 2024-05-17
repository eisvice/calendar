from django.urls import path, include
from .views import UserRegisterView, ChangePasswordView, ResetPasswordView
from . import views

urlpatterns = [
    # account manager
    path("", include("django.contrib.auth.urls")), # login, logout views
    path("register/", UserRegisterView.as_view(), name="register"),
    path("change-password/", ChangePasswordView.as_view(), name="change_password"),
    path("reset-password/", ResetPasswordView.as_view(), name="reset_password"),
    # site's endpoints
    path("", views.index, name="index"), # index view
    path("dates", views.get_dates, name="dates"),
    path("add-event", views.add_event, name="add_event"),
    path("event-group/<int:id>", views.event_group, name="event_group"),
    path("edit-event", views.edit_event, name="edit_event"),
    path("add-theme", views.add_theme, name="add_theme"),
    path("theme/<int:id>", views.edit_theme, name="theme")
]