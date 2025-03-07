import traceback
import logging

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction

from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, status

from core.serializers import OTPSendSerializer, OTPVerifySerializer, PasswordLoginSerializer, UserUpdateSerializer, UserSerializer
from core.utils import CoreUtils
from core.models import OTP


User = get_user_model()

utility = CoreUtils()

logger = logging.getLogger("core")


class AuthenticationViewSet(viewsets.ViewSet):
    """
    ViewSet for handling OTP generation and verification
    """
    @action(methods=["post"], detail=False, url_path="send")
    def send_otp(self, request):
        """Takes a phone number and sends it an OTP code via SMS"""
        serializer = OTPSendSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data["phone_number"]
        logger.info(f"Attempting to send OTP to phone_number={phone_number}")

        try:
            user, created = User.objects.get_or_create(
                phone_number=phone_number)
            logger.debug(
                f"User retrieved/created: phone_number={phone_number}, created={created}")
            if not user.is_active:
                logger.warning(
                    f"Authentication failed: inactive user, phone_number={phone_number}")
                raise AuthenticationFailed(
                    detail="User account is inactive",
                    code="user_inactive"
                )

            with transaction.atomic():
                last_otp = OTP.objects.filter(
                    user=user).order_by('-created_at').first()
                if last_otp and not last_otp.can_resend():
                    time_remaining = (last_otp.created_at + OTP.COOL_DOWN - timezone.now()).total_seconds()
                    logger.warning(
                        f"Rate limit hit for phone_number={phone_number}, time_remaining={int(time_remaining)}s"
                    )
                    return Response(
                        {
                            "status": "error",
                            "data": {
                                "error": "Please wait before requesting a new OTP",
                                "time_remaining_seconds": max(0, int(time_remaining))
                            }
                        },
                        status=status.HTTP_429_TOO_MANY_REQUESTS
                    )

                otp = OTP.objects.create(user=user)
                otp_code = otp.generate_otp()
                logger.info(
                    f"OTP generated for phone_number={phone_number}, otp_id={otp.id}")

            utility.send_otp(phone_number=phone_number, otp=otp_code)
            logger.info(
                f"OTP successfully sent to phone_number={phone_number}")

            return Response(
                {"status": "success", "data": {"message": "OTP sent successfully"}},
                status=status.HTTP_200_OK
            )

        except AuthenticationFailed as e:
            logger.error(
                f"Authentication failed for phone_number={phone_number}: {str(e)}")
            return Response({"status": "error", "data": {"error": str(e)}}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            logger.error(
                f"Unexpected error for phone_number={phone_number}: {str(e)}\n{traceback.format_exc()}")
            return Response(
                {"status": "error", "data": {
                    "error": f"An unexpected error occurred: {e}"}},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(methods=["post"], detail=False, url_path="verify")
    def verify_otp(self, request):
        """Takes both phone number and OTP code and returns access and refresh tokens"""
        serializer = OTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data["phone_number"]
        code = serializer.validated_data["code"]
        logger.info(
            f"Verifying OTP for phone_number={phone_number}, code={code}")

        try:
            user = User.objects.get(phone_number=phone_number)
            latest_otp = OTP.objects.filter(
                user=user).order_by('-created_at').first()

            if not latest_otp or not latest_otp.verify(code):
                logger.warning(
                    f"OTP verification failed for phone_number={phone_number}, code={code}")
                return Response(
                    {"status": "error", "data": {"error": "Invalid or expired OTP"}},
                    status=status.HTTP_400_BAD_REQUEST
                )

            refresh_token = RefreshToken.for_user(user)
            access_token = str(refresh_token.access_token)
            logger.info(
                f"OTP verified successfully for phone_number={phone_number}, user_id={user.id}")
            response_data = {
                "status": "success",
                "data": {
                    "message": "OTP verified successfully",
                    "access_token": access_token,
                    "refresh_token": str(refresh_token)
                }
            }
            latest_otp.delete()
            logger.debug(
                f"OTP deleted after successful verification for phone_number={phone_number}")
            return Response(response_data, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            logger.error(f"User not found for phone_number={phone_number}")
            return Response(
                {"status": "error", "data": {"error": "User not found"}},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(methods=["post"], detail=False, url_path="login")
    def password_login(self, request):
        """Takes phone number and password, returns JWT tokens"""
        serializer = PasswordLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data.get("phone_number", "unknown")
        logger.info(f"Password login attempt for phone_number={phone_number}")

        try:
            tokens = serializer.save()
            logger.info(f"Login successful for phone_number={phone_number}")
            return Response(
                {
                    "status": "success",
                    "data": {
                        "message": "Login successful",
                        "access_token": tokens["access_token"],
                        "refresh_token": tokens["refresh_token"]
                    }
                },
                status=status.HTTP_200_OK
            )
        except ValidationError as e:
            logger.warning(
                f"Login failed for phone_number={phone_number}: {str(e)}")
            return Response(
                {"status": "error", "data": {"error": str(e)}},
                status=status.HTTP_400_BAD_REQUEST
            )


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.request.user.id
        logger.debug(
            f"Fetching queryset for user_id={user_id}, action={self.action}")
        return User.objects.filter(id=user_id)

    def get_serializer_class(self):
        user_id = self.request.user.id
        if self.action in ['update', 'partial_update']:
            logger.debug(
                f"Using UserUpdateSerializer for user_id={user_id}, action={self.action}")
            return UserUpdateSerializer
        logger.debug(
            f"Using UserSerializer for user_id={user_id}, action={self.action}")
        return UserSerializer
