from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from hospitals.models import Hospital
from donors.models import BLOOD_GROUP_CHOICES, Donor


# =========================
# BLOOD REQUEST
# =========================
class BloodRequest(models.Model):
    STATUS_CHOICES = [
        ("open", "Open"),
        ("matched", "Matched"),
        ("fulfilled", "Fulfilled"),
        ("cancelled", "Cancelled"),
    ]

    requested_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="blood_requests",
    )

    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="blood_requests",
    )

    blood_group = models.CharField(
        max_length=5,
        choices=BLOOD_GROUP_CHOICES,
    )

    units_required = models.PositiveIntegerField()
    city = models.CharField(max_length=100)
    contact_info = models.CharField(max_length=200)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="open",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.blood_group} ({self.units_required}) - {self.city}"

    def clean(self):
        """
        HARD RULES:
        - Cancelled / fulfilled requests are immutable
        """
        if self.pk:
            old = BloodRequest.objects.get(pk=self.pk)
            if old.status in ("cancelled", "fulfilled") and old.status != self.status:
                raise ValidationError(
                    "Cancelled or fulfilled requests cannot be modified."
                )


# =========================
# REQUEST ↔ DONOR MATCH
# =========================
class RequestMatch(models.Model):
    request = models.ForeignKey(
        BloodRequest,
        on_delete=models.CASCADE,
        related_name="matches",
    )

    donor = models.ForeignKey(
        Donor,
        on_delete=models.CASCADE,
        related_name="matches",
    )
    notified = models.BooleanField(default=False)

    accepted = models.BooleanField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["request", "donor"],
                name="unique_request_donor_match",
            )
        ]

    def clean(self):
        """
        HARD RULES:
        - Donor cannot be matched to own request
        - Cannot accept/reject non-open requests
        """
        if (
            self.request
            and self.donor
            and self.request.requested_by_id == self.donor.user_id
        ):
            raise ValidationError(
                "Requester cannot be matched as a donor for their own blood request."
            )

        if self.accepted is not None and self.request.status != "open":
            raise ValidationError(
                "Cannot respond to a request that is not open."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.donor.full_name} → {self.request.blood_group}"
