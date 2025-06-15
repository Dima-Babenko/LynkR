from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Notification
from chat.models import Message  # або твоя модель повідомлень

User = get_user_model()

@receiver(post_save, sender=Message)
def create_notification(sender, instance, created, **kwargs):
    if created:
        for user in instance.chat.participants.all():
            if user != instance.sender:
                Notification.objects.create(
                    user=user,
                    notification_type='message',
                    message=f"Нове повідомлення від {instance.sender.username}"
                )
