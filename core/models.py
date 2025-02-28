from datetime import timedelta, timezone
import random

from django.contrib.auth.models import AbstractUser as BaseUser, Group
from django.utils.translation import gettext_lazy as _
from django.db import models

from core.validators import phone_number_validator
from core.managers import UserManager


class User(BaseUser):
    phone_number = models.CharField(max_length=11, validators=[
                                    phone_number_validator], null=False, unique=True, blank=False)
    password = models.CharField(max_length=128, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    user_name = models.CharField(
        max_length=250, null=True, blank=True, unique=True)
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['user_name']

    object = UserManager()

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="custom_user_set",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="custom_user_set",
        related_query_name="user",
    )

    def __str__(self):
        return self.user_name

    def has_perm(self, perm, obj=None):

        if self.is_superuser:
            return True

        return self.user_permissions.filter(codename=perm).exists() or super().has_perm(perm, obj)

    def has_module_perms(self, app_label):

        if self.is_superuser:
            return True

        return self.user_permissions.filter(content_type__app_label=app_label).exists() or super().has_module_perms(app_label)

    @property
    def is_admin(self):
        return self.is_superuser

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')


class OTP(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='otps')
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    COOL_DOWN = timedelta(minutes=3)

    def is_valid(self):

        return self.created_at >= timezone.now() - self.COOL_DOWN

    def generate_otp(self):
        return f"{random.randint(100000, 999999):06}"

    def __str__(self):
        return f"OTP for {self.user.phone_number} - Code: {self.otp_code}"

    class Meta:
        verbose_name = _("OTP")
        verbose_name_plural = _("OTPs")
