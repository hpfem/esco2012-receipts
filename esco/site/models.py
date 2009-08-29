from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)

    institution = models.CharField(max_length=100, blank=True)

    address = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=50, blank=True)
    postal_code = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50, blank=True)

    phone = models.CharField(max_length=50, blank=True)

