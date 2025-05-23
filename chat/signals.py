from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Chat
from accounts.models import Friendship

@receiver(post_save, sender=Friendship)
def create_chat_for_friends(sender, instance, created, **kwargs):
    if created:
        chats = Chat.objects.filter(participants=instance.user1).filter(participants=instance.user2)
        if not chats.exists():
            chat = Chat.objects.create()
            chat.participants.add(instance.user1, instance.user2)