from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.encoding import force_bytes, force_str  # Changed force_text to force_str

# Generate token for email verification
def generate_email_verification_token(user):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    return uid, token

# Send verification email
def send_verification_email(request, user, uid, token):
    subject = 'Activate your account'
    verification_link = f"{settings.SITE_URL}/verify-email?uid={uid}&token={token}"
    message = f"Hi {user.username},\n\nTo activate your account, click the following link:\n{verification_link}"
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
