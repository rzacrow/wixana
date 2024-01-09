from typing import Any
from django.forms import ModelForm
from django import forms
from .models import User, Team, Wallet
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
    

class UpdateProfileForm(forms.Form):
    avatar = forms.ImageField(allow_empty_file=True, required=False)
    username = forms.CharField(max_length=128, required=True, help_text=None)
    email = forms.EmailField(max_length=128, required=True)
    national_code = forms.CharField(max_length=10, required=False)

    def clean(self):
        cleaned_data = super().clean()
        national_code = cleaned_data.get('national_code')

        if len(national_code) != 0: 
            if (len(national_code) != 10) or (not national_code.isdigit()):
                raise ValidationError('National code must be 10 digits')

class CreateTeamForm(ModelForm):
    class Meta:
        model = Team
        fields = ['name']

class TeamRequestForm(forms.Form):
    RESPONSE_CHOICES = (
        ('Accept', 'Accept'),
        ('Reject', 'Reject'),
    )
    response = forms.ChoiceField(label="", required=True, widget=forms.RadioSelect, choices=RESPONSE_CHOICES)


class WalletForm(ModelForm):
    class Meta:
        model = Wallet
        fields = ['card_number', 'IR', 'card_full_name']

    def clean(self):
        cleaned_data = super().clean()
        card_number = cleaned_data.get('card_number')
        IR = cleaned_data.get('IR')

        if not card_number.isdigit():
            raise ValidationError("card number must be a nubmer only")
        if not IR.isdigit():
            raise ValidationError("IR must be a nubmer only")
        if len(card_number) != 16:
            raise ValidationError("card number must be 16 digits")
        if len(IR) != 24:
            raise ValidationError("IR muset be 24 digits")


class ResetPasswordForm(forms.Form):
    password = forms.CharField(max_length=16, required=True, strip=True, widget=forms.PasswordInput, label='Password')
    repassword = forms.CharField(max_length=16, required=True, strip=True, widget=forms.PasswordInput, label='Re Password')

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        repassword = cleaned_data.get('repassword')

        if len(password) < 8:
            raise ValidationError('Password should be greater than 8 characters')
            
        if password != repassword:
            raise ValidationError('Password and Re Password must be the same')


class ForgetPasswordForm(forms.Form):
    email = forms.EmailField(max_length=255, required=True, label='Email')


class CheckPasswordForm(forms.Form):
    check_code = forms.CharField(max_length=6, required=True, strip=True, label='Confirm Code')
