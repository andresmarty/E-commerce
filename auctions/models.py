from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from datetime import datetime

class User(AbstractUser):
    pass

class Listing(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=64)
    description = models.TextField(blank=True)
    startingBid = models.IntegerField()
    photo = models.TextField(blank=True)
    category = models.TextField(blank=True)
    active = models.BooleanField(default=True)
    watchlist = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.title}"

class Bid(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE, null=True)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="product")
    bids = models.IntegerField()
    

    def __str__(self):
        return f"{self.bids}"

class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE, null=True)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="name")
    comments = models.TextField(blank=True)
    date = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.comments}"
        






