from django.urls import path
from . import views

app_name = "donors"

urlpatterns = [
    path("register/", views.register_donor, name="register-donor"),
    path("list/", views.donors_page, name="donors-page"),


    path("dashboard/", views.donor_dashboard, name="donor-dashboard"),
    path("profile/", views.donor_profile, name="donor-profile"),
    path("profile/edit/", views.edit_donor_profile, name="donor-profile-edit"),
    path("donations/", views.donor_donations, name="donor-donations"),
    path(
    "donations/<int:donation_id>/",
    views.donation_detail,
    name="donation-detail",
      ), 
    path(
        "requests/",
        views.donor_matching_requests,
        name="donor-matching-requests",
    ),
    path(
        "requests/<int:match_id>/<str:action>/",
        views.respond_to_request,
        name="respond-request",
    ),
    path(
        "availability/toggle/",
        views.toggle_availability,
        name="toggle-availability",
    ),
    path(
        "notifications/",
        views.donor_notifications,
        name="donor-notifications",
    ),
]
