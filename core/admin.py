from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib import admin

from core.models import User, OTP


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('phone_number', 'is_staff', 'is_active', 'created_at') 
    search_fields = ('phone_number',)
    list_filter = ('is_staff', 'is_active')
    ordering = ('phone_number',)

    fieldsets = (
        ('Personal Info', {
            'fields': ('phone_number',)
        }),
        ('Permissions', {
            'fields': ('is_staff', 'is_active')
        }),
        ('Important dates', {
            'fields': ('last_login',)
        }),
        ('Security', {
            'fields': ('password',)
        }),
    )

    readonly_fields = ('created_at',)

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'password'),
        }),
    )

@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ('user', 'otp_code', 'created_at')
    search_fields = ('user__phone_number', 'otp_code')
