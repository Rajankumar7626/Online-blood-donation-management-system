from django.urls import path
from . import views

app_name = "hospital"

urlpatterns = [
    path("", views.hospitals_page, name="hospitals-page"),
    path("register/", views.register_hospital, name="register-hospital"),
    path("dashboard/", views.hospital_dashboard, name="hospital-dashboard"),
    path("profile/", views.hospital_profile, name="hospital-profile"),
    path("requests/", views.hospital_dashboard, name="hospital-requests"),
    path("requests/create/", views.create_blood_request, name="create-blood-request"),
    path(
        "requests/<int:request_id>/cancel/",
        views.cancel_blood_request,
        name="cancel-blood-request",
    ),
]
