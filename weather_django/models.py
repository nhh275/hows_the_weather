from django.db import models

# Create your models here.
class User(models.Model):
    user_id = models.CharField(max_length=8, unique=True)
    username = models.CharField(max_length=128, unique=True)
    current_location = models.CharField(max_length=128)
    # Users NEED to have a foreign key relationship w/ Locations 

class Forum(models.Model):
    location = models.CharField(max_length=128)
    max_comments = models.IntegerField(max_length=128)

class Comment(models.Model):
    user = models.ForeignKey(User)
    url = models.URLField()
    text = models.CharField(max_length=1024)

class Location(models.Model):
    forum = models.URLField()
    rating = models.IntegerField(max_length=2)
    # weather_data = ????

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # saved_locations = models.ManyToManyField(Location)

    # Note: It might be better to include a link to a "Saved Locations" page
        # Every location has a note

# Potential adds:
    # User Profile Model?
    # Something else??? Feel free to suggest anything