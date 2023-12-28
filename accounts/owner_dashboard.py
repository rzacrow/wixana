from .models import User
from gamesplayed.models import Attendance, CutInIR

def member_count() -> str:
    count = User.objects.filter().count()
    
    return count

def get_last_attendance() -> str:
    last_attendance = Attendance.objects.filter(status='A')
    if last_attendance:
        get_latest = last_attendance.latest('date_time')
        return  get_latest
    return None

def get_cut_in_ir():
    cut_in_ir = CutInIR.objects.filter().first()
    return cut_in_ir

def booster_count():
    count = User.objects.filter(status='B').count()
    return count

def admin_count():
    count = User.objects.filter(status='A').count()
    return count