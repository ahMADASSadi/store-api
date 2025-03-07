from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

from core.models import OTP

User = get_user_model()

class HybridAuthBackend(BaseBackend):
    def authenticate(self, request, phone_number=None, password=None, otp_code=None):
        """
        Authenticate user with either password or OTP.
        """
        try:
            user = User.objects.get(phone_number=phone_number)
            if not user.is_active:
                return None

            if password:
                if user.password and user.check_password(password):
                    return user
                return None

            if otp_code:
                latest_otp = OTP.objects.filter(user=user).order_by('-created_at').first()
                if latest_otp and latest_otp.verify(otp_code):
                    latest_otp.delete()
                    return user
                return None

            return None
        
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None