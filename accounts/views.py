from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib import messages
from django.conf import settings
import requests
from django.contrib.auth import authenticate, login, logout
import shutil
import os
from . import booster_dashboard

#forms
from .forms import SignupForm, LoginForm, UpdateProfileForm, CreateTeamForm, WalletForm

#models
from .models import User, Wallet, Alt, Realm, Team, TeamDetail, TeamRequest, Notifications, Transaction
from gamesplayed.models import CutInIR


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
                            messages.add_message(request, messages.SUCCESS, message=f"Welcome back {user['username']}")
                            return redirect('dashboard')
                        else:
                            messages.add_message(request, messages.ERROR, "This username is reserved. You can't connect to it with Discord")
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
                                messages.add_message(request, messages.SUCCESS, message=f"Welcome back {user['username']}")
                                return redirect('dashboard')
                            else:
                                messages.add_message(request, messages.ERROR, "This email is reserved. You can't connect to it with Discord")
                                return redirect('login')
                        else:
                                messages.add_message(request, messages.ERROR, "This email is reserved. You can't connect to it with Discord")
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
        if request.user.is_authenticated:
            #Define Context
            context = dict()

            #get user 
            user = request.user

            #get user profile
            context['profile_form'] = booster_dashboard.get_profile(pk=user.id)

            #if get query for add alts exist
            altname =  request.GET.get('altname')
            realm = request.GET.get('realm')

            #A flag to identify the user level
            is_superuser = None
            is_user = None
            if altname and realm:
                if (altname == '') or (altname == None) or (int(realm) == 0):
                    messages.add_message(request, messages.ERROR, 'You must fill all required fields')
                else:
                    realm_obj = Realm.objects.get(id=realm)
                    alts = Alt.objects.filter(realm=realm_obj, name=altname, player=request.user)
                    if not alts:
                        Alt.objects.create(realm=realm_obj, name=altname, player=request.user)
                        messages.add_message(request, messages.SUCCESS, 'Alt added successfully, after admin approval, it will be placed in your profile')
                    else:
                        messages.add_message(request, messages.WARNING, 'Alt with this detail already exist')

            if user.is_superuser:
                #change user type to Owner in first login
                is_superuser = True
                if user.user_type != 'O':
                    user.user_type = 'O'
                    user.save()
                    return redirect('dashboard')
            if user.user_type != 'U':
                context['alts'] = booster_dashboard.get_alts(pk=user.id)
                context['realms'] = booster_dashboard.get_realms()
                context['team'] = booster_dashboard.get_team(pk=user.id)
                context['create_team_form'] = CreateTeamForm()
                context['matches'] = booster_dashboard.get_matches(pk=user.id)
                context['wallet'] = booster_dashboard.get_wallet(pk=user.id)
                context['wallet_report'] = booster_dashboard.wallet_report(pk=user.id)
                context['cut_per_ir'] = booster_dashboard.cut_per_ir()
                context['transactions'] = booster_dashboard.transactions(pk=user.id)
                context['unseen_notif_count'] = booster_dashboard.unseen_notif_badge(pk=user.id)
            else:
                is_user = True
                context['is_user'] = is_user

            context['notifications'] = Notifications.objects.filter(send_to=request.user, status="U")

            
            context['is_superuser'] = is_superuser

            return render(request, 'accounts/dashboard.html', context)
        else:
            messages.add_message(request, messages.WARNING, 'Login required!')
            return redirect('login')
        

    def post(self, request):
        print(request.FILES)
        profile_form = UpdateProfileForm(request.POST, request.FILES)
        print(request.FILES['avatar'])
        if profile_form.is_valid():
            user = User.objects.get(id=request.user.id)
            print(request.FILES['avatar'])
            user.avatar = request.FILES['avatar']
            user.save()
            messages.add_message(request, messages.SUCCESS, "Profile updated successfully")
            return redirect('dashboard')
        else:
            return render(request, 'accounts/dashboard.html', {'profile_form': profile_form})


class CreateTeam(View):
    def post(self, request):
        create_team_form = CreateTeamForm(request.POST)
        if create_team_form.is_valid():
            data = create_team_form.cleaned_data
            team = Team.objects.create(name=data['name'])
            team.save()

            TeamDetail.objects.create(team=team, player=request.user, team_role="Leader")
            messages.add_message(request, messages.SUCCESS, 'Your team created successfully')
            return redirect('dashboard')
        else:
            messages.add_message(request, messages.ERROR, f"Error team form: name is required")
            return redirect('dashboard')
        
class LeftTheTeam(View):
    def get(self, request, team_pk):
        team = Team.objects.filter(id=team_pk).first()
        team_detail = TeamDetail.objects.filter(team=team, player=request.user).first()
        if team_detail:
            is_leader = False
            if team_detail.team_role == "Leader":
                is_leader = True

            team_detail.delete()
            messages.add_message(request, messages.SUCCESS, f"You left team {team.name}")
            if (TeamDetail.objects.filter(team=team).count()) < 1:
                #if members of team equal to 0, removed the team 
                team.delete()
            elif is_leader:
                #change leader team
                next_leader = TeamDetail.objects.filter(team=team).first()
                next_leader.team_role = "Leader"
                next_leader.save()

            return redirect('dashboard')
        else:
            messages.add_message(request, messages.ERROR, f"Request is not valid")
            return redirect('dashboard')


class TeamDetailLink(View):
    def get(self, request, team_name, team_pk):
        if request.user.is_authenticated:
            if request.user.user_type == 'U':
                messages.add_message(request, messages.WARNING, 'You are not allowed to see this content')
                return redirect('dashboard')
            
            team = Team.objects.filter(id=team_pk).first()

            if team:
                user_have_team = None
                user = request.user
                td = TeamDetail.objects.filter(team=team, player=user)
                if td:
                    user_have_team = True
            else:
                messages.add_message(request, messages.WARNING, 'Team not found')
                return redirect('dashboard')
            

            context = {
                'team' : team,
                'user_have_team' : user_have_team
            }

            return render(request, 'accounts/team.html', context)
        else:
            messages.add_message(request, messages.WARNING, 'Login required!')
            return redirect('login')
    
    def post(self, request, team_name, team_pk):
        user_requested = request.user
        if user_requested.user_type != 'U':
            team = Team.objects.filter(id=team_pk).first()
            is_requesetd_before = TeamRequest.objects.filter(player=user_requested, team=team, status='Awaiting')
            if not is_requesetd_before:
                TeamRequest.objects.create(player=user_requested, team=team)
                messages.add_message(request, messages.SUCCESS, 'Your request to join the team has been sent')
            else:
                messages.add_message(request, messages.ERROR, 'You have already sent a request to this team')
            return redirect('dashboard')
        else:
            messages.add_message(request, messages.ERROR, 'You are not allowed to join the team')
            return redirect('dashboard')
    

class JoinTeamResponse(View):
    def post(self, request):
        data = request.POST['response']
        team_id = request.POST['team']
        username = request.POST['username']
        team = Team.objects.filter(id=team_id).first()
        player = User.objects.filter(username=username).first()

        if data == 'accept':
            if not TeamDetail.objects.filter(player=player):
                TeamDetail.objects.create(team=team, player=player)
                Notifications.objects.create(send_to=player, title="Join Team", caption=f"You are now a member of {team.name}")
                messages.add_message(request, messages.SUCCESS, message=f"User {player.username} joined to your team")
            else:
                Notifications.objects.create(send_to=player, title="Join Team", caption=f"Your request to joined team {team.name} accepted, but you are already have a team")
                messages.add_message(request, messages.WARNING, message=f"User {player.username} already has a team")
            
            rq = TeamRequest.objects.filter(team=team, player=player, status="Awaiting").first()
            rq.status = "Verified"
            rq.save()
            del rq
            return redirect('dashboard')
        else:
                Notifications.objects.create(send_to=player, title="Join Team", caption=f"Your request to joined team {team.name} rejected.")
                messages.add_message(request, messages.WARNING, message=f"User {player.username} rejected!")
                rq = TeamRequest.objects.filter(team=team, player=player, status="Awaiting").first()
                rq.status = "Rejected"
                rq.save()
                del rq

                
                return redirect('dashboard')
        
class SeenNotif(View):
    def get(self, request):
        if request.user.is_authenticated:
            notif = Notifications.objects.filter(send_to=request.user)
            for nf in notif:
                nf.status = 'S'
                nf.save()
                nf.delete()
            
        return redirect('dashboard')


class WalletUpdateDetail(View):
    def post(self, request):
        wallet_form = WalletForm(request.POST)
        if wallet_form.is_valid():
            data = wallet_form.cleaned_data
            wallet = Wallet.objects.get_or_create(player=request.user)
            wallet = wallet[0]
            wallet.card_full_name = data['card_full_name']
            wallet.card_number = data['card_number']
            wallet.IR = data['IR']
            wallet.save()

            messages.add_message(request, messages.SUCCESS, 'Wallet detail, updated successfully')
            return redirect('dashboard')
        else:
            messages.add_message(request, messages.ERROR, wallet_form.errors)
            return redirect('dashboard')
        

class AskingMoney(View):
    def post(self, request):
        if request.user.is_authenticated:
            user = request.user
            if user.user_type != 'U':
                currency = request.POST['asking_money_type']
                amount = int(request.POST['asking_money_amount'])
                wallet = Wallet.objects.get(player=user)
                if amount <= wallet.amount:
                    if amount >= 1:
                        wallet.amount -= amount
                        wallet.save()
                        if currency == 'IR':
                            try:
                                cut_in_ir = CutInIR.objects.last()
                                cut_in_ir = int(cut_in_ir.amount)
                            except:
                                Transaction.objects.create(requester=user, amount=amount, currency=currency, caption="there was a problem to convert the rate, the amount mentioned is in Cut")
                            else:
                                print(amount)
                                amount = amount * cut_in_ir
                                print(amount)
                                Transaction.objects.create(requester=user, amount=amount, currency=currency)
                            messages.add_message(request, messages.SUCCESS, "Your payment request has been successfully registered")
                        else:        
                            Transaction.objects.create(requester=user, amount=amount, currency=currency)
                            messages.add_message(request, messages.SUCCESS, "Your payment request has been successfully registered")
                        admins = User.objects.filter(user_type__in=['A', 'O'])
                        for admin in admins:
                            Notifications.objects.create(send_to=admin, title="Payment reqeust", caption=f"You have a new payment request from {request.user.username}")
                    else:
                        messages.add_message(request, messages.WARNING, 'Payment request in not valid')

                else:
                    messages.add_message(request, messages.WARNING, 'Your wallet balance is not enough')

        return redirect('dashboard')