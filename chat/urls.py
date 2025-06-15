from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.chat_list, name='chat_list'),
    path('<int:chat_id>/', views.chat_detail, name='chat_detail'),
    path('start/<int:user_id>/', views.start_private_chat, name='start_private_chat'),
    path('create_group/', views.create_group_chat, name='create_group_chat'),
    path('<int:chat_id>/fetch_messages/', views.fetch_messages, name='fetch_messages'),
]
