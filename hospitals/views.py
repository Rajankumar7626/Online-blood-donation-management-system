from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.contrib.auth.models import User

from .models import Hospital
from .forms import HospitalProfileForm, HospitalRegistrationForm
from blood_requests.models import BloodRequest


# ==================================================
# HOSPITAL DASHBOARD
# ==================================================
@login_required
def hospital_dashboard(request):
    hospital = get_object_or_404(Hospital, user=request.user)

    requests_qs = BloodRequest.objects.filter(hospital=hospital)

    stats = {
        "total": requests_qs.count(),
        "open": requests_qs.filter(status="open").count(),
        "matched": requests_qs.filter(status="matched").count(),
        "fulfilled": requests_qs.filter(status="fulfilled").count(),
        "cancelled": requests_qs.filter(status="cancelled").count(),
    }

    return render(request, "hospital/dashboard.html", {
        "hospital": hospital,
        "stats": stats,
        "requests": requests_qs.order_by("-created_at"),
    })


# ==================================================
# HOSPITAL PROFILE
# ==================================================
@login_required
def hospital_profile(request):
    hospital = get_object_or_404(Hospital, user=request.user)

    if request.method == "POST":
        form = HospitalProfileForm(request.POST, instance=hospital)
        if form.is_valid():
            form.save()
            messages.success(request, "Hospital profile updated successfully.")
            return redirect("hospital:hospital-profile")
        messages.error(request, "Please correct the errors below.")
    else:
        form = HospitalProfileForm(instance=hospital)

    return render(request, "hospital/profile.html", {
        "form": form,
        "hospital": hospital,
    })


# ==================================================
# HOSPITAL REGISTRATION
# ==================================================
def register_hospital(request):
    if request.method == "POST":
        form = HospitalRegistrationForm(request.POST)
        password = request.POST.get("password")

        if form.is_valid():
            email = form.cleaned_data["email"]
            if User.objects.filter(username=email).exists():
                messages.error(request, "Email already registered.")
                return redirect("hospital:register-hospital")

            with transaction.atomic():
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=password,
                )
                hospital = form.save(commit=False)
                hospital.user = user
                hospital.save()

            messages.success(request, "Hospital registered successfully.")
            return redirect("login")
        messages.error(request, "Please correct the errors below.")

    else:
        form = HospitalRegistrationForm()

    return render(request, "hospital/hospital_registration.html", {
        "form": form,
    })

# ==================================================
# PUBLIC: HOSPITAL LIST
# ==================================================
def hospitals_page(request):
    location = request.GET.get("location", "").strip()

    qs = Hospital.objects.all()

    if location:
        qs = qs.filter(
            Q(city__icontains=location)
            | Q(state__icontains=location)
            | Q(address__icontains=location)
        )

    return render(request, "hospital/list.html", {
        "hospitals": qs.order_by("hospital_name"),
        "location": location,
    })


# ==================================================
# CREATE BLOOD REQUEST (HOSPITAL ONLY)
# ==================================================
@login_required
def create_blood_request(request):
    hospital = get_object_or_404(Hospital, user=request.user)

    if request.method == "POST":
        blood_group = request.POST.get("blood_group")
        units = request.POST.get("units_required")

        if not blood_group or not units:
            messages.error(request, "All fields are required.")
            return redirect("hospital:create-blood-request")

        BloodRequest.objects.create(
            requested_by=request.user,
            hospital=hospital,
            blood_group=blood_group,
            units_required=units,
            city=hospital.city,
            contact_info=hospital.phone,
            status="open",
        )

        messages.success(request, "Blood request created successfully.")
        return redirect("hospital:hospital-dashboard")

    return render(request, "requests/create.html")


# ==================================================
# CANCEL BLOOD REQUEST (HOSPITAL – OWNER ONLY)
# ==================================================
@login_required
def cancel_blood_request(request, request_id):
    hospital = get_object_or_404(Hospital, user=request.user)

    blood_request = get_object_or_404(
        BloodRequest,
        id=request_id,
        hospital=hospital,
        status="open",
    )

    blood_request.status = "cancelled"
    blood_request.save(update_fields=["status"])

    messages.success(request, "Blood request cancelled successfully.")
    return redirect("hospital:hospital-dashboard")
