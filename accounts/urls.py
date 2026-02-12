from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from .views import login_view, logout_view, dashboard

urlpatterns = [
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("dashboard/", dashboard, name="dashboard"),

    # Password change
    path(
        "change-password/",
        auth_views.PasswordChangeView.as_view(
            template_name="accounts/change_password.html",
            success_url=reverse_lazy("change-password-done"),
        ),
        name="change-password",
    ),
    path(
        "change-password/done/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="accounts/change_password_done.html",
        ),
        name="change-password-done",
    ),
]
