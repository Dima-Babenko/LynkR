from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Chat, Message
from django.contrib.auth import get_user_model

User = get_user_model()


@login_required
def chat_list(request):
    chats = request.user.chats.all().order_by('-created_at')
    return render(request, 'chat/chat_list.html', {'chats': chats})


@login_required
def chat_detail(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    if request.user not in chat.participants.all():
        return redirect('chat:chat_list')

    messages = chat.messages.all().order_by('timestamp')

    if request.method == 'POST':
        text = request.POST.get('text')
        file = request.FILES.get('file')
        if text or file:
            Message.objects.create(
                chat=chat,
                sender=request.user,
                text=text or '',
                file=file
            )
            return redirect('chat:chat_detail', chat_id=chat.id)

    return render(request, 'chat/chat_detail.html', {
        'chat': chat,
        'messages': messages
    })


@login_required
def start_private_chat(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    chats = Chat.objects.filter(is_group=False, participants=request.user).filter(participants=other_user)

    if chats.exists():
        return redirect('chat:chat_detail', chat_id=chats.first().id)

    chat = Chat.objects.create(is_group=False)
    chat.participants.set([request.user, other_user])
    return redirect('chat:chat_detail', chat_id=chat.id)
