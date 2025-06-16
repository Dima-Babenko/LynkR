from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseForbidden

from .forms import CustomUserCreationForm, CustomAuthenticationForm, EditProfileForm
from .models import CustomUser, Subscription, Friendship
from chat.models import Chat

# Головна
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


# Вихід
def logout_view(request):
    logout(request)
    return redirect('home')


# Профіль
@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html', {'user': request.user})


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


# Зміна ID
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


# Додати підписку
@login_required
def subscribe_view(request):
    if request.method == 'POST':
        friend_id = request.POST.get('friend_id')
        to_user = CustomUser.objects.filter(friend_id=friend_id).exclude(id=request.user.id).first()

        if not to_user:
            messages.error(request, 'Користувача з таким ID не знайдено.')
            return redirect('friends')

        if Subscription.objects.filter(follower=request.user, following=to_user).exists():
            messages.info(request, 'Ви вже підписані на цього користувача.')
            return redirect('friends')

        # Підписка
        Subscription.objects.create(follower=request.user, following=to_user)
        messages.success(request, f'Ви підписалися на {to_user.username}.')

        # Перевіряємо взаємну підписку
        if Subscription.objects.filter(follower=to_user, following=request.user).exists():
            # Створення дружби, якщо ще немає
            if not Friendship.are_friends(request.user, to_user):
                Friendship.objects.create(user1=request.user, user2=to_user)

                # Створюємо приватний чат
                existing_chat = Chat.objects.filter(is_group=False, participants=request.user).filter(participants=to_user)
                if not existing_chat.exists():
                    chat = Chat.objects.create(is_group=False)
                    chat.participants.add(request.user, to_user)

                messages.success(request, f'Ви і {to_user.username} тепер друзі!')

        return redirect('friends')


# Видалити друга (відписка + видалення дружби)
@login_required
def remove_friend(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)

    if chat.is_group:
        return HttpResponseForbidden("Це не приватний чат.")

    if request.user not in chat.participants.all():
        return HttpResponseForbidden("Ви не учасник цього чату.")

    if request.method == 'POST':
        friend = chat.participants.exclude(id=request.user.id).first()

        if friend:
            # Видаляємо дружбу
            Friendship.objects.filter(
                Q(user1=request.user, user2=friend) |
                Q(user1=friend, user2=request.user)
            ).delete()

            # Видаляємо підписки
            Subscription.objects.filter(follower=request.user, following=friend).delete()
            Subscription.objects.filter(follower=friend, following=request.user).delete()

            # Видаляємо чат
            chat.delete()

        return redirect('friends')
    else:
        return HttpResponseForbidden("Метод не дозволений.")


# Сторінка друзів
@login_required
def friends_view(request):
    friendships = Friendship.objects.filter(Q(user1=request.user) | Q(user2=request.user))
    friends = [f.user2 if f.user1 == request.user else f.user1 for f in friendships]

    query = request.GET.get('friend_id')
    found_user = None
    already_friends = False
    already_subscribed = False

    if query:
        found_user = CustomUser.objects.filter(friend_id=query).exclude(id=request.user.id).first()
        if found_user:
            already_friends = Friendship.are_friends(request.user, found_user)
            already_subscribed = Subscription.objects.filter(follower=request.user, following=found_user).exists()

    # Передаємо ID користувачів, на яких підписаний поточний користувач
    following_ids = request.user.following.values_list('following__id', flat=True)

    return render(request, 'accounts/friends.html', {
        'friends': friends,
        'found_user': found_user,
        'already_friends': already_friends,
        'already_subscribed': already_subscribed,
        'following_ids': list(following_ids),  # передаємо як список
    })

