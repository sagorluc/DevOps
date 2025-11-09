from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from celery_app.models import ROLE, Restaurant, SellerProfile, TemporaryRole


class LoginSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "password"]
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def validate_username(self, value):
        exist_user = User.objects.filter(username=value).exists()
        if not exist_user:
            raise serializers.ValidationError("User is not exists.")
        return exist_user


class RoleAssignmentSerializer(serializers.Serializer):
    username = serializers.CharField()
    role = serializers.ChoiceField(choices=ROLE)
    duration_minutes = serializers.FloatField(
        help_text="Duration in minutes for temporary role assignment"
    )

    def validate_username(self, value):
        # Ensure the username exists
        if not User.objects.filter(username=value).exists():
            raise serializers.ValidationError("User does not exist.")
        return value

    def validate(self, data):
        input_user = data["username"]
        target_role = data["role"]
        request_user = self.context["request"].user

        # Get user profiles
        request_user_profile = SellerProfile.objects.filter(user=request_user).first()
        target_user = User.objects.filter(username=input_user).first()
        target_user_profile = SellerProfile.objects.filter(user=target_user).first()

        # Validation checks
        if not request_user_profile:
            raise serializers.ValidationError("User profile not found.")
        if not target_user:
            raise serializers.ValidationError("Target user not found.")
        if not target_user_profile:
            raise serializers.ValidationError("Target user profile not found.")

        request_user_role = request_user_profile.role
        target_user_role = target_user_profile.role

        # Role-based assignment rules
        if request_user_role == "owner":
            if target_role not in ["owner", "manager", "employee"]:
                raise serializers.ValidationError(
                    "Owner can only assign manager or employee roles."
                )
            if target_user_role == "employee" and target_role == "owner":
                raise serializers.ValidationError(
                    "An employee cannot be assigned the owner role."
                )

        elif request_user_role == "manager":
            if target_role not in ["manager", "employee"]:
                raise serializers.ValidationError(
                    "Manager can only assign manager or employee roles."
                )

        elif request_user_role == "employee":
            raise serializers.ValidationError(
                "Employee does not have permission to assign roles."
            )

        # Check if target user already has the requested role
        if request_user_role in ["owner", "manager"] and target_user_role == target_role:
            raise serializers.ValidationError(
                f"{target_user_profile.user.username} is already a {target_user_role}."
            )

        return data
