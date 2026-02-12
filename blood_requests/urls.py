from django.urls import path
from . import views

app_name = "requests"

urlpatterns = [

    # =========================
    # Blood request (User / Hospital)
    # =========================

    path(
        "create/",
        views.create_blood_request,
        name="create-request",
    ),

    path(
        "my/",
        views.my_requests,
        name="my-requests",
    ),

    path(
        "<int:request_id>/cancel/",
        views.cancel_blood_request,
        name="cancel-request",
    ),

    # =========================
    # Hospital-only actions
    # =========================

    path(
        "hospital/",
        views.hospital_requests,
        name="hospital-requests",
    ),

    path(
        "hospital/<int:request_id>/fulfilled/",
        views.mark_request_fulfilled,
        name="mark-fulfilled",
    ),
    
    path(
    "hospital/<int:request_id>/fulfilled/",
    views.mark_request_fulfilled,
    name="mark-fulfilled",
),

]
