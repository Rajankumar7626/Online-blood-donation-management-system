from django import forms
from datetime import date
import re
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from .models import Donor


class DonorRegistrationForm(forms.ModelForm):

    # =========================
    # EMAIL (User account)
    # =========================
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "Email Address",
        }),
    )

    # =========================
    # Aadhaar Number (store only last 4 digits)
    # =========================
    aadhaar_number = forms.CharField(
        max_length=12,
        min_length=12,
        required=True,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "12-digit Aadhaar Number",
        }),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["aadhaar_number"].required = False

    # =========================
    # META
    # =========================
    class Meta:
        model = Donor
        fields = [
            "email",
            "first_name",
            "middle_name",
            "last_name",
            "date_of_birth",
            "gender",
            "marital_status",
            "blood_group",
            "phone",
            "address",
            "state",
            "city",
            "pincode",
        ]

        widgets = {
            "first_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "First Name",
            }),
            "middle_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Middle Name (optional)",
            }),
            "last_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Last Name",
            }),
            "date_of_birth": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
            }),
            "gender": forms.Select(attrs={"class": "form-select"}),
            "marital_status": forms.Select(attrs={"class": "form-select"}),
            "blood_group": forms.Select(attrs={"class": "form-select"}),
            "phone": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Phone Number",
            }),
            "address": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Full Address",
            }),
            "state": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "State",
            }),
            "city": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "City",
            }),
            "pincode": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Pincode",
            }),
        }

    # =========================
    # VALIDATIONS
    # =========================

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip()

        try:
            validate_email(email)
        except ValidationError:
            raise forms.ValidationError("Enter a valid email address.")

        return email

    def clean_first_name(self):
        name = (self.cleaned_data.get("first_name") or "").strip()

        if not re.match(r"^[A-Za-z ]+$", name):
            raise forms.ValidationError(
                "First name must contain only letters."
            )
        return name

    def clean_last_name(self):
        name = (self.cleaned_data.get("last_name") or "").strip()

        if not re.match(r"^[A-Za-z ]+$", name):
            raise forms.ValidationError(
                "Last name must contain only letters."
            )
        return name

    def clean_phone(self):
        phone = (self.cleaned_data.get("phone") or "").strip()

        if not phone.isdigit():
            raise forms.ValidationError("Phone number must contain digits only.")

        if len(phone) < 10:
            raise forms.ValidationError("Enter a valid phone number.")

        return phone

    def clean_date_of_birth(self):
        dob = self.cleaned_data.get("date_of_birth")

        if not dob:
            return dob

        today = date.today()
        age = today.year - dob.year - (
            (today.month, today.day) < (dob.month, dob.day)
        )

        if age < 18:
            raise forms.ValidationError("Donor must be at least 18 years old.")

        return dob

    def clean_aadhaar_number(self):
        aadhaar = (self.cleaned_data.get("aadhaar_number") or "").strip()

        if not aadhaar:
            return ""

        if not aadhaar.isdigit():
            raise forms.ValidationError("Aadhaar must contain digits only.")

        if len(aadhaar) != 12:
            raise forms.ValidationError("Aadhaar must be exactly 12 digits.")

        return aadhaar
