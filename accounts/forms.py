from django.forms import ModelForm
from django import forms
from .models import User

class SignupForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        