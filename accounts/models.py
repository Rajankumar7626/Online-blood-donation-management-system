from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User


class UserRole(models.Model):
    ROLE_CHOICES = (
        ("donor", "Donor"),
        ("hospital", "Hospital"),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="role"
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES
    )

    def __str__(self):
        return f"{self.user.username} - {self.role}"
