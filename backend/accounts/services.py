import re
import secrets
import string

from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from rest_framework import serializers
from .models import RoleActivationCode


RESTRICTED_ROLES = {'jury', 'organizer', 'admin'}
MAX_ACTIVE_CODES_PER_ROLE = 10


def send_html_email(subject: str, template_name: str, context: dict, recipient: str) -> None:
    html_message = render_to_string(template_name, context)
    email = EmailMessage(
        subject=subject,
        body=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient],
    )
    email.content_subtype = 'html'
    email.send()


def validate_strong_password(password, user=None, field_name='password'):
    errors = []
    if not re.search(r'[A-Z]', password):
        errors.append('Password must include at least one uppercase letter.')
    if not re.search(r'[a-z]', password):
        errors.append('Password must include at least one lowercase letter.')
    if not re.search(r'\d', password):
        errors.append('Password must include at least one digit.')
    if not re.search(r'[^A-Za-z0-9]', password):
        errors.append('Password must include at least one special character.')
    if errors:
        raise serializers.ValidationError({field_name: errors})

    validate_password(password, user=user)


def generate_unique_role_code(length=12):
    alphabet = string.ascii_uppercase + string.digits
    for _ in range(20):
        code = ''.join(secrets.choice(alphabet) for _ in range(length))
        if not RoleActivationCode.objects.filter(code=code).exists():
            return code
    raise serializers.ValidationError({'message': ['Unable to generate a unique activation code. Please retry.']})