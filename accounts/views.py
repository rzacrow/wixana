from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib import messages
from django.conf import settings
import requests
from django.contrib.auth import authenticate, login, logout
import shutil
import os
from . import owner_dashboard


#forms
from .forms import SignupForm, LoginForm

#models
from .models import User


class Signup(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        
        form = SignupForm()
        
        context = {
            'form' : form
        }

        return render(request, 'accounts/signup.html', context)
    

    def post(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        
        form = SignupForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            create_user = User.objects.create(username=data['username'], email=data['email'])
            create_user.set_password(data['password'])
            create_user.save()
            messages.add_message(request, messages.SUCCESS, 'Your account has been successfully created')

            user = authenticate(request, username=data['username'], password=data['password'])
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.add_message(request, messages.SUCCESS, 'Your account was created but there was a problem logging in. Log in to your account')
                return redirect('login')
            
        else:
            return render(request, 'accounts/signup.html', {'form' : form})





class SignupDiscord(View):
    def get(self, request):
        code = request.GET.get('code')
        url = "https://discord.com/api/oauth2/token"
        if code:
            CLIENT_ID = "1187671686179467285"
            CLIENT_SECRET = "tCSBGmtghlEW9Bf15g2hr4PZxR4U0I9g"
            REDIRECT_URI = "http://127.0.0.1:8000/signup/discord/response/"

            header = {
                'Content-Type' : 'application/x-www-form-urlencoded'
            }
            data = {
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': REDIRECT_URI
            }

            try:
                response = requests.post(url=f"{url}",headers=header, data=data, auth=(CLIENT_ID, CLIENT_SECRET))
            except:
                messages.add_message(request, messages.ERROR, 'Could not connect to Discord. try again')
                return redirect('signup')
            else:
                user_token = response.json()
                header = {
                    'authorization' : f"{user_token['token_type']} {user_token['access_token']}",
                }

                user = requests.get(url="https://discord.com/api/users/@me", headers=header)
                user = user.json()

                if user['verified'] == True:                    
                    #get user avatar with discord cdn
                    avatar_hash = None

                    if user['avatar']:
                        r = requests.get(url=f"https://cdn.discordapp.com/avatars/{user['id']}/{user['avatar']}", stream=True)
                        img_path = f"media/profile/discord/{user['id']}/"
                        #make top directories
                        os.makedirs(os.path.dirname(img_path), exist_ok=True)

                        #get image from request and copy into follow path with unique user_id/user_avatar_hash
                        with open("{0}{1}.png".format(img_path, user['avatar']), 'wb') as f:
                            shutil.copyfileobj(r.raw, f)

                            #save path profile into db
                            avatar_hash = "{0}{1}.png".format(img_path, user['avatar'])

                    #if username exist
                    if User.objects.filter(username=user['username']).exists():
                        get_user = User.objects.get(username=user['username'])
                        if get_user.discord_id:
                            get_user.email = user['email']
                            get_user.discord_id = user['id']
                            get_user.avatar_hash = avatar_hash
                            get_user.save()
                            login(request, get_user, backend=settings.AUTHENTICATION_BACKENDS[0])
                            messages.add_message(request, messages.ERROR, message=f"Welcome back {user['username']}")
                            return redirect('dashboard')
                        else:
                            messages.add_message(request, messages.SUCCESS, "This username is reserved. You can't connect to it with Discord")
                            return redirect('login')
                    
                    #if email exist
                    if User.objects.filter(email=user['email']).exists():
                        get_user = User.objects.get(email=user['email'])
                        #check user sign in from discord : if True -> change username
                        if get_user.discord_id:
                            if get_user.discord_id == user['id']:
                                get_user.username = user['username']
                                get_user.discord_id = user['id']
                                get_user.avatar_hash = avatar_hash
                                get_user.save()
                                login(request, get_user, backend=settings.AUTHENTICATION_BACKENDS[0])
                                messages.add_message(request, messages.ERROR, message=f"Welcome back {user['username']}")
                                return redirect('dashboard')
                            else:
                                messages.add_message(request, messages.SUCCESS, "This email is reserved. You can't connect to it with Discord")
                                return redirect('login')
                        else:
                                messages.add_message(request, messages.SUCCESS, "This email is reserved. You can't connect to it with Discord")
                                return redirect('login')            
                            


                    create_user = User.objects.create(username=user['username'], email=user['email'], discord_id=user['id'], avatar_hash=avatar_hash)
                    create_user.save()
                    login(request, create_user, backend=settings.AUTHENTICATION_BACKENDS[0])
                    messages.add_message(request, messages.SUCCESS, 'Your account has been successfully created')
                    return redirect('dashboard')

                else:
                    messages.add_message(request, messages.ERROR, 'Your Discord account has not been verified')
                    return redirect('signup')              
        else:
            messages.add_message(request, messages.ERROR, 'There was a problem authenticating you through Discord')
            return redirect('signup')


class Login(View):
    def get(self,request):
        #if user was logged in, then redirect to dashboard
        if request.user.is_authenticated:
            return redirect('dashboard')
        
        form = LoginForm()

        context = {
            'form' : form,
        }

        return render(request, 'accounts/login.html', context)
    
    def post(self, request):
        form = LoginForm(request.POST)

        if form.is_valid():
            #get cleaned data
            data = form.cleaned_data
            password = data['password']
            username = data['username']
            print(username)
            print(password)
            #If a user with the entered profile is found
            user = authenticate(request, username=username,password=password)
            if user is not None:
                login(request, user)
                messages.add_message(request, level=messages.SUCCESS, message=f"Welcome back {username}")
                return redirect('dashboard')
            else:
                messages.add_message(request, level=messages.ERROR, message='Wrong username or password')
                return redirect('login')
        else:
            context = {
                'form': form
            }
            return render(request, 'accounts/login.html', context)
        

class Logout(View):
    def get(self, request):
        logout(request)
        return redirect('login')
    
    
class Dashboard(View):
    def get(self, request):
        user = request.user
        context = dict()
        context['user'] = user
        if user.is_superuser:
            is_superuser = True
            context['member_count'] = owner_dashboard.get_cut_in_ir()
            context['last_attendance'] = owner_dashboard.get_last_attendance()
            context['recantly_actions'] = owner_dashboard.get_recantly_actions()
        else:
            is_superuser = None
        
        context['is_superuser'] = is_superuser

        return render(request, 'accounts/dashboard.html', context)

