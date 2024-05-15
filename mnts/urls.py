from django.urls import path, include
from .views import UserRegisterView, ChangePasswordView, ResetPasswordView
from . import views

urlpatterns = [
    path("", include("django.contrib.auth.urls")), # Login view
    path("logout", views.logout_view, name="logout"),
    path("register/", UserRegisterView.as_view(), name="register"),
    path("change-password/", ChangePasswordView.as_view(), name="change_password"),
    path("reset-password/", ResetPasswordView.as_view(), name="reset_password"),
    path("", views.index, name="index"), # Index view
    path("dates", views.get_dates, name="dates"),
    path("add-event", views.add_event, name="add_event"),
    path("edit-event", views.edit_event, name="edit_event"),
    path("add-theme", views.add_theme, name="add_theme"),
    path("theme/<int:id>", views.edit_theme, name="theme")
]