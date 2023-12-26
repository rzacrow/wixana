from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    def generate_unique_path(self, filename):
        return f"profile/{self.user.user_username}/{filename}"
    
    USER_TYPE_CHOICES = (
        ('O', 'Owner'),
        ('A', 'Admin'),
        ('P','Player'),
        ('U', 'User')
    )

    avatar = models.ImageField(upload_to=generate_unique_path, blank=True, null=True)
    email = models.CharField(unique=True, max_length=256, blank=False, null=False)
    user_type = models.CharField(max_length=1, choices=USER_TYPE_CHOICES, blank=False, null=False, default="U")
    discord_id = models.CharField(max_length=256, blank=True, null=True)
    avatar_hash = models.CharField(max_length=256, blank=True, null=True)
    
    def __str__(self) -> str:
        return self.username
    




class Wallet(models.Model):
    player = models.OneToOneField(User, on_delete=models.CASCADE)
    card_number = models.CharField(max_length=16, blank=False, null=False)
    IR = models.CharField(max_length=24, blank=True, null=True)
    card_full_name = models.CharField(max_length=128, blank=False, null=False)
    amount = models.IntegerField(default=0)

    def __str__(self) -> str:
        return self.card_full_name
    



class Realm(models.Model):
    name = models.CharField(max_length=128, blank=False, null=False)
    def __str__(self) -> str:
        return self.name
    


class Alt(models.Model):
    player = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False)
    name = models.CharField(max_length=128, blank=False, null=False)
    realm = models.ForeignKey(Realm, on_delete=models.PROTECT)
    def __str__(self) -> str:
        return f"{self.player.username} | {self.name}"






class Team(models.Model):
    name = models.CharField(max_length=128, blank=False, null=False)

    def __str__(self) -> str:
        return self.name





class TeamDetail(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    player = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.team.name} | {self.player.username}"


class RecantlyAction(models.Model):
    ACTION_STATUS_CHOICES = (
        ('C', 'Create'),
        ('R', 'Read'),
        ('U', 'Update'),
        ('D', 'Delete'),
    )

    date_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=1, choices=ACTION_STATUS_CHOICES, blank=False, null=False)
    obg_from_model = models.CharField(max_length=128, blank=False, null=False)
    obg_id = models.IntegerField(blank=False, null=False)