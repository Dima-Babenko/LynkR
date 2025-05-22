from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomAuthenticationForm, EditProfileForm
from .models import CustomUser, FriendRequest, Friendship

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
        Friendship.objects.create(user1=friend_request.from_user, user2=friend_request.to_user)
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