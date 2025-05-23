from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from .models import Friendship

User = get_user_model()

class FriendshipInline(admin.TabularInline):
    model = Friendship
    fk_name = 'user1'  # дружби, де користувач — user1
    extra = 0
    verbose_name = "Друг"
    verbose_name_plural = "Друзі"
    can_delete = True

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    inlines = [FriendshipInline]

    list_display = ('username', 'email', 'get_friends')

    def get_friends(self, obj):
        friends1 = Friendship.objects.filter(user1=obj).values_list('user2__username', flat=True)
        friends2 = Friendship.objects.filter(user2=obj).values_list('user1__username', flat=True)
        all_friends = list(friends1) + list(friends2)
        return ", ".join(all_friends)

    get_friends.short_description = 'Друзі'
