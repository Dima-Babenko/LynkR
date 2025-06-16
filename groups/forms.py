from django import forms
from .models import Group, GroupPost
from .models import GroupReview

from django import forms
from .models import GroupReview

class GroupReviewForm(forms.ModelForm):
    class Meta:
        model = GroupReview
        fields = ['content', 'rating']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Напишіть ваш відгук...',
            }),
            'rating': forms.RadioSelect(
                choices=[(i, f'{i} зірок') for i in range(1, 6)],
                attrs={'class': 'star-input'}
            ),
        }
        labels = {
            'content': '',
            'rating': '',
        }


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