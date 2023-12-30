from .models import User, Alt, Realm, TeamDetail, TeamRequest
from gamesplayed.models import Attendance, CutInIR
from .forms import UpdateProfileForm



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
        if team_detail.team_role == 'Leader':
            new_requests = TeamRequest.objects.filter(team=team_detail.team, status='Awaiting')
            is_leader_team = True
        return {'detail': team_detail.team, 'members': members, 'is_leader_team' : is_leader_team, 'new_requests' : new_requests}
    return None



def booster_count():
    count = User.objects.filter(status='B').count()
    return count

def admin_count():
    count = User.objects.filter(status='A').count()
    return count