from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.feed, name='feed'),
    path('like/<int:post_id>/', views.like_post, name='like_post'),
    path('delete/<int:post_id>/', views.delete_post, name='delete_post'),
    path('edit/<int:post_id>/', views.edit_post, name='edit_post'),
]
