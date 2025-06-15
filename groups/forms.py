from django import forms
from .models import Group, GroupPost

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'description', 'avatar']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Введіть опис групи...'}),
        }

class GroupPostForm(forms.ModelForm):
    class Meta:
        model = GroupPost
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Напишіть щось...'}),
        }