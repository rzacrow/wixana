from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver

class User(AbstractUser):
    def generate_unique_path(self, filename):
        return f"profile/{self.username}/{filename}"
    
    USER_TYPE_CHOICES = (
        ('O', 'Owner'),
        ('A', 'Admin'),
        ('B','Booster'),
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
    ALT_STATUS_CHOICES = (
        ('Verified', 'Verified'),
        ('Awaiting', 'Awaiting'),
        ('Rejected', 'Rejected')
    )

    player = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False)
    name = models.CharField(max_length=128, blank=False, null=False)
    status = models.CharField(max_length=8, choices=ALT_STATUS_CHOICES, default='Awaiting')
    realm = models.ForeignKey(Realm, on_delete=models.PROTECT)
    def __str__(self) -> str:
        return f"{self.player.username} | {self.name}"







class Team(models.Model):
    name = models.CharField(max_length=128, blank=False, null=False)
    team_url = models.CharField(max_length=258, blank=True, null=True)
    def __str__(self) -> str:
        return self.name

@receiver(post_save, sender=Team)
def populate_parents(sender, instance, created, **kwargs):
    if created:
        instance.team_url = f"{settings.ALLOWED_HOSTS[0]}/dashboard/team/{instance.name}/{instance.id}/"
        instance.save()



class TeamDetail(models.Model):
    ROLE_TEAM_CHOICES = (
        ('Leader', 'Leader'),
        ('Member', 'Member'),
    )
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    team_role = models.CharField(max_length=6, choices=ROLE_TEAM_CHOICES, default="Member")
    def __str__(self) -> str:
        return f"{self.team.name} | {self.player.username}"
    
class TeamRequest(models.Model):
    TEAM_STATUS_CHOICES = (
        ('Verified', 'Verified'),
        ('Awaiting', 'Awaiting'),
        ('Rejected', 'Rejected')
    )

    player = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    status = models.CharField(max_length=8, choices=TEAM_STATUS_CHOICES, default='Awaiting')

class Notifications(models.Model):
    NOTIF_CHOICES = (
        ('S', 'Seen'),
        ('U', 'Unseen'),
    )

    send_to = models.ForeignKey(User, on_delete = models.CASCADE)
    title = models.CharField(max_length=48)
    caption = models.CharField(max_length=255, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=1, choices=NOTIF_CHOICES, default='U')