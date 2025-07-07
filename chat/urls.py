from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.chat_list, name='chat_list'),
    path('<int:chat_id>/', views.chat_detail, name='chat_detail'),
    path('start/<int:user_id>/', views.start_private_chat, name='start_private_chat'),
    path('create_group/', views.create_group_chat, name='create_group_chat'),
    path('<int:chat_id>/fetch_messages/', views.fetch_messages, name='fetch_messages'),
    path('add-reaction/', views.add_reaction, name='add_reaction'),
    path('edit-message/', views.edit_message, name='edit_message'),
    path('delete-message/', views.delete_message, name='delete_message'),
]
