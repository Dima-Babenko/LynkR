from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
import random
from django.utils import timezone


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('moderator', 'Moderator'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    friend_id = models.CharField(max_length=7, unique=True, blank=True, null=True)
    last_seen = models.DateTimeField(default=timezone.now)

    def is_moderator(self):
        return self.role in ['moderator', 'admin']

    def is_admin(self):
        return self.role == 'admin'

    def save(self, *args, **kwargs):
        if not self.friend_id:
            self.friend_id = self.generate_unique_friend_id()
        super().save(*args, **kwargs)

    def generate_unique_friend_id(self):
        while True:
            new_id = ''.join([str(random.randint(0, 9)) for _ in range(7)])
            if not CustomUser.objects.filter(friend_id=new_id).exists():
                return new_id


class Subscription(models.Model):
    follower = models.ForeignKey(CustomUser, related_name='following', on_delete=models.CASCADE)
    following = models.ForeignKey(CustomUser, related_name='followers', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')

    def __str__(self):
        return f"{self.follower.username} → {self.following.username}"



class Friendship(models.Model):
    user1 = models.ForeignKey(CustomUser, related_name='friendship_user1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(CustomUser, related_name='friendship_user2', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user1', 'user2')

    @staticmethod
    def are_friends(user1, user2):
        return Friendship.objects.filter(user1=user1, user2=user2).exists() or \
               Friendship.objects.filter(user1=user2, user2=user1).exists()