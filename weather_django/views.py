from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse
from weather_django.models import Location, Forum, UserProfile, Comment
from weather_django.forms import UserForm, UserProfileForm
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


# Create your views here.
def index(request):
    return redirect('/hows-the-weather/home/')

def home(request):
    liked_locations = Location.objects.order_by('-rating')[:3]

    context_dict = {}
    context_dict['liked_locations'] = liked_locations

    response = render(request, 'hows_the_weather/home.html', context=context_dict)

    # return HttpResponse("Home Page <a href='/hows-the-weather/my-weather/'>Test</a>")
    return response

def my_weather(request):
    return HttpResponse("My Weather Page")

def my_profile(request):
    context_dict = {}
    context_dict['profile'] = None
    if request.user.is_authenticated:
        context_dict['profile'] = UserProfile.objects.filter(user=request.user).first()
    response = render(request, 'hows_the_weather/user_profile.html', context=context_dict)
    return response

def browse(request):
    # We could separate liked_locations out of both browse and home so both
    # pull from the same variable (for the day)
    liked_locations = Location.objects.order_by('-rating')[:3]

    context_dict = {}
    context_dict['liked_locations'] = liked_locations

    response = render(request, 'hows_the_weather/browse.html', context=context_dict)
    return response

def location(request, location_name_slug):
    context_dict = {}
    location = Location.objects.get(slug=location_name_slug)

    context_dict['location'] = location

    response = render(request, 'hows_the_weather/location.html', context=context_dict)
    return response

def forum(request, location_name_slug):
    context_dict = {}

    forum_used = Forum.objects.get(slug=location_name_slug)

    comments = Comment.objects.filter(forum=forum_used)

    context_dict['location'] = forum_used.location.name
    context_dict['comments'] = comments

    response = render(request, 'hows_the_weather/forum.html', context=context_dict)
    return response

def saved_locations(request):
    response = render(request, 'hows_the_weather/saved_locations.html')
    return response

def register(request):
    registered = False
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            
            profile = profile_form.save(commit=False)
            profile.user = user
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
            
            profile.save()
            registered = True
        else:
            print(user_form.errors(), profile_form.errors())
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
    
    response = render(request, 'hows_the_weather/register.html', context={'user_form':user_form,
                                                                      'profile_form':profile_form,
                                                                      'registered':registered})
    return response

def user_login(request):
    if request.method=='POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username,password=password)
        
        if user:
            if user.is_active:
                login(request, user)
                return redirect(reverse('hows_the_weather:home'))
            else:
                return HttpResponse("Your Weather account is disabled.")
        else:
            print(f"Invalid login details: {username}, {password}")
            return HttpResponse("Invalid login details supplied.")
    else:
        return render(request, 'hows_the_weather/login.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect(reverse('hows_the_weather:home'))
