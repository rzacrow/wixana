from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    def generate_unique_path(self, filename):
        return f"profile/{self.user.user_username}/{filename}"
    
    USER_TYPE_CHOICES = (
        ('O', 'Owner'),
        ('M', 'Manager'),
        ('A','Assistant'),
        ('U', 'User')
    )

    avatar = models.ImageField(upload_to=generate_unique_path, blank=True, null=True)
    email = models.CharField(unique=True, max_length=256, blank=False, null=False)
    user_type = models.CharField(max_length=1, choices=USER_TYPE_CHOICES, blank=False, null=False, default="U")

    def __str__(self) -> str:
        return self.username
    