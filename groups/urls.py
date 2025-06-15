from django.urls import path
from . import views

app_name = 'groups'

urlpatterns = [
    path('', views.group_list, name='group_list'),
    path('create/', views.create_group, name='create_group'),
    path('<int:group_id>/', views.group_detail, name='group_detail'),
    path('<int:group_id>/join/', views.join_group, name='join_group'),
    path('<int:group_id>/leave/', views.leave_group, name='leave_group'),
    path('<int:group_id>/delete/', views.group_delete, name='group_delete'),
    path('<int:group_id>/post/', views.create_group_post, name='create_group_post'),
    path('<int:group_id>/change-member-role/<int:user_id>/', views.change_member_role, name='change_member_role'),
]
