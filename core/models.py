from datetime import timedelta
import random

from django.contrib.auth.models import AbstractBaseUser as BaseUser, Group
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db import models

from core.validators import phone_number_validator
from core.managers import UserManager


class User(BaseUser):
    phone_number = models.CharField(max_length=11, validators=[
                                    phone_number_validator], null=False, unique=True, blank=False)
    password = models.CharField(max_length=128, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

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

    USERNAME_FIELD = 'phone_number'

    objects = UserManager()

    def __str__(self):
        return self.phone_number

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
        User,
        on_delete=models.CASCADE,
        related_name='otps'
    )
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    attempts = models.PositiveIntegerField(default=0)

    COOL_DOWN = timedelta(minutes=3)
    MAX_ATTEMPTS = 3

    def generate_otp(self):
        """Generate a random 6-digit OTP"""
        self.otp_code = f"{random.randint(100000, 999999):06}"
        self.save()
        return self.otp_code

    def can_resend(self):
        """Check if cooldown period has passed"""
        return timezone.now() >= self.created_at + self.COOL_DOWN

    def is_valid(self):
        """Check if OTP is still valid"""
        return (timezone.now() <= self.created_at + self.COOL_DOWN and
                self.attempts < self.MAX_ATTEMPTS)

    def verify(self, code):
        """Verify provided OTP code"""
        if not self.is_valid():
            return False
        self.attempts += 1
        self.save()
        return self.otp_code == code

    def __str__(self):
        return f"OTP for {self.user.phone_number} - Code: {self.otp_code}"

    class Meta:
        verbose_name = _("OTP")
        verbose_name_plural = _("OTPs")
