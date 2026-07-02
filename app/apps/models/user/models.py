from django.contrib.auth.models import AbstractUser
from django.db import models
from model_utils.models import TimeStampedModel, UUIDModel


class User(AbstractUser, UUIDModel, TimeStampedModel):
    last_name = None

    MALE = "M"
    FEMALE = "F"
    OTHER = "O"
    GENDER = [
        (MALE, "Masculino"),
        (FEMALE, "Femenino"),
        (OTHER, "Otro"),
    ]

    first_name = models.CharField(
        max_length=100,
        blank=False,
        null=False,
        verbose_name="First name",
        help_text="User's first name(s).",
    )

    paternal_last_name = models.CharField(
        max_length=100,
        blank=False,
        null=False,
        verbose_name="Paternal last name",
        help_text="User's paternal last name.",
    )

    maternal_last_name = models.CharField(
        max_length=100,
        blank=False,
        null=False,
        verbose_name="Maternal last name",
        help_text="User's maternal last name.",
    )

    accepted_terms = models.BooleanField(
        default=False,
        verbose_name="Accepted terms and conditions",
        help_text="Indicates whether the user accepted the terms and conditions.",
    )

    gender = models.CharField(
        max_length=1,
        choices=GENDER,
        default=OTHER,
        help_text="User gender.",
        verbose_name="Gender",
    )

    phone = models.CharField(
        max_length=9,
        blank=True,
        verbose_name="Phone",
    )

    address = models.CharField(
        max_length=60,
        blank=True,
        help_text="User address.",
        verbose_name="Address",
    )

    email = models.EmailField(
        max_length=60,
        unique=True,
        blank=False,
        null=False,
        help_text="User email.",
        verbose_name="Email",
    )

    def __str__(self):
        return f"{self.first_name} {self.paternal_last_name} {self.maternal_last_name}"

    class Meta:
        verbose_name = 'User record'
        verbose_name_plural = "User records"