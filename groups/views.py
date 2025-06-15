from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from .models import Group, GroupMembership, GroupPost
from .forms import GroupForm, GroupPostForm
from django.contrib.auth import get_user_model

User = get_user_model()

def group_list(request):
    q = request.GET.get('q', '').strip()
    groups = Group.objects.all()

    if q:
        groups = groups.filter(name__icontains=q)

    user_group_ids = set()
    if request.user.is_authenticated:
        user_group_ids = set(request.user.groupmembership_set.values_list('group_id', flat=True))

    context = {
        'groups_joined': groups.filter(id__in=user_group_ids),
        'groups_not_joined': groups.exclude(id__in=user_group_ids),
        'q': q,
    }
    return render(request, 'groups/group_list.html', context)


@login_required
def group_detail(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    membership = GroupMembership.objects.filter(user=request.user, group=group).first()
    is_member = membership is not None

    members = GroupMembership.objects.filter(group=group).select_related('user').order_by(
        models.Case(
            models.When(role='owner', then=0),
            models.When(role='admin', then=1),
            models.When(role='moderator', then=2),
            models.When(role='member', then=3),
            default=4,
            output_field=models.IntegerField()
        )
    )

    if request.method == 'POST' and not is_member:
        if 'confirm' in request.POST:
            GroupMembership.objects.create(user=request.user, group=group, role='member')
            messages.success(request, "Ви приєдналися до групи!")
            return redirect('groups:group_detail', group.id)
        elif 'cancel' in request.POST:
            messages.info(request, "Ви скасували вступ.")
            return redirect('groups:group_list')

    posts = GroupPost.objects.filter(group=group).order_by('-created_at')
    post_form = GroupPostForm() if is_member else None

    return render(request, 'groups/group_detail.html', {
        'group': group,
        'is_member': is_member,
        'posts': posts,
        'post_form': post_form,
        'members': members,
        'membership': membership,
    })


@login_required
def create_group(request):
    if request.method == 'POST':
        form = GroupForm(request.POST, request.FILES)
        if form.is_valid():
            group = form.save(commit=False)
            group.owner = request.user
            group.save()
            GroupMembership.objects.create(user=request.user, group=group, role='owner')
            messages.success(request, "Групу створено!")
            return redirect('groups:group_detail', group.id)
    else:
        form = GroupForm()
    return render(request, 'groups/create_group.html', {'form': form})


@login_required
def join_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    if not GroupMembership.objects.filter(user=request.user, group=group).exists():
        GroupMembership.objects.create(user=request.user, group=group, role='member')
        messages.success(request, "Ви приєдналися до групи!")
    else:
        messages.info(request, "Ви вже є учасником цієї групи.")
    return redirect('groups:group_detail', group.id)


@login_required
def leave_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    membership = GroupMembership.objects.filter(user=request.user, group=group).first()

    if not membership:
        messages.error(request, "Ви не є учасником цієї групи.")
    elif membership.role == 'owner':
        messages.error(request, "Ви не можете покинути групу як власник.")
    else:
        membership.delete()
        messages.success(request, "Ви покинули групу.")

    return redirect('groups:group_list')


@login_required
def group_delete(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    if group.owner != request.user:
        messages.error(request, "Ви не маєте прав видаляти цю групу.")
        return redirect('groups:group_list')

    if request.method == 'POST':
        group.delete()
        messages.success(request, "Групу успішно видалено.")
        return redirect('groups:group_list')

    return render(request, 'groups/group_confirm_delete.html', {'group': group})


@login_required
def create_group_post(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    membership = GroupMembership.objects.filter(user=request.user, group=group).first()

    if not membership:
        messages.error(request, "Ви не є учасником цієї групи.")
        return redirect('groups:group_detail', group.id)

    if request.method == 'POST':
        form = GroupPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.group = group
            post.author = request.user
            post.save()
            messages.success(request, "Пост створено.")
            return redirect('groups:group_detail', group.id)
    else:
        form = GroupPostForm()

    return render(request, 'groups/create_post.html', {'form': form, 'group': group})


@login_required
def change_member_role(request, group_id, user_id):
    group = get_object_or_404(Group, id=group_id)
    target_user = get_object_or_404(User, id=user_id)
    target_membership = get_object_or_404(GroupMembership, user=target_user, group=group)
    current_membership = GroupMembership.objects.filter(user=request.user, group=group).first()

    if not current_membership or current_membership.role not in ['owner', 'admin']:
        messages.error(request, "У вас немає прав для зміни ролей.")
        return redirect('groups:group_detail', group.id)

    if target_membership.role == 'owner':
        messages.error(request, "Не можна змінити роль власника.")
        return redirect('groups:group_detail', group.id)

    if request.method == 'POST':
        new_role = request.POST.get('new_role')  # важливо: new_role, не role!
        allowed_roles = dict(GroupMembership.ROLE_CHOICES).keys()
        if new_role in allowed_roles and new_role != 'owner':
            target_membership.role = new_role
            target_membership.save()
            messages.success(request, f"Роль змінено на {new_role} для {target_membership.user.username}.")
        else:
            messages.error(request, "Неприпустима роль.")

    return redirect('groups:group_detail', group.id)
