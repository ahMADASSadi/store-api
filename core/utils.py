from functools import wraps
import logging

logger = logging.getLogger("core")


class CoreUtils:
    def sms_sender(func):
        """Decorator to send an SMS before executing the function."""
        @wraps(func)
        def wrapper(self, phone_number: str, *args, **kwargs):
            KINDS = {
                "otp": {
                    "code": kwargs.get("otp"),
                    "logic": lambda: print(f"OTP {kwargs.get('otp')} sent to {phone_number}")
                },
                "notify": {
                    "code": kwargs.get("notify"),
                    "message": kwargs.get("message"),
                    "logic": lambda: print(f"Notification sent to {phone_number}: {kwargs.get("message")}")
                }
            }
            kind = kwargs.get("kind", "otp").lower()
            kind_data = KINDS.get(kind if kind else "otp")

            if kind_data:
                kind_data["logic"]()
            logger.info(f"using sms utility for {kind}")
            return func(self, phone_number, *args, **kwargs)

        return wrapper

    @sms_sender
    def send_otp(self, phone_number, otp):
        logger.info(f"Sending OTP ({otp}) to user {phone_number}")
