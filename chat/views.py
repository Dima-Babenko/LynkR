from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Count
from .models import Chat, Message

User = get_user_model()

@login_required
def chat_list(request):
    # Всі чати користувача, сортування за датою створення (останній вгорі)
    chats = request.user.chats.all().order_by('-created_at').prefetch_related('participants')
    return render(request, 'chat/chat_list.html', {'chats': chats})

@login_required
def chat_detail(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)

    # Перевірка, чи користувач учасник цього чату
    if request.user not in chat.participants.all():
        return redirect('chat:chat_list')

    # Всі повідомлення чату, відсортовані за часом, оптимізовано запит
    messages = chat.messages.all().order_by('timestamp').select_related('sender')

    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        file = request.FILES.get('file')

        # Створюємо повідомлення, якщо є текст або файл
        if text or file:
            Message.objects.create(
                chat=chat,
                sender=request.user,
                text=text,
                file=file
            )
            # Переадресація після відправлення для уникнення повторної відправки при оновленні сторінки
            return redirect('chat:chat_detail', chat_id=chat.id)

    return render(request, 'chat/chat_detail.html', {
        'chat': chat,
        'messages': messages,
    })

@login_required
def start_private_chat(request, user_id):
    other_user = get_object_or_404(User, id=user_id)

    # Шукаємо приватний чат між двома користувачами (без груп)
    chats = Chat.objects.filter(
        is_group=False,
        participants=request.user
    ).annotate(num_participants=Count('participants')).filter(
        participants=other_user,
        num_participants=2
    )

    if chats.exists():
        # Якщо такий чат існує, переходимо до нього
        return redirect('chat:chat_detail', chat_id=chats.first().id)

    # Інакше створюємо новий приватний чат
    chat = Chat.objects.create(is_group=False)
    chat.participants.set([request.user, other_user])

    return redirect('chat:chat_detail', chat_id=chat.id)

