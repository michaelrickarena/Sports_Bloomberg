from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import UserSubscription
import logging
from django.utils import timezone  # Import timezone from django.utils (removes datetime import)
from django.contrib.auth.signals import user_logged_in
from datetime import timedelta  # This is also correct for timedelta

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

@receiver(user_logged_in)
def check_subscription_status(sender, request, user, **kwargs):
    print(f"User {user.username} logged in.")  # Print to console
    logger.info(f"User {user.username} logged in.")  # Log to file

    subscription = UserSubscription.objects.filter(user=user).first()
    if subscription:
        print(f"Subscription found: Expiration date = {subscription.expiration_date}")
        logger.info(f"Subscription found for {user.username}, expiration date: {subscription.expiration_date}")

        if subscription.expiration_date and subscription.expiration_date < timezone.now():
            subscription.status = 'inactive'
            subscription.save()
            print(f"Subscription expired. Status set to inactive.")
            logger.info(f"Subscription expired for {user.username}. Status set to inactive.")
    else:
        print("No subscription found.")
        logger.info(f"No subscription found for {user.username}")
