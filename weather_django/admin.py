from django.contrib import admin

# Register your models here.

from weather_django.models import Location, Forum, Comment, UserProfile, Rating

class CommentAdmin(admin.ModelAdmin):
    list_display = ('forum', 'user_id', 'username','text')

class ForumAdmin(admin.ModelAdmin):
    list_display = ('location', 'max_comments', 'weather_data')
    
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'location_forum', 'total_rating','people_voted', 'weather_description')

class RatingAdmin(admin.ModelAdmin):
    list_display = ('location', 'user', 'rating_value', 'date_rated')
    
admin.site.register(Location, LocationAdmin)
admin.site.register(Forum, ForumAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(UserProfile)
admin.site.register(Rating, RatingAdmin)