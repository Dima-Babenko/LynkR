from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    path('friends/', views.friends_view, name='friends'),
    path('friends/send/', views.send_friend_request, name='send_friend_request'),
    path('friends/respond/<int:request_id>/<str:action>/', views.respond_to_request, name='respond_friend_request'),
    path('friends/change_id/', views.change_friend_id, name='change_friend_id'),
]