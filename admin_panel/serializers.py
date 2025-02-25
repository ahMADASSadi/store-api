from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class AdminTokenObtainSerializer(TokenObtainPairSerializer):
    """Custom serializer to restrict JWT login to staff users only."""

    def validate(self, attrs):
        data = super().validate(attrs)

        if not self.user.is_staff:
            raise serializers.ValidationError("Only staff users can log in.")

        return data


class AdminUserSerializer(serializers.ModelSerializer):
    """Serializer to return basic admin user info."""

    class Meta:
        model = User
        fields = ["id", "phone_number", "email", "is_staff", "username"]
