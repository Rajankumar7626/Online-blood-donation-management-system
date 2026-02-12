from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User

from donors.models import Donor
from hospitals.models import Hospital


# ==============================
# Login view
# ==============================
def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")

        if not email or not password:
            messages.error(request, "Email and password are required.")
            return render(request, "accounts/login.html")

        user = authenticate(request, username=email, password=password)

        if user:
            login(request, user)
            return redirect("dashboard")

        if User.objects.filter(username=email).exists():
            messages.error(request, "Incorrect password.")
        else:
            messages.error(request, "No account found with this email.")

    return render(request, "accounts/login.html")


# ==============================
# Logout view
# ==============================
@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect("login")


# ==============================
# Dashboard view
# ==============================
@login_required
def dashboard(request):
    user = request.user

    donor = Donor.objects.filter(user=user).first()
    if donor:
        return redirect("donors:donor-dashboard")

    hospital = Hospital.objects.filter(user=user).first()
    if hospital:
        return redirect("hospital:hospital-dashboard")

    if user.is_superuser:
        return render(request, "admin/dashboard.html", {"user_obj": user})

    return render(request, "home.html", {"user_obj": user})
