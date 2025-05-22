from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'avatar', 'friend_id']

    def clean_friend_id(self):
        friend_id = self.cleaned_data['friend_id']
        if CustomUser.objects.filter(friend_id=friend_id).exclude(id=self.instance.id).exists():
            raise forms.ValidationError("Цей ID вже зайнятий.")
        return friend_id


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']


class CustomAuthenticationForm(AuthenticationForm):
    pass
