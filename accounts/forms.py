from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):

    user_type = forms.ChoiceField(
        choices=[
            ('student', 'Student'),
            ('tutor', 'Tutor/Author'),
            
        ]
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'user_type', 'password1', 'password2')