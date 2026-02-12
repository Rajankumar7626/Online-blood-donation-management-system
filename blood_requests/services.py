from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.db import IntegrityError
import logging
from donors.models import Donor
from .models import RequestMatch
from django.db.models.functions import Upper, Trim

logger = logging.getLogger(__name__)




BLOOD_COMPATIBILITY = {
    "O-": ["O-"],
    "O+": ["O-", "O+"],
    "A-": ["O-", "A-"],
    "A+": ["O-", "O+", "A-", "A+"],
    "B-": ["O-", "B-"],
    "B+": ["O-", "O+", "B-", "B+"],
    "AB-": ["O-", "A-", "B-", "AB-"],
    "AB+": ["O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"],
}



# ==================================================
# MATCH DONORS & NOTIFY
# ==================================================
def match_and_notify(blood_request, request=None):
    """
    Match donors by blood_group + city,
    create RequestMatch rows,
    and notify donors via email.

    HARD RULES:
    - Only ACTIVE donors
    - No self-matching
    - No duplicate matches
    """
    request_bg = (blood_request.blood_group or "").strip().upper()
    request_city_title = (blood_request.city or "").strip().title()

    compatible = BLOOD_COMPATIBILITY.get(request_bg, [])
    compatible = [bg.strip().upper() for bg in compatible]
    donors = Donor.objects.annotate(
        norm_bg=Upper(Trim("blood_group")),
        norm_city=Trim("city"),
    ).filter(
        norm_bg__in=compatible,
        norm_city__iexact=request_city_title,
        status="active",
    )

    for donor in donors:
        if donor.user_id == blood_request.requested_by_id:
            continue

        try:
            match, created = RequestMatch.objects.get_or_create(
                request=blood_request,
                donor=donor,
            )
        except IntegrityError:
            continue

        if not created:
            continue

        accept_path = reverse(
            "donors:respond-request",
            args=[match.id, "accept"],
        )
        reject_path = reverse(
            "donors:respond-request",
            args=[match.id, "reject"],
        )

        if request:
            accept_link = request.build_absolute_uri(accept_path)
            reject_link = request.build_absolute_uri(reject_path)
        else:
            accept_link = accept_path
            reject_link = reject_path

        subject = f"Blood request matching your blood group ({blood_request.blood_group})"
        message = (
            f"Blood Group: {blood_request.blood_group}\n"
            f"City: {blood_request.city}\n"
            f"Units Required: {blood_request.units_required}\n\n"
            f"Accept: {accept_link}\n"
            f"Reject: {reject_link}\n"
        )

        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [donor.user.email],
                fail_silently=False,
            )
        except Exception:
            logger.exception(
                "Email failed for donor %s (request %s)",
                donor.user.email,
                blood_request.id,
            )


# ==================================================
# DONOR ACCEPTANCE NOTIFICATION
# ==================================================
def send_acceptance_email_to_requester(match):
    """
    Sent when donor ACCEPTS request.
    Contact details are shared ONLY here.
    """

    req = match.request

    recipient = None
    if req.hospital:
        recipient = req.hospital.user.email
    else:
        recipient = req.requested_by.email

    if not recipient:
        return

    subject = f"Donor accepted your blood request ({req.blood_group})"
    message = (
        f"Donor Name: {match.donor.full_name}\n"
        f"Donor Phone: {match.donor.phone}\n"
        f"Donor Email: {match.donor.user.email}\n\n"
        f"Blood Group: {req.blood_group}\n"
        f"City: {req.city}\n"
        f"Units Required: {req.units_required}\n"
    )

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient],
            fail_silently=False,
        )
    except Exception:
        logger.exception(
            "Acceptance email failed for request %s",
            match.id,
        )


# ==================================================
# REQUEST CANCELLED
# ==================================================
def notify_cancelled_request(blood_request):
    """
    Notify ONLY donors who ACCEPTED the request.
    """

    matches = RequestMatch.objects.filter(
        request=blood_request,
        accepted=True,
    )

    for match in matches:
        try:
            send_mail(
                f"Blood Request Cancelled ({blood_request.blood_group})",
                f"The blood request in {blood_request.city} has been cancelled.",
                settings.DEFAULT_FROM_EMAIL,
                [match.donor.user.email],
                fail_silently=False,
            )
        except Exception:
            logger.exception(
                "Cancel email failed for donor %s",
                match.donor.user.email,
            )


# ==================================================
# REQUEST FULFILLED
# ==================================================
def notify_fulfilled_request(blood_request):
    """
    Notify ONLY donors who ACCEPTED the request.
    """

    matches = RequestMatch.objects.filter(
        request=blood_request,
        accepted=True,
    )

    for match in matches:
        try:
            send_mail(
                f"Blood Request Fulfilled ({blood_request.blood_group})",
                "Thank you for helping. The request has been fulfilled.",
                settings.DEFAULT_FROM_EMAIL,
                [match.donor.user.email],
                fail_silently=False,
            )
        except Exception:
            logger.exception(
                "Fulfilled email failed for donor %s",
                match.donor.user.email,
            )
