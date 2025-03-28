import json
from django.db import models
from jsonfield import JSONField
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from django.utils.timezone import now
MAX_CHAR_LENGTH = 128
MAX_REVIEW_LENGTH = 256
# Create your models here.


class Location(models.Model):
    name = models.CharField(max_length=MAX_CHAR_LENGTH)
    location_forum = models.URLField(blank=False)

    #Can probably be renamed for clarity on average-calculation
    total_rating = models.IntegerField(default=0)
    # Keep the below commented until we know how to properly implement it
    people_voted = models.IntegerField(default=0)

    weather_description = models.CharField(max_length=MAX_CHAR_LENGTH)
    slug = models.SlugField(unique=True)
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Location, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Locations'
    
    def __str__(self):
        return self.name
    
    
class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    rating_value = models.IntegerField()
    date_rated = models.DateField(default=now)
    
    class Meta:
        verbose_name_plural = 'Ratings'
        unique_together = ('user','location','date_rated')
    
class Forum(models.Model):
    locationName = models.CharField(max_length=MAX_CHAR_LENGTH)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)    
    max_comments = models.IntegerField(default=100)
    weather_data = models.CharField(max_length=MAX_CHAR_LENGTH)
    slug = models.SlugField(unique=True)
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.location)
        super(Forum, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Forums'
    
    def __str__(self):
        return self.location.name
    
class Comment(models.Model):
    username = models.CharField(max_length=MAX_CHAR_LENGTH)

    # If the forum is deleted, the comments will be deleted form the db. as well.
    forum = models.ForeignKey(Forum, on_delete=models.CASCADE)
    user_id = models.IntegerField(null=True,blank=True)
    text = models.CharField(max_length=MAX_REVIEW_LENGTH, null=True, blank=True)
    slug = models.SlugField()
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.text)
        super(Comment, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Comments'
    
    def __str__(self):
        return self.text
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    picture = models.ImageField(upload_to='profile_images', blank=True)
    saved_locations = JSONField(default=list, blank=True)  # Store URLs as a list

    def __str__(self):
        return self.user.username
    
    def get_urls(self):
        return json.loads(self.saved_locations)
    
    def set_urls(self, url_list):
        self.urls = json.dumps(url_list)
        self.save()
    