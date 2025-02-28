from functools import wraps


class CoreUtils:
    def sms_sender(func):
        """Decorator to send an SMS before executing the function."""
        @wraps(func)
        def wrapper(self, phone_number: str, message: str, kind: str, *args, **kwargs):
            KINDS = {
                "otp": {
                    "code": kwargs.get("otp"),
                    "message": message,
                    "logic": lambda: print(f"OTP {kwargs.get('otp')} sent to {phone_number}")
                },
                "notify": {
                    "code": kwargs.get("notify"),
                    "message": message,
                    "logic": lambda: print(f"Notification sent to {phone_number}: {message}")
                }
            }

            kind_data = KINDS.get(kind.lower())

            if kind_data:
                kind_data["logic"]()

            return func(self, phone_number, *args, **kwargs)

        return wrapper

    @sms_sender
    def send_otp(self, phone_number, otp, message="Your OTP is", kind="otp"):
        print(f"{otp} sent to {phone_number}")
