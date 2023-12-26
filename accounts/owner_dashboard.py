from .models import User

def get_number_of_members() -> str:
    count = User.objects.filter().count()
    return count

def get_last_attendance() -> str:
    pass