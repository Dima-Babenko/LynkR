from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Post, Like
from .forms import PostForm


@login_required
def feed(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:feed')
    else:
        form = PostForm()
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'posts/feed.html', {'posts': posts, 'form': form})


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    # Перевірка, що користувач — автор або має права
    if post.author != request.user:
        return HttpResponseForbidden("Ви не можете видалити цей пост")

    if request.method == 'POST':
        post.delete()
        return redirect('posts:feed')

    # Можна зробити підтвердження видалення, якщо хочеш
    return render(request, 'posts/confirm_delete.html', {'post': post})


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = request.user
    if post.author != user and not (user.is_moderator() or user.is_admin()):
        return redirect('posts:feed')

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('posts:feed')
    else:
        form = PostForm(instance=post)
    return render(request, 'posts/edit_post.html', {'form': form, 'post': post})


@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    if not created:
        like.delete()
    return redirect('posts:feed')
