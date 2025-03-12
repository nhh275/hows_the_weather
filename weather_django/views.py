from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse
import weather_django.models# import Location, Forum, UserProfile, Comment
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime

# Create your views here.
def index(request):
    return redirect('/hows-the-weather/home/')

def home(request):
    response = render(request, 'hows_the_weather/home.html')
    # return HttpResponse("Home Page <a href='/hows-the-weather/my-weather/'>Test</a>")
    return response

def my_weather(request):
    return HttpResponse("My Weather Page")

def my_profile(request):
    response = render(request, 'hows_the_weather/user_profile.html')
    return response

def browse(request):
    return HttpResponse("Browse Tab")

def saved_locations(request):
    response = render(request, 'hows_the_weather/saved_locations.html')
    return response

