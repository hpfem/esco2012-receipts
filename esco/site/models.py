from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)

    affiliation = models.CharField(max_length=100)

    address = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=50)
    country = models.CharField(max_length=50)

    phone = models.CharField(max_length=50)

    speaker = models.BooleanField()
    student = models.BooleanField()

    accompanying = models.IntegerField()
    vegeterian = models.BooleanField()

    arrival = models.DateTimeField()
    departure = models.DateTimeField()

class UserAbstract(models.Model):
    user = models.ForeignKey(User)

    title = models.CharField(max_length=200)

    digest = models.CharField(max_length=40)
    size = models.IntegerField()

    upload_date = models.DateTimeField()
    modify_date = models.DateTimeField()

    accepted = models.NullBooleanField()

