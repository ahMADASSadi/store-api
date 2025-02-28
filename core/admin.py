from django.contrib import admin


from core.models import User, OTP


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name',
                    'last_name', 'phone_number', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name',
                     'last_name', 'phone_number')
    list_filter = ('is_staff', 'is_active')
    ordering = ('username',)
    fieldsets = (
        ('Personal Info', {
            'fields': ('username', 'email', 'first_name', 'last_name', 'phone_number')
        }),
        ('Permissions', {
            'fields': ('is_staff', 'is_active')
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined')
        }),
        ('Security', {
            'fields': ('password',)
        })
    )


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ('user', 'otp_code', 'created_at')
    search_fields = ('user__username', 'user__email', 'otp_code')