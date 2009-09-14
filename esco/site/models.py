from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)

    affiliation = models.CharField(max_length=100)

    address = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=50)
    country = models.CharField(max_length=50)

    speaker = models.BooleanField()
    student = models.BooleanField()

    accompanying = models.IntegerField()
    vegeterian = models.BooleanField()

    arrival = models.DateField()
    departure = models.DateField()

    postconf = models.BooleanField()

class UserAbstract(models.Model):
    user = models.ForeignKey(User)

    title = models.CharField(max_length=200)

    digest_tex = models.CharField(max_length=40)
    digest_pdf = models.CharField(max_length=40)

    size_tex = models.IntegerField()
    size_pdf = models.IntegerField()

    submit_date = models.DateTimeField()
    modify_date = models.DateTimeField()

    accepted = models.NullBooleanField()

