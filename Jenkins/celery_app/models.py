from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError

# Create your models here.
ROLE = (("owner", "owner"), ("manager", "manager"), ("employee", "employee"))


class Restaurant(models.Model):
    res_name = models.CharField(max_length=100, blank=True, null=True)
    res_address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modify_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.res_name


class SellerProfile(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="seller_profiles"
    )
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.SET_NULL,
        related_name="res_seller_profiles",
        blank=True,
        null=True,
    )
    full_name = models.CharField(max_length=100, blank=True, null=True)
    role = models.CharField(max_length=100, choices=ROLE)
    created_at = models.DateTimeField(auto_now_add=True)
    modify_at = models.DateTimeField(auto_now=True)

    # ================================== CLEAN METHOD =================================
    def clean(self) -> None:
        if self.role == "manager":
            if SellerProfile.objects.filter(
                user=self.user,
                role="owner",
                restaurant=self.restaurant,
            ).exists():
                raise ValidationError(
                    {"role": "You are already owner of this resturants"}
                )

        if self.role == "employee":
            if (
                SellerProfile.objects.filter(user=self.user, restaurant=self.restaurant)
                .filter(role="owner")
                .exists()
            ):
                raise ValidationError(
                    {"role": "You are already owner of this resturants"}
                )

            if (
                SellerProfile.objects.filter(
                    user=self.user, restaurant=self.restaurant, role="manager"
                )
                .exclude(id=self.id)
                .exists()
            ):
                raise ValidationError(
                    {"role": "You are already manager of this resturants"}
                )
        return super().clean()
    
    # ================================== SAVE METHOD =================================
    def save(self, *args, **kwargs):
        if self.role == "manager":
            if SellerProfile.objects.filter(
                user=self.user,
                role="owner",
                restaurant=self.restaurant,
            ).exists():
                raise ValidationError(
                    {"role": "You are already owner of this resturants"}
                )

        if self.role == "employee":
            if (
                SellerProfile.objects.filter(user=self.user, restaurant=self.restaurant)
                .filter(role="owner")
                .exists()
            ):
                raise ValidationError(
                    {"role": "You are already owner of this resturants"}
                )

            if (
                SellerProfile.objects.filter(
                    user=self.user, restaurant=self.restaurant, role="manager"
                )
                .exclude(id=self.id)
                .exists()
            ):
                raise ValidationError(
                    {"role": "You are already manager of this resturants"}
                )
        super().save(*args, **kwargs)


class TemporaryRole(models.Model):
    seller_profile = models.ForeignKey(
        SellerProfile, on_delete=models.CASCADE, related_name="temporary_roles"
    )
    temporary_role = models.CharField(max_length=20, choices=ROLE)
    expires_at = models.DateTimeField()

    def is_active(self):
        return timezone.now() < self.expires_at


class EmployeeInvitation(models.Model):
    pass
