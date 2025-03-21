from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse
from weather_django.models import Location, Forum, UserProfile, Comment
from weather_django.forms import UserForm, UserProfileForm, CommentForm
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

    try:
        forum_used = Forum.objects.get(slug=location_name_slug)
        comments = Comment.objects.filter(forum=forum_used)
        
        context_dict['forum'] = forum_used  
        context_dict['location'] = forum_used.location.name
        context_dict['comments'] = comments
    except Forum.DoesNotExist:
        forum_used = None  
        context_dict['forum'] = None
        context_dict['comments'] = None   
             
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

@login_required
def add_comment(request, location_name_slug):
    try:
        forum = Forum.objects.get(slug=location_name_slug)
    except Forum.DoesNotExist:
        forum = None
    
    if forum is None:
        return redirect('/weather_django/')
    
    print("Form 0")

    form = CommentForm()
    if request.method == 'POST':
        print("Form 1")

        form = CommentForm(request.POST)
        if form.is_valid():
            print("Form valid")
            #if forum:
            comment = form.save(commit=False)
            comment.forum = forum
            comment.user_id = request.user.id
            comment.username = request.user.username
            comment.save()
                
            return redirect(reverse('weather_django:forum',kwargs={'location_name_slug':location_name_slug}))
        else:
            print(form.errors)
    
    context_dict = {'form': form, 'forum': forum}
    context_dict['profile'] = UserProfile.objects.filter(user=request.user).first() if request.user.is_authenticated else None
    return render(request, 'hows_the_weather/add_comment.html', context=context_dict)