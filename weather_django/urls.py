from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.urls import include
from weather_django import views
from weather_django.views import asynchronous_view_test

import asyncio 
import os

app_name = 'hows_the_weather'

#/<slug:location_name_slug>/ should be used for the location name

urlpatterns = [
    path('', views.index, name='index'),
    path('test/', asynchronous_view_test, name='test'),
    path('home/', views.home, name='home'),
    path('my-weather/', views.my_weather, name='my-weather'),
    path('my-profile/', views.my_profile, name='my-profile'),
    path('my-profile/saved/', views.saved_locations, name='saved-locations'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('browse/', views.browse, name='browse'),
    path('logout/', views.user_logout, name='logout'),

    # Unless we can implement the logout function inside of the text itself, this 
    # HAS to be last in the list.
    path('<slug:location_name_slug>/', views.location, name='location'),
    path('<slug:location_name_slug>/forum/', views.forum, name='forum'),


]