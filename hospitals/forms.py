from django import forms
import re
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from .models import Hospital


class HospitalRegistrationForm(forms.ModelForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "Official Hospital Email",
        }),
    )

    class Meta:
        model = Hospital
        fields = [
            "email",
            "hospital_name",
            "category",
            "contact_person",
            "phone",
            "address",
            "state",
            "city",
            "licence_number",
        ]

        widgets = {
            "hospital_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter Hospital Name",
            }),
            "category": forms.Select(attrs={"class": "form-select"}),
            "contact_person": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter Contact Person Name",
            }),
            "phone": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter Contact Number",
            }),
            "address": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
            }),
            "state": forms.TextInput(attrs={"class": "form-control"}),
            "city": forms.TextInput(attrs={"class": "form-control"}),
            "licence_number": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Hospital Licence Number",
            }),
        }


    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip()
        try:
            validate_email(email)
        except ValidationError:
            raise forms.ValidationError("Enter a valid email address.")
        return email

    def clean_contact_person(self):
        name = (self.cleaned_data.get("contact_person") or "").strip()
        if not re.match(r"^[A-Za-z ]+$", name):
            raise forms.ValidationError(
                "Contact person name must contain only letters."
            )
        return name

    def clean_phone(self):
        phone = (self.cleaned_data.get("phone") or "").strip()
        if not phone.isdigit():
            raise forms.ValidationError("Phone number must contain digits only.")
        if len(phone) < 10:
            raise forms.ValidationError("Enter a valid phone number.")
        return phone

    def clean_licence_number(self):
        licence = (self.cleaned_data.get("licence_number") or "").strip()
        if len(licence) < 5:
            raise forms.ValidationError("Invalid licence number.")
        return licence


# ==================================================
# HOSPITAL PROFILE UPDATE   
# ==================================================

class HospitalProfileForm(forms.ModelForm):

    class Meta:
        model = Hospital
        fields = [
            "hospital_name",
            "contact_person",
            "phone",
            "category",
            "state",
            "city",
            "address",
        ]

        widgets = {
            "hospital_name": forms.TextInput(attrs={"class": "form-control"}),
            "contact_person": forms.TextInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "state": forms.TextInput(attrs={"class": "form-control"}),
            "city": forms.TextInput(attrs={"class": "form-control"}),
            "address": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
            }),
        }

    def clean_contact_person(self):
        name = (self.cleaned_data.get("contact_person") or "").strip()
        if not re.match(r"^[A-Za-z ]+$", name):
            raise forms.ValidationError(
                "Contact person name must contain only letters."
            )
        return name

    def clean_phone(self):
        phone = (self.cleaned_data.get("phone") or "").strip()
        if not phone.isdigit():
            raise forms.ValidationError("Phone number must contain digits only.")
        if len(phone) < 10:
            raise forms.ValidationError("Enter a valid phone number.")
        return phone
