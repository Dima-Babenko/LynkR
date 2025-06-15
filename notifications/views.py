from django.shortcuts import render
from .models import Notification
from django.contrib.auth.decorators import login_required

@login_required
def notification_list(request):
    notifications = request.user.notifications.order_by('-created_at')
    notifications.filter(is_read=False).update(is_read=True)
    return render(request, 'notifications/notification_list.html', {'notifications': notifications})
