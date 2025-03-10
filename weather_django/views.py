from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse

# Create your views here.
def index(request):
    return redirect('/hows-the-weather/home/')

def home(request):
    return HttpResponse("Home Page <a href='/hows-the-weather/my-weather/'>Test</a>")

def my_weather(request):
    return HttpResponse("My Weather Page")