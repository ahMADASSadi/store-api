from django.core.validators import RegexValidator


phone_number_validator = RegexValidator(r'^09\d{9}$', 'Invalid phone number')
