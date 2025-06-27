from django import forms
from .models import Message, Chat

class MessageForm(forms.ModelForm):
    reply_to = forms.ModelChoiceField(
        queryset=Message.objects.all(),  # Або обмеження динамічно в view
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
    class Meta:
        model = Chat
        fields = ['name', 'participants']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'participants': forms.SelectMultiple(attrs={'class': 'form-control'})
        }