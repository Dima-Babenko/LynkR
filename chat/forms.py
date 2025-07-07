from django import forms
from django.contrib.auth import get_user_model
from .models import Message, Chat
from accounts.models import Friendship

User = get_user_model()

class MessageForm(forms.ModelForm):
    reply_to = forms.ModelChoiceField(
        queryset=Message.objects.all(),  # обмежується в view
        required=False,
        widget=forms.HiddenInput()
    )

    class Meta:
        model = Message
        fields = ['text', 'file', 'reply_to']
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 2,
                'placeholder': 'Введіть повідомлення...',
                'class': 'form-control',
            }),
            'file': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            })
        }


class GroupChatForm(forms.ModelForm):
    participants = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        widget=forms.CheckboxSelectMultiple
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')  # дістаємо поточного користувача
        super().__init__(*args, **kwargs)

        # Дістаємо список друзів поточного користувача
        friend_ids_1 = Friendship.objects.filter(user1=user).values_list('user2_id', flat=True)
        friend_ids_2 = Friendship.objects.filter(user2=user).values_list('user1_id', flat=True)
        all_friend_ids = list(friend_ids_1) + list(friend_ids_2)

        self.fields['participants'].queryset = User.objects.filter(id__in=all_friend_ids)

    class Meta:
        model = Chat
        fields = ['name', 'participants']
