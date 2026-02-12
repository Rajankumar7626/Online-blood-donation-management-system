from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


# ==================================================
# COMMON CHOICES
# ==================================================

BLOOD_GROUP_CHOICES = [
    ("A+", "A+"), ("A-", "A-"),
    ("B+", "B+"), ("B-", "B-"),
    ("O+", "O+"), ("O-", "O-"),
    ("AB+", "AB+"), ("AB-", "AB-"),
]

GENDER_CHOICES = [
    ("male", "Male"),
    ("female", "Female"),
    ("other", "Other"),
]

MARITAL_STATUS_CHOICES = [
    ("unmarried", "Unmarried"),
    ("married", "Married"),
]


# ==================================================
# DONOR
# ==================================================

class Donor(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="donor",
    )

    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50)

    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    marital_status = models.CharField(max_length=20, choices=MARITAL_STATUS_CHOICES)

    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUP_CHOICES)
    phone = models.CharField(max_length=15)
    aadhaar_last4 = models.CharField(max_length=4)

    address = models.TextField()
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    pincode = models.CharField(max_length=6)

    status = models.CharField(
        max_length=20,
        choices=[("active", "Active"), ("inactive", "Inactive")],
        default="active",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["first_name", "last_name"]
        indexes = [
            models.Index(fields=["blood_group"]),
            models.Index(fields=["city"]),
            models.Index(fields=["status"]),
        ]

    @property
    def full_name(self):
        return " ".join(filter(None, [
            self.first_name,
            self.middle_name,
            self.last_name,
        ]))

    def __str__(self):
        return f"{self.full_name} ({self.blood_group})"


# ==================================================
# DONOR DONATION
# ==================================================

class DonorDonation(models.Model):
    STATUS_CHOICES = [
        ("completed", "Completed"),
    ]

    donor = models.ForeignKey(
        Donor,
        on_delete=models.CASCADE,
        related_name="donations",
    )

    request = models.ForeignKey(
        "blood_requests.BloodRequest",
        on_delete=models.CASCADE,
        related_name="donations",
    )

    units_donated = models.PositiveIntegerField()
    donation_date = models.DateField(auto_now_add=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="completed",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["donor", "request"],
                name="unique_donor_request_donation",
            )
        ]

    def __str__(self):
        return f"{self.donor.full_name} → {self.units_donated} units"

    def clean(self):
        """
        HARD OBDMS RULES:
        - Donation only if RequestMatch exists AND accepted=True
        - Donor cannot donate to own request
        """

        from blood_requests.models import RequestMatch
        if self.request.requested_by_id == self.donor.user_id:
            raise ValidationError(
                "Donor cannot donate to their own blood request."
            )

        if not RequestMatch.objects.filter(
            donor=self.donor,
            request=self.request,
            accepted=True,
        ).exists():
            raise ValidationError(
                "Donation allowed only after donor has accepted the request."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


# ==================================================
# DONOR NOTIFICATIONS
# ==================================================

class DonorNotification(models.Model):
    donor = models.ForeignKey(
        Donor,
        on_delete=models.CASCADE,
        related_name="notifications",
    )

    title = models.CharField(max_length=200)
    message = models.TextField()

    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.donor.full_name} - {self.title}"
