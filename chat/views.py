from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.db.models import Count
from .models import Chat, Message, Reaction
from .forms import MessageForm, GroupChatForm
from django.template.loader import render_to_string
import json
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now, timedelta
from django.views.decorators.csrf import csrf_exempt

User = get_user_model()


@csrf_exempt
def edit_message(request):
    if request.method == 'POST' and request.user.is_authenticated:
        data = json.loads(request.body)
        message_id = data.get('message_id')
        new_text = data.get('new_text', '').strip()
        try:
            message = Message.objects.get(id=message_id)
            if message.sender != request.user:
                return JsonResponse({'success': False, 'error': 'Це не ваше повідомлення.'})
            message.text = new_text
            message.save()
            return JsonResponse({'success': True})
        except Message.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Повідомлення не знайдено.'})
    return JsonResponse({'success': False, 'error': 'Невірний запит.'})


@csrf_exempt
def delete_message(request):
    if request.method == 'POST' and request.user.is_authenticated:
        data = json.loads(request.body)
        message_id = data.get('message_id')
        try:
            message = Message.objects.get(id=message_id)
            if message.sender != request.user:
                return JsonResponse({'success': False, 'error': 'Це не ваше повідомлення.'})
            message.delete()
            return JsonResponse({'success': True})
        except Message.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Повідомлення не знайдено.'})
    return JsonResponse({'success': False, 'error': 'Невірний запит.'})


@login_required
def chat_list(request):
    chats = request.user.chats.all().order_by('-created_at').prefetch_related('participants')
    return render(request, 'chat/chat_list.html', {'chats': chats})

@login_required
def chat_detail(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    if request.user not in chat.participants.all():
        return redirect('chat:chat_list')

    messages = chat.messages.select_related("sender", "reply_to")
    other_user = chat.get_other_user(request.user)

    is_online = False
    if other_user and other_user.last_seen:
        is_online = now() - other_user.last_seen < timedelta(seconds=60)

    form = MessageForm(request.POST or None, request.FILES or None)

    if request.method == "POST" and form.is_valid():
        message = form.save(commit=False)
        message.chat = chat
        message.sender = request.user

        reply_to_id = request.POST.get("reply_to")
        if reply_to_id:
            try:
                reply_to_msg = Message.objects.get(id=reply_to_id, chat=chat)
                message.reply_to = reply_to_msg
            except Message.DoesNotExist:
                message.reply_to = None

        message.save()

        return redirect('chat:chat_detail', chat_id=chat.id)

    return render(request, 'chat/chat_detail.html', {
        'chat': chat,
        'messages': messages,
        'form': form,
        'other_user': other_user,
        'is_online': is_online,
        'participants': chat.participants.all(),
        'room_name': f'chat_{chat.id}',
    })

@login_required
def start_private_chat(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    chats = Chat.objects.filter(
        is_group=False,
        participants=request.user
    ).annotate(num_participants=Count('participants')).filter(
        participants=other_user,
        num_participants=2
    )
    if chats.exists():
        return redirect('chat:chat_detail', chat_id=chats.first().id)
    chat = Chat.objects.create(is_group=False)
    chat.participants.set([request.user, other_user])
    return redirect('chat:chat_detail', chat_id=chat.id)

@login_required
def create_group_chat(request):
    if request.method == 'POST':
        form = GroupChatForm(request.POST, user=request.user)
        if form.is_valid():
            chat = form.save(commit=False)
            chat.is_group = True
            chat.save()
            form.save_m2m()
            if request.user not in chat.participants.all():
                chat.participants.add(request.user)
            return redirect('chat:chat_detail', chat_id=chat.id)
    else:
        form = GroupChatForm(user=request.user)

    return render(request, 'chat/create_group_chat.html', {'form': form})

@login_required
def fetch_messages(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    if request.user not in chat.participants.all():
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    messages = chat.messages.select_related("sender").order_by("timestamp")
    html = render_to_string("chat/_messages.html", {"messages": messages, "request": request})
    return JsonResponse({"html": html})

@login_required
@require_POST
def add_reaction(request):
    try:
        data = json.loads(request.body)
        message_id = data.get('message_id')
        emoji = data.get('emoji')

        message = Message.objects.get(id=message_id)

        reaction, created = Reaction.objects.update_or_create(
            user=request.user,
            message=message,
            defaults={'emoji': emoji}
        )

        reactions = list(message.reactions.values('emoji'))

        return JsonResponse({'success': True, 'reactions': reactions})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
