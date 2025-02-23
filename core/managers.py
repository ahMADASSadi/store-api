from django.contrib.auth.models import BaseUserManager as BaseManager


class UserManager(BaseManager):

    def create_user(self, phone_number, email=None, username=None, password=None, **kwargs):
        if not phone_number:

            raise ValueError("The phone number must be set")

        user = self.model(phone_number=phone_number, **kwargs)

        if password:
            user.set_password(password)

        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, email, password=None, **kwargs):
        kwargs.setdefault('is_active', True)
        kwargs.setdefault('is_staff', True)
        kwargs.setdefault('is_superuser', True)

        if not password:
            raise ValueError('Superusers must have a password')

        return self.create_user(phone_number=phone_number, email=email, password=password, **kwargs)
