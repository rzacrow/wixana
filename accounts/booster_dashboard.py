from .models import User, Alt, Realm, TeamDetail, TeamRequest, Wallet, Transaction
from gamesplayed.models import Attendance, CutInIR, AttendanceDetail
from .forms import UpdateProfileForm, WalletForm
from gamesplayed.models import CutInIR



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
        if team_detail.team_role == 'Leader':
            new_requests = TeamRequest.objects.filter(team=team_detail.team, status='Awaiting')
            is_leader_team = True
        return {'detail': team_detail.team, 'members': members, 'is_leader_team' : is_leader_team, 'new_requests' : new_requests}
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
    amount = wallet.amount
    return {'amount' : amount}


def cut_per_ir():
    cut_ir = CutInIR.objects.last()
    return cut_ir

def transactions(pk):
    user = User.objects.get(id=pk)
    user_transaction = Transaction.objects.filter(requester=user).order_by('-created')[:10]
    return user_transaction