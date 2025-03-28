import json
from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse, JsonResponse
import pandas as pd
from weather_django.models import Location, Forum, UserProfile, Comment, Rating
from weather_django.forms import UserForm, UserProfileForm, CommentForm
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import requests
from django.utils.timezone import now
from datetime import date
from django.contrib import messages
from django.template.defaultfilters import slugify
from django.db.models import F
import os
from dotenv import load_dotenv
load_dotenv()
import geocoder

def search_function_algorithm(search_input):
    formatted_input = slugify(search_input)
    locations = Location.objects.all()

    returned_locations = []

    for location in locations:
        if locations.name.lower().startswith(formatted_input):
            returned_locations.append(location)
        continue

    return returned_locations

def get_ip(request):
    if not request.session.get("ip_grabbed", False):  # Check if already grabbed
        public_ip = requests.get("https://api64.ipify.org").text  # Get public IP
        df = pd.DataFrame({'ip': [public_ip]})
        df['city'] = df['ip'].apply(lambda x: geocoder.ip(x).city)
        city_name = df['city'].iloc[0] if not df['city'].isnull().iloc[0] else "Unknown"  # Handle missing data
        
        # Store the flag and city in session
        request.session["ip_grabbed"] = True
        request.session["user_city"] = city_name
    else:
        city_name = request.session.get("user_city", "Unknown")  # Retrieve stored city

    return JsonResponse({"city": city_name})  # Return JSON response

# Create your views here.
def index(request):
    return redirect('/hows-the-weather/home/')

async def asynchronous_view_test(request):
    return HttpResponse("Async Test")

def get_top_three_locations_of_the_day():
    return Location.objects.annotate(rating_per_person=F('total_rating') / F('people_voted')).order_by('-rating_per_person')[:3]

def home(request):
    context_dict = {}

    liked_locations = get_top_three_locations_of_the_day()
    context_dict['liked_locations'] = liked_locations
    # context_dict['weather'] = weather


    response = render(request, 'hows_the_weather/home.html', context=context_dict)
    return response

def my_profile(request):
    context_dict = {}
    if not request.session.get("ip_grabbed", False):  # First-time check
        response = get_ip(request)  # Call get_ip
        location_name = response.content  # Raw JSON bytes
        location_name = json.loads(location_name.decode("utf-8"))["city"]  # Decode JSON
    else:
        location_name = request.session.get("user_city", "Unknown")  # Get from session

    # Change it such that the location refers to a specific location rather than getting
    # The first location with the same name.
    location_object = Location.objects.get(name=location_name)

    context_dict['location'] = location_object 

    context_dict['profile'] = None
    if request.user.is_authenticated:
        context_dict['profile'] = UserProfile.objects.filter(user=request.user).first()
    response = render(request, 'hows_the_weather/user_profile.html', context=context_dict)
    return response

def browse(request):
    liked_locations = get_top_three_locations_of_the_day()
    context_dict = {}
    context_dict['liked_locations'] = liked_locations

    query = request.GET.get('searchbox')
    if query:
        context_dict['search_query'] = slugify(query)
        
        results = Location.objects.filter(name__icontains=query)
        
        if not results:
            api_key = os.getenv("API_KEY")
            url = f"https://api.openweathermap.org/data/2.5/find?q={query}&appid={api_key}&units=metric"
            response = requests.get(url)
            
            if response.status_code == 200:
                json_data = response.json()
                locations_from_api = json_data['list']
                
                for loc in locations_from_api:
                    location_name = loc['name']
                    if not Location.objects.filter(name=location_name).exists():
                        Location.objects.create(
                            name=location_name,
                            weather_description=loc['weather'][0]['description'],
                            slug=slugify(location_name),
                        )
                
                results = Location.objects.filter(name__icontains=query)
        
        context_dict['results'] = results
    else:
        context_dict['search_query'] = None
        context_dict['results'] = None

    response = render(request, 'hows_the_weather/browse.html', context=context_dict)
    return response

def location(request, location_name_slug):
    context_dict = {}
    if not request.session.get("ip_grabbed", False):  # First-time check
        response = get_ip(request)  # Call get_ip
        location_name = response.content  # Raw JSON bytes
        location_name = json.loads(location_name.decode("utf-8"))["city"]  # Decode JSON
    else:
        location_name = request.session.get("user_city", "Unknown")  # Get from session
    context_dict['user_city'] = location_name

    try:
        location = Location.objects.get(slug=location_name_slug)
    except Location.DoesNotExist:
        location = None 
        context_dict['location'] = location
        context_dict['json_data'] = {}
        return render(request, 'hows_the_weather/location.html', context=context_dict)

    
    context_dict['is_users_city'] = context_dict['user_city']==location.name

    forum, created = Forum.objects.get_or_create(location=location, locationName=location.name)
    if location.people_voted > 0:
        context_dict['avg_rating'] = round(location.total_rating / location.people_voted, 2)
    else:
        context_dict['avg_rating'] = 0
    my_key = os.getenv("API_KEY")
    url = f"https://api.openweathermap.org/data/2.5/weather?q={location.name}&appid={my_key}&mode=json&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        json_data = response.json()
    else:
        json_data = {}

    if request.user.is_authenticated:
        is_saved = False
        user = UserProfile.objects.filter(user=request.user).first()
        saved = user.saved_locations

        for saved_location in saved:
            if saved_location['name'] == location.name:
                is_saved = True
                break
    else:
        is_saved = False

    context_dict['is_in_saved_locations'] = is_saved
    context_dict['location'] = location
    context_dict['json_data'] = json_data
   
    show_form = True  # default showing the form
    if request.user.is_authenticated:
        last_rating = Rating.objects.filter(user=request.user, location=location, date_rated=date.today()).exists()
        if last_rating:
            show_form = False  # hide if the user has rated it today
    if not request.user.is_authenticated:
        show_form = False
    context_dict['show_form'] = show_form
    # POST request handling
    if request.method == 'POST':            
        if request.POST['action'] == 'Save Location':
            if not is_saved:
                add_location(request, location_name_slug=location_name_slug)
                messages.warning(request, message="Saved the location.")
            return redirect(request.path)  # Redirect to same page to prevent resubmission

        elif request.POST['action'] == 'Rate':
            if request.POST.get("rating"):
                rating_value = int(request.POST.get("rating"))
                # Check if a rating entry exists for this user, location, and today's date
                rating_entry, created = Rating.objects.get_or_create(
                    user=request.user, location=location, date_rated=date.today(),
                    defaults={'rating_value': rating_value}  # Set default value if creating a new entry
                )

                if not created:
                    # If the entry already exists, update the rating value
                    rating_entry.rating_value = rating_value
                    rating_entry.save()
                location.total_rating += rating_value
                location.people_voted += 1
                location.save()
                show_form = False

                messages.success(request, "Thank you for rating!")
                show_form = False
            else:
                messages.error(request, message="Please select a rating before submitting.")
                show_form = True

            return redirect(request.path)  # Redirect to same page to prevent resubmission

    response = render(request, 'hows_the_weather/location.html', context=context_dict)
    return response

def forum(request, location_name_slug):
    context_dict = {}
    
    if not request.session.get("ip_grabbed", False):  # First-time check
        response = get_ip(request)  # Call get_ip
        location_name = response.content  # Raw JSON bytes
        location_name = json.loads(location_name.decode("utf-8"))["city"]  # Decode JSON
    else:
        location_name = request.session.get("user_city", "Unknown")  # Get from session
    context_dict['current_location'] = location_name
    
    try:
        forum_used = Forum.objects.get(slug=location_name_slug)
        comments = Comment.objects.filter(forum=forum_used)
        
        context_dict['forum'] = forum_used  
        context_dict['location'] = forum_used.location
        context_dict['is_users_location'] = context_dict['current_location']==context_dict['location'].name
        context_dict['comments'] = comments
    except Forum.DoesNotExist:
        forum_used = None  
        context_dict['forum'] = None
        context_dict['comments'] = None   
             
    response = render(request, 'hows_the_weather/forum.html', context=context_dict)
    return response

def saved_locations(request):
    saved = None 
    if request.user.is_authenticated:
        user = UserProfile.objects.filter(user=request.user).first()
        saved = user.saved_locations

    context_dict = {}
    context_dict['saved_locations'] = saved

    if request.method == 'POST':
        print("POST OK")

        location_name = request.POST.get('location_name')

        if location_name:
            print(location_name)
            delete_location(request, location_name=location_name)

    response = render(request, 'hows_the_weather/saved_locations.html', context=context_dict)
    return response

def register(request):
    registered = False
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            username = user_form.cleaned_data['username']
            if User.objects.filter(username=username).exists() == False:

                user = user_form.save()
                user.set_password(user.password)
                user.save()
                
                profile = profile_form.save(commit=False)
                profile.user = user
                profile.saved_locations = []

                if 'picture' in request.FILES:
                    profile.picture = request.FILES['picture']
                
                profile.save()
                registered = True
                login(request, authenticate(username=username,password=user_form.cleaned_data['password']))
        else:
            print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
    
    response = render(request, 'hows_the_weather/register.html', context={'user_form':user_form,
                                                                      'profile_form':profile_form,
                                                                      'registered':registered,
                                                                      })
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
            return redirect(reverse('hows_the_weather:home'))

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


# Function for adding a location.
def add_location(request, location_name_slug):
    try:
        location = Location.objects.get(slug=location_name_slug)
        url = reverse("hows_the_weather:location", kwargs={'location_name_slug': location_name_slug})
    except Location.DoesNotExist:
        location = None
        url = None
    
    if location is None:
        return redirect('/weather_django/')
    
    if request.user.is_authenticated:
        if request.method == 'POST':
            user = UserProfile.objects.filter(user=request.user).first()
            
            city = {'name': location.name,
                    'url': url,}
            if city not in user.saved_locations:
                user.saved_locations.append(city)
                user.save()
    
    context_dict = {}
    context_dict['location'] = location
    context_dict['profile'] = UserProfile.objects.filter(user=request.user).first() if request.user.is_authenticated else None
    return render(request, 'hows_the_weather/home.html', context=context_dict)

def delete_location(request, location_name):
    try:
        #print("ONE")
        location = Location.objects.get(name=location_name)
        location_name_slug = location.slug
        url = reverse("hows_the_weather:location", kwargs={'location_name_slug': location_name_slug})
    except Location.DoesNotExist:
        #print("TWO")

        location = None
        url = None

    if request.user.is_authenticated:
        #print("THREE")

        if request.method == 'POST':
            #print("FOUR")

            user = UserProfile.objects.filter(user=request.user).first()

            for location in user.saved_locations:
                #print(location['url'] == url, location, " FIVE")
                if location['url'] == url:
                    user.saved_locations.remove(location)
                    #print("REMOVED SIX")
                    break
            
            user.save()