from django.db import transaction
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.exceptions import PermissionDenied

from .forms import DonorRegistrationForm
from .models import Donor, DonorDonation, DonorNotification
from blood_requests.models import BloodRequest, RequestMatch
from blood_requests import services


# ==================================================
# PUBLIC: DONORS LIST
# ==================================================
def donors_page(request):
    blood_group = request.GET.get("blood_group", "").strip()
    city = request.GET.get("city", "").strip()
    location = request.GET.get("location", "").strip()

    qs = Donor.objects.filter(status="active")

    if blood_group:
        qs = qs.filter(blood_group__iexact=blood_group)

    if city:
        qs = qs.filter(city__icontains=city)

    if location:
        qs = qs.filter(
            Q(city__icontains=location)
            | Q(state__icontains=location)
            | Q(address__icontains=location)
        )

    return render(request, "donor/list.html", {
        "donors": qs.order_by("first_name"),
        "blood_group": blood_group,
        "city": city,
        "location": location,
    })


# ==================================================
# REGISTER DONOR
# ==================================================
def register_donor(request):
    if request.method == "POST":
        form = DonorRegistrationForm(request.POST)
        password = request.POST.get("password")

        if form.is_valid():
            email = form.cleaned_data["email"]

            if User.objects.filter(username=email).exists():
                messages.error(request, "Email already registered.")
                return redirect("donors:register-donor")

            with transaction.atomic():
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=password,
                )

                donor = form.save(commit=False)
                donor.user = user
                donor.city = donor.city.strip().title()
                aadhaar = form.cleaned_data.get("aadhaar_number")
                if aadhaar:
                    donor.aadhaar_last4 = aadhaar[-4:]

                donor.save()

            messages.success(request, "Donor registered successfully.")
            return redirect("login")

        messages.error(request, "Please correct the errors below.")

    else:
        form = DonorRegistrationForm()

    return render(request, "donor/register.html", {
        "form": form,
    })
# ==================================================
# DONOR DASHBOARD
# ==================================================
@login_required
def donor_dashboard(request):
    donor = get_object_or_404(Donor, user=request.user)

    donations = DonorDonation.objects.filter(donor=donor)

    last_donation = (
        donations.filter(status="completed")
        .order_by("-created_at")
        .first()
    )

    return render(
        request,
        "donor/dashboard.html",
        {
            "donor": donor,
            "donations_count": donations.count(),
            "completed_donations": donations.filter(status="completed").count(),
            "last_donation": last_donation,
        },
    )



# ==================================================
# PROFILE
# ==================================================
@login_required
def donor_profile(request):
    donor = get_object_or_404(Donor, user=request.user)

    return render(request, "donor/profile.html", {
        "donor": donor,
    })


@login_required
def edit_donor_profile(request):
    donor = get_object_or_404(Donor, user=request.user)

    if request.method == "POST":
        form = DonorRegistrationForm(request.POST, instance=donor)
        if form.is_valid():
            donor = form.save(commit=False)
            donor.city = donor.city.strip().title()
            aadhaar = form.cleaned_data.get("aadhaar_number")
            if aadhaar:
                donor.aadhaar_last4 = aadhaar[-4:]
            donor.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("donors:donor-profile")
    else:
        form = DonorRegistrationForm(instance=donor)

    return render(request, "donor/edit_profile.html", {"form": form})


# ==================================================
# DONATIONS (STRICTLY READ-ONLY)
# ==================================================
@login_required
def donor_donations(request):
    donor = get_object_or_404(Donor, user=request.user)

    donations = DonorDonation.objects.filter(donor=donor).order_by("-donation_date")

    return render(request, "donor/donations.html", {
        "donations": donations,
        "total": donations.count(),
        "completed": donations.filter(status="completed").count(),
        "pending": donations.exclude(status="completed").count(),
    })



# ==================================================
# DONATION HISTORY (STRICTLY READ-ONLY)
# ==================================================

@login_required
def donation_detail(request, donation_id):
    donor = get_object_or_404(Donor, user=request.user)

    donation = get_object_or_404(
        DonorDonation,
        id=donation_id,
        donor=donor,
    )

    return render(
        request,
        "donor/donation_detail.html",
        {
            "donation": donation,
        },
    )


# ==================================================
# MATCHING REQUESTS (PENDING ONLY)
# ==================================================
@login_required
def donor_matching_requests(request):
    donor = get_object_or_404(Donor, user=request.user)

    matches = RequestMatch.objects.filter(
        donor=donor,
        accepted__isnull=True,
        request__status="open",
    ).select_related("request")

    return render(request, "donor/matching_requests.html", {
        "matches": matches,
    })


@login_required
def respond_to_request(request, match_id, action):
    try:
        match = RequestMatch.objects.select_related("request").get(
            id=match_id,
            donor__user=request.user,
            accepted__isnull=True,
            request__status="open",
        )
    except RequestMatch.DoesNotExist:
        messages.error(
            request,
            "This blood request is no longer available or already responded to."
        )
        return redirect("donors:donor-matching-requests")

    if action not in ("accept", "reject"):
        messages.error(request, "Invalid action.")
        return redirect("donors:donor-matching-requests")

    match.accepted = True if action == "accept" else False
    match.save(update_fields=["accepted"])

    if match.accepted:
        req = match.request
        if req.status == "open":
            req.status = "matched"
            req.save(update_fields=["status"])

        try:
            services.send_acceptance_email_to_requester(match)
        except Exception:
            pass

        DonorNotification.objects.create(
            donor=match.donor,
            title="Request Accepted",
            message="You have accepted a blood request. Please coordinate with the hospital.",
        )

    messages.success(request, "Your response has been recorded.")
    return redirect("donors:donor-matching-requests")

# ==================================================
# AVAILABILITY
# ==================================================
@login_required
def toggle_availability(request):
    donor = get_object_or_404(Donor, user=request.user)

    donor.status = "inactive" if donor.status == "active" else "active"
    donor.save(update_fields=["status"])

    messages.success(request, f"You are now marked as {donor.status.upper()}.")
    return redirect("donors:donor-dashboard")


# ==================================================
# NOTIFICATIONS
# ==================================================
@login_required
def donor_notifications(request):
    donor = get_object_or_404(Donor, user=request.user)

    notifications = donor.notifications.all()
    notifications.filter(is_read=False).update(is_read=True)

    return render(
        request,
        "donor/notifications.html",
        {"notifications": notifications},
    )
