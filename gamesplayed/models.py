from django.db import models
from accounts.models import User, Realm


class RunType(models.Model):
    name = models.CharField(max_length=128, blank=True, null=False)
    community = models.FloatField(default=63.5)
    guild = models.FloatField(default=27.5)
    def __str__(self) -> str:
        return self.name
    
class Attendance(models.Model):
    ATTENDANCE_CHOICES = (
        ('A', 'Active'),
        ('C', 'Closed')
    )
    date_time = models.DateTimeField(blank=False, null=False)
    run_type = models.ForeignKey(RunType, on_delete=models.PROTECT, blank=False, null=False)
    total_pot = models.IntegerField(blank=False, null=False)
    boss_kill = models.IntegerField(blank=False, null=False)
    run_notes = models.CharField(max_length=555, blank=True, null=True)
    status = models.CharField(max_length=1, choices=ATTENDANCE_CHOICES)
    paid_status = models.BooleanField(default=False)

    def __str__(self) -> str:
        return str(self.date_time)
    
class CurrentRealm(models.Model):
    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE)
    realm = models.ForeignKey(Realm, on_delete=models.CASCADE, blank=True, null=True)
    amount = models.IntegerField(blank=True, null=True)

    def __str__(self) -> str:
        return f"{str(self.attendance.id)} - {self.realm.name} -> {self.amount}"

class Guild(models.Model):
    attendance = models.OneToOneField(Attendance, on_delete=models.CASCADE, default=None)
    booster = models.IntegerField(default=0)
    gold_collector = models.IntegerField(default=0)
    guild_bank = models.IntegerField(default=0)
    total = models.IntegerField(default=0)
    in_house_customer_pot = models.IntegerField(default=0) #sum by total
    refunds = models.IntegerField(default=0) #negative by total

    def __str__(self) -> str:
        return str(self.total)

class CutDistributaion(models.Model):
    attendance = models.OneToOneField(Attendance, on_delete=models.CASCADE)
    total_guild = models.OneToOneField(Guild, on_delete=models.CASCADE)
    community = models.IntegerField(default=0)


class Role(models.Model):
    name = models.CharField(max_length=128, blank=False, null=False)
    ratio = models.FloatField(default=1.00)

    def __str__(self) -> str:
        return self.name
    
    @classmethod
    def get_default_role(cls):
        role = cls.objects.filter()
        if role:
            return role.first().id
        role = cls.objects.get_or_create(
            name="default booster 1.0",
            defaults=dict(ratio=1.0)
        )
        return role[0].id
    


class AttendanceDetail(models.Model):
    attendane = models.ForeignKey(Attendance, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, default=Role.get_default_role, null=True)
    player = models.ForeignKey(User, on_delete=models.PROTECT)
    missing_boss = models.IntegerField(default=0)
    multiplier = models.FloatField(default=1.0)
    cut = models.IntegerField(default=0)

    def __str__(self) -> str:
        return self.player.username


class CutInIR(models.Model):
    amount = models.IntegerField()
    date_time = models.DateField(auto_now=True)
    def __str__(self) -> str:
        return str(self.amount)