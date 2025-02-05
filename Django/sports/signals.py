from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import UserSubscription
import logging
from datetime import timedelta, timezone

logger = logging.getLogger(__name__)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_subscription(sender, instance, created, **kwargs):
    if created:
        logger.info(f"Creating subscription for new user: {instance.username}")
        try:
            expiration_date = timezone.now() + timedelta(days=7)  # Free 7-day trial
            user_subscription = UserSubscription.objects.create(
                user=instance,
                status='active',  # Mark as active during the trial
                expiration_date=expiration_date
            )
            logger.info(f"UserSubscription created for user {instance.username} with status 'active' and trial expiration on {expiration_date}")
        except Exception as e:
            logger.error(f"Error creating subscription for user {instance.username}: {str(e)}")