from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
MAX_CHAR_LENGTH = 128
MAX_REVIEW_LENGTH = 256
# Create your models here.


class Location(models.Model):
    name = models.CharField(max_length=MAX_CHAR_LENGTH)
    location_forum = models.URLField(blank=False)
    rating = models.IntegerField(default=0)
    weather_description = models.CharField(max_length=MAX_CHAR_LENGTH)
    slug = models.SlugField(unique=True)
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Location, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Locations'
    
    def __str__(self):
        return self.name
    
class Forum(models.Model):
    locationName = models.CharField(max_length=MAX_CHAR_LENGTH)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)    
    max_comments = models.IntegerField(default=0)
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
    
    def __str__(self):
        return self.user.username