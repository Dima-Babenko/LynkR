from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()

class Group(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    avatar = models.ImageField(upload_to='group_avatars/', blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_groups')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class GroupMembership(models.Model):
    ROLE_CHOICES = (
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('moderator', 'Moderator'),
        ('member', 'Member'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='memberships')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'group')

    def __str__(self):
        return f"{self.user.username} in {self.group.name} as {self.role}"

class GroupPost(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Post by {self.author.username} in {self.group.name}"
