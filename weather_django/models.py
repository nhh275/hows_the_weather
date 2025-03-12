from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
maxCharLength = 128
maxReviewLength = 256
# Create your models here.


class Location(models.Model):
    name = models.CharField(max_length=maxCharLength)
    forum = models.URLField(blank=False)
    rating = models.IntegerField(default=0)
    weather_description = models.CharField(max_length=maxCharLength)
    slug = models.SlugField(unique=True)
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Location, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Locations'
    
    def __str__(self):
        return self.name
    
class Forum(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    max_comments = models.IntegerField(default=0)
    weather_data = models.CharField(max_length=maxCharLength)
    slug = models.SlugField(unique=True)
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Location, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Forums'
    
    def __str__(self):
        return self.name
    
class Comment(models.Model):
    username = models.CharField(max_length=maxCharLength)
    forum = models.ForeignKey(Forum, on_delete=models.CASCADE)
    user_id = models.IntegerField()
    text = models.CharField(max_length=maxReviewLength, unique=True)
    slug = models.SlugField(unique=True)
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Location, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Comments'
    
    def __str__(self):
        return self.name
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    website = models.URLField(blank=True)
    picture = models.ImageField(upload_to='profile_images', blank=True)
    
    def __str__(self):
        return self.user.username