import logging

from django.contrib.auth import get_user_model

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import ValidationError
from rest_framework import serializers


User = get_user_model()

logger = logging.getLogger("core")


class OTPSendSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=11)

    def validate_phone_number(self, value):
        if not value.isdigit() or len(value) != 11:
            raise ValidationError("Invalid phone number")

        logger.info(f"Validated phone number")
        return value


class OTPVerifySerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=11)
    code = serializers.CharField(max_length=6)

    def validate_phone_number(self, value):
        if not value.isdigit() or len(value) != 11:
            raise ValidationError("Phone number must be 11 digits")

        logger.info(f"Validated phone number")
        return value

    def validate_code(self, value):
        if not value.isdigit() or len(value) != 6:
            raise ValidationError("OTP code must be 6 digits")
        logger.info(f"Validated OTP code")
        return value


class PasswordLoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=11)
    password = serializers.CharField(write_only=True)

    def validate_phone_number(self, value):
        if not value.isdigit() or len(value) != 11:
            raise ValidationError("Phone number must be 11 digits")

        logger.info(f"Validated phone number")
        return value

    def validate(self, data):
        phone_number = data['phone_number']
        password = data['password']
        user = User.objects.filter(phone_number=phone_number).first()
        if not user or not user.check_password(password):
            raise ValidationError("Invalid phone number or password")
        if not user.is_active:
            raise ValidationError("User account is inactive")
        data['user'] = user
        logger.info(
            f"Password authentication for user completed successfully")
        return data

    def save(self):
        user = self.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return {
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
        }


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "phone_number"]
        read_only = ["phone_number",]


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['phone_number', 'password']
        read_only = ["phone_number"]
        extra_kwargs = {'password': {'write_only': True}}

    def update(self, instance, validated_data):
        phone_number = validated_data.pop('phone_number', None)
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        logger.info(f"User {phone_number} password updated")
        return user
