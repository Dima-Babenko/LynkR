from django.utils import timezone

def update_last_seen(user):
    user.last_seen = timezone.now()
    user.save(update_fields=["last_seen"])
