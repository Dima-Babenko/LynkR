from django.db import models
from django.conf import settings


class Reaction(models.Model):
    message = models.ForeignKey('Message', on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    emoji = models.CharField(max_length=10)

    class Meta:
        unique_together = ('message', 'user')  # Один користувач — одна реакція на повідомлення

    def __str__(self):
        return f"{self.user.username} reacted {self.emoji} on message {self.message.id}"

class Chat(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='chats')
    is_group = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name if self.is_group else f"Private chat {self.id}"

    def get_other_user(self, current_user):
        if self.is_group:
            return None
        others = self.participants.exclude(id=current_user.id)
        return others.first() if others.exists() else None

class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField(blank=True)
    file = models.FileField(upload_to='chat_files/', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    reply_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies')

    def __str__(self):
        return f"{self.sender} → {self.chat}: {self.text[:30]}"
