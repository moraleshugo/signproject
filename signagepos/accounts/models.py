# accounts/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # Override existing fields from AbstractUser
    email = models.EmailField(max_length=255, unique=False)
    phone_number = models.CharField(max_length=20, blank=True)
    # Additional fields for user profile
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    is_admin = models.BooleanField(default=False)
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)


    def __str__(self):
        return self.username

