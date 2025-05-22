from django.db import models
from django.conf import settings


class Chat(models.Model):
    """
    Чат — може бути або приватним (між 2 людьми), або груповим.
    """
    name = models.CharField(max_length=255, blank=True, null=True)  # Для групового чату
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='chats')
    is_group = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name if self.is_group else f"Private chat {self.id}"


class Message(models.Model):
    """
    Повідомлення в чаті.
    """
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField(blank=True)
    file = models.FileField(upload_to='chat_files/', blank=True, null=True)  # фото/відео/файли
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender} → {self.chat}: {self.text[:30]}"
