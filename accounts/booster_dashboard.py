from .models import User, Alt, Realm, TeamDetail, TeamRequest, Wallet, Transaction, Notifications
from gamesplayed.models import Attendance, CutInIR, AttendanceDetail
from .forms import UpdateProfileForm, WalletForm
from gamesplayed.models import CutInIR
from django.db.models import Sum
from django.utils import timezone


def get_profile(pk) -> str:
    profile = User.objects.filter(id=pk).first()
    profile_form = UpdateProfileForm(initial={'username':profile.username, 'email':profile.email})

    return profile_form

def get_alts(pk) -> str:
    user = User.objects.get(id=pk)
    alts = Alt.objects.filter(player=user, status="Verified")
    Alt.objects.filter(player=user, status="Rejected").delete()
    return alts

def get_realms():
    realms = Realm.objects.all()
    return realms

def get_team(pk):
    user = User.objects.get(id=pk)
    team_detail = TeamDetail.objects.filter(player=user).first()
    if team_detail:
        members = TeamDetail.objects.filter(team=team_detail.team)
        is_leader_team = None
        new_requests = None
        request_count = None
        if team_detail.team_role == 'Leader':
            new_requests = TeamRequest.objects.filter(team=team_detail.team, status='Awaiting')
            request_count = TeamRequest.objects.filter(team=team_detail.team, status='Awaiting').count()
            if request_count < 1:
                request_count = None
            is_leader_team = True
        return {'detail': team_detail.team, 'members': members, 'is_leader_team' : is_leader_team, 'new_requests' : new_requests, 'request_count': request_count}
    return None

def get_matches(pk):
    user = User.objects.get(id=pk)
    active_attendance = AttendanceDetail.objects.filter(player=user, attendane__status='A').order_by('-attendane__date_time')[0:10]
    closed_attendance = AttendanceDetail.objects.filter(player=user, attendane__status='C').order_by('-attendane__date_time')[0:10]
    return {'active_cycle' : active_attendance, 'closed_cycle' : closed_attendance}

def get_wallet(pk):
    player = User.objects.get(id=pk)
    wallet = Wallet.objects.get_or_create(player=player)
    wallet = wallet[0]
    wallet = WalletForm(initial={'card_number' : wallet.card_number, 'IR' : wallet.IR, 'card_full_name' : wallet.card_full_name})
    return wallet

def wallet_report(pk):
    user = User.objects.get(id=pk)
    wallet = Wallet.objects.get_or_create(player=user)
    wallet = wallet[0]

    #wallet balance
    amount = wallet.amount

    todays_income = 0
    tomonth_income = 0
    to_month_attendance = AttendanceDetail.objects.filter(attendane__paid_status=True, player=user, attendane__date_time__month=timezone.datetime.today().month)
    to_day_attendance = AttendanceDetail.objects.filter(attendane__paid_status=True, player=user, attendane__date_time__day=timezone.datetime.today().day)
    for td in to_day_attendance:
        print(td.cut)
    if to_day_attendance:
        todays_income = to_day_attendance.aggregate(Sum('cut', default=0))['cut__sum']


    if to_month_attendance:
        tomonth_income = to_month_attendance.aggregate(Sum('cut', default=0))['cut__sum']
    
    
    return {'amount' : amount, 'todays_income' : todays_income, 'tomonth_income' : tomonth_income}


def cut_per_ir():
    cut_ir = CutInIR.objects.last()
    return cut_ir

def transactions(pk):
    user = User.objects.get(id=pk)
    user_transaction = Transaction.objects.filter(requester=user).order_by('-created')[:10]
    return user_transaction

def unseen_notif_badge(pk):
    user = User.objects.get(id=pk)
    count =  Notifications.objects.filter(send_to=user, status='U').count()
    if count > 0:
        return count
    else:
        return None

