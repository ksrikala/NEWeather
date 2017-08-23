from django.db import models
from django.contrib.auth.models import User
from djangotoolbox.fields import ListField

class azure_americas(models.Model):
    service = models.CharField(max_length=100)
    date = models.CharField(max_length=20)
    status = models.TextField()

class azure_asia(models.Model):
    service = models.CharField(max_length=100)
    date = models.CharField(max_length=20)
    status = models.TextField()

class azure_europe(models.Model):
    service = models.CharField(max_length=100)
    date = models.CharField(max_length=20)
    status = models.TextField()
class google_americas(models.Model):
    service = models.CharField(max_length=100)
    date = models.CharField(max_length=20)
    status = models.TextField()

class google_asiapacific(models.Model):
    service = models.CharField(max_length=100)
    date = models.CharField(max_length=20)
    status = models.TextField()

class google_europe(models.Model):
    service = models.CharField(max_length=100)
    date = models.CharField(max_length=20)
    status = models.TextField()
class SavedFilter(models.Model):
    user = models.ForeignKey(User)
    templatename=models.TextField()
    cloudprovider=models.TextField()
    regions = models.TextField()
    services = models.TextField()
    date1 = models.TextField(max_length=255,default="")
    date2 = models.TextField(max_length=255,default="")
class aws_na(models.Model):
    service = models.CharField(max_length=100)
    date = models.CharField(max_length=20)
    status = models.TextField()

class aws_sa(models.Model):
    service = models.CharField(max_length=100)
    date = models.CharField(max_length=20)
    status = models.TextField()

class aws_ap(models.Model):
    service = models.CharField(max_length=100)
    date = models.CharField(max_length=20)
    status = models.TextField()

class aws_eu(models.Model):
    service = models.CharField(max_length=100)
    date = models.CharField(max_length=20)
    status = models.TextField()
