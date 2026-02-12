from django.db import models
from django.contrib.auth.models import User


class Hospital(models.Model):
    CATEGORY_CHOICES = [
        ("government", "Government"),
        ("private", "Private"),
        ("trust", "Trust"),
        ("clinic", "Clinic"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="hospital",
    )

    hospital_name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)

    contact_person = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)

    address = models.TextField()
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)

    licence_number = models.CharField(
        max_length=50,
        unique=True,
        help_text="Government issued hospital licence number",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["hospital_name"]

    def __str__(self):
        return self.hospital_name
