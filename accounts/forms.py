from django.forms import ModelForm
from django import forms
from .models import User
from django.core.exceptions import ValidationError

class SignupForm(forms.Form):
    username = forms.CharField(max_length=128, required=True, strip=True)
    email = forms.EmailField(max_length=128, required=True)
    password = forms.CharField(max_length=128, required=True, strip=True, widget=forms.PasswordInput)

     
    def clean_username(self):
        username = self.cleaned_data['username']
        username = username.strip()
        if len(username) < 3:
            raise ValidationError(('Username must greater than 3 characters'), code='minimum')
        elif (' ' in username):
            raise ValidationError(message='Username is not valid, Check that there are no spaces between letters')
        elif User.objects.filter(username=username).exists():
            raise ValidationError('an account with this username has already been created')
            
        return username
        
    def clean_password(self):
        password = self.cleaned_data['password']
        password = password.strip()

        if (' ' in password):
            raise ValidationError('Password is not valid, Check that there are no spaces between letters')
        if len(password) < 8:
            raise ValidationError('Password must equal or greater than 8 characters')
        return password
    
    #check that the email is unique
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError('an account with this email has already been created')
        return email
    

class ResetPasswordForm(forms.Form):
    password = forms.CharField(max_length=16, required=True, strip=True, widget=forms.PasswordInput)
    repassword = forms.CharField(max_length=16, required=True, strip=True, widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        repassword = cleaned_data.get('repassword')

        if len(password) < 8:
            raise ValidationError('Password must greater than 8 characters')
            
        if password != repassword:
            raise ValidationError('Password and Repassword must be equal')


class ForgetPasswordForm(forms.Form):
    email = forms.EmailField(max_length=255, required=True)


class ConfirmPasswordForm(forms.Form):
    confirm_code = forms.CharField(max_length=6, required=True, strip=True, label='Confirm code')

    def clean_confirm_code(self):
        cc = self.cleaned_data['confirm_code']

        if len(cc) != 6:
            raise ValidationError('Confirm code must be 6 digits')
        
        return cc

class LoginForm(forms.Form):
    username = forms.CharField(max_length=255, required=True, strip=True)
    password = forms.CharField(max_length=16, required=True, strip=True, widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data['username']
        username = username.strip()
        if (' ' in username):
            raise ValidationError(message='Username is not valid, Check that there are no spaces between letters')          
        return username
        
    def clean_password(self):
        password = self.cleaned_data['password']
        password = password.strip()

        if (' ' in password):
            raise ValidationError('Password is not valid, Check that there are no spaces between letters')
        return password