from django import forms
from .models import Message, Chat

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['text', 'file']
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
    class Meta:
        model = Chat
        fields = ['name', 'participants']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'participants': forms.SelectMultiple(attrs={'class': 'form-control'})
        }