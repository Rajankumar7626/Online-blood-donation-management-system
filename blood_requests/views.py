from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.core.exceptions import PermissionDenied

from hospitals.models import Hospital
from donors.models import Donor, BLOOD_GROUP_CHOICES, DonorDonation, DonorNotification
from .models import BloodRequest, RequestMatch
from . import services


# ==================================================
# CREATE BLOOD REQUEST (User or Hospital)
# ==================================================
@login_required
def create_blood_request(request):
    hospital = getattr(request.user, "hospital", None)

    if request.method == "POST":
        blood_group = request.POST.get("blood_group")
        units = request.POST.get("units_required")
        city = request.POST.get("city", "").strip().title()

        if not blood_group or not units or not city:
            messages.error(request, "All fields are required.")
            return redirect("requests:create-request")

        if hospital:
            contact_info = hospital.phone
        else:
            contact_info = request.user.email

        blood_request = BloodRequest.objects.create(
            requested_by=request.user,
            hospital=hospital,
            blood_group=blood_group,
            units_required=units,
            city=city,
            contact_info=contact_info,
            status="open",
        )

        # Auto-match donors
        try:
            services.match_and_notify(blood_request, request=request)
        except Exception:
            pass

        messages.success(request, "Blood request created successfully.")

        if hospital:
            return redirect("hospital:hospital-dashboard")
        return redirect("requests:my-requests")

    return render(request, "requests/create.html", {
        "blood_groups": BLOOD_GROUP_CHOICES,
    })



# ==================================================
# MY REQUESTS (Requester: User or Hospital)
# ==================================================
@login_required
def my_requests(request):
    requests_qs = BloodRequest.objects.filter(requested_by=request.user)

    return render(request, "requests/my_requests.html", {
        "requests": requests_qs,
        "hospital":None,
    })


# ==================================================
# CANCEL BLOOD REQUEST (OWNER ONLY)
# ==================================================
@login_required
def cancel_blood_request(request, request_id):
    blood_request = get_object_or_404(
        BloodRequest,
        id=request_id,
        requested_by=request.user,
        status="open",
    )

    blood_request.status = "cancelled"
    blood_request.save(update_fields=["status"])

    try:
        services.notify_cancelled_request(blood_request)
    except Exception:
        pass

    messages.success(request, "Blood request cancelled successfully.")
    return redirect("requests:my-requests")


# ==================================================
# HOSPITAL: VIEW OWN REQUESTS
# ==================================================
@login_required
def hospital_requests(request):
    hospital = getattr(request.user, "hospital", None)
    if not hospital:
        raise PermissionDenied("Hospital access only.")

    requests_qs = BloodRequest.objects.filter(hospital=hospital)

    return render(request, "requests/my_requests.html", {
        "requests": requests_qs,
        "hospital": hospital,
    })


# ==================================================
# MARK REQUEST AS FULFILLED 
# ==================================================
@login_required
def mark_request_fulfilled(request, request_id):
    hospital = Hospital.objects.filter(user=request.user).first()

    blood_request = get_object_or_404(
        BloodRequest,
        id=request_id,
        status="matched",
    )


    if not (
        (hospital and blood_request.hospital_id == hospital.id)
        or blood_request.requested_by_id == request.user.id
    ):
        messages.error(request, "You are not allowed to fulfill this request.")
        return redirect("dashboard")

    accepted_match = RequestMatch.objects.filter(
        request=blood_request,
        accepted=True,
    ).select_related("donor").first()

    if not accepted_match:
        messages.error(request, "No accepted donor found.")
        return redirect("dashboard")

    with transaction.atomic():
        blood_request.status = "fulfilled"
        blood_request.save(update_fields=["status"])

        DonorDonation.objects.get_or_create(
            donor=accepted_match.donor,
            request=blood_request,
            defaults={
                "units_donated": blood_request.units_required,
                "status": "completed",
            },
        )

        DonorNotification.objects.create(
            donor=accepted_match.donor,
            title="Blood Request Fulfilled",
            message="Thank you for donating blood. The requester has marked the request as fulfilled.",
        )

        try:
            services.notify_fulfilled_request(blood_request)
        except Exception:
            pass

    messages.success(request, "Blood request marked as fulfilled.")
    return redirect("dashboard")
