from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomAuthenticationForm, EditProfileForm
from .models import CustomUser, FriendRequest, Friendship
from chat.models import Chat
from django.db.models import Q
from django.http import HttpResponseForbidden

# Головна сторінка
def home(request):
    return render(request, 'home.html')

# Реєстрація
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Реєстрація пройшла успішно!")
            return redirect('/')
        else:
            messages.error(request, "Помилка реєстрації.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

# Вхід
def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('/')
        else:
            messages.error(request, "Невірний логін або пароль.")
    else:
        form = CustomAuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

# Редагування профілю
@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = EditProfileForm(instance=request.user)
    return render(request, 'accounts/edit_profile.html', {'form': form})

# Вихід
def logout_view(request):
    logout(request)
    return redirect('home')

# Профіль
@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html', {'user': request.user})


# Сторінка друзів
@login_required
def friends_view(request):
    friend_requests = request.user.received_requests.all()
    friendships = Friendship.objects.filter(user1=request.user) | Friendship.objects.filter(user2=request.user)
    friends = [f.user2 if f.user1 == request.user else f.user1 for f in friendships]

    query = request.GET.get('friend_id')
    found_user = None
    already_friends = False

    if query:
        found_user = CustomUser.objects.filter(friend_id=query).exclude(id=request.user.id).first()
        if found_user and Friendship.are_friends(request.user, found_user):
            already_friends = True

    return render(request, 'accounts/friends.html', {
        'friends': friends,
        'found_user': found_user,
        'already_friends': already_friends,
        'requests': friend_requests
    })

@login_required
def send_friend_request(request):
    if request.method == 'POST':
        friend_id = request.POST.get('friend_id')
        to_user = CustomUser.objects.filter(friend_id=friend_id).exclude(id=request.user.id).first()
        if to_user:
            if not Friendship.are_friends(request.user, to_user) and \
               not FriendRequest.objects.filter(from_user=request.user, to_user=to_user).exists():
                FriendRequest.objects.create(from_user=request.user, to_user=to_user)
                messages.success(request, 'Запит надіслано.')
            else:
                messages.error(request, 'Ви вже друзі або запит вже існує.')
        else:
            messages.error(request, 'Користувача не знайдено.')
    return redirect('friends')


@login_required
def respond_to_request(request, request_id, action):
    friend_request = get_object_or_404(FriendRequest, id=request_id, to_user=request.user)

    if action == 'accept':
        # Створюємо запис дружби
        Friendship.objects.create(user1=friend_request.from_user, user2=friend_request.to_user)

        # Створюємо чат, якщо ще не існує
        from_user = friend_request.from_user
        to_user = friend_request.to_user

        existing_chats = Chat.objects.filter(
            is_group=False,
            participants=from_user
        ).filter(
            participants=to_user
        )

        if not existing_chats.exists():
            chat = Chat.objects.create(is_group=False)
            chat.participants.add(from_user, to_user)

        # Видаляємо запит
        friend_request.delete()

    elif action == 'reject':
        friend_request.delete()

    return redirect('friends')


@login_required
def change_friend_id(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ваш ID оновлено.')
            return redirect('friends')
    else:
        form = EditProfileForm(instance=request.user)
    return render(request, 'accounts/change_friend_id.html', {'form': form})


@login_required
def remove_friend(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)

    if chat.is_group:
        return HttpResponseForbidden("Це не приватний чат.")

    if request.user not in chat.participants.all():
        return HttpResponseForbidden("Ви не учасник цього чату.")

    if request.method == 'POST':
        # Знайдемо іншого учасника чату — це і є друг
        friend = chat.participants.exclude(id=request.user.id).first()

        if friend:
            # Видалити дружбу між request.user і friend
            friendship = Friendship.objects.filter(
                (Q(user1=request.user) & Q(user2=friend)) |
                (Q(user1=friend) & Q(user2=request.user))
            ).first()

            if friendship:
                friendship.delete()

            # Можна також видалити чат, якщо потрібно, або залишити
            chat.delete()

        return redirect('friends')  # або куди потрібно

    else:
        return HttpResponseForbidden("Метод не дозволений.")
