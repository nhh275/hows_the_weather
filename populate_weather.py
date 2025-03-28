import os 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hows_the_weather.settings')

import django
django.setup()
from weather_django.models import Location, Forum, Comment, User
from django.db import connection

def populate():
    Comment.objects.all().delete()
    Forum.objects.all().delete()
    Location.objects.all().delete()
    superuser = User.objects.filter(is_superuser=True).first()

    # Step 2: Delete all users except the superuser
    User.objects.exclude(is_superuser=True).delete()

    if superuser and superuser.id != 1:
        # Step 3: Store superuser data, delete it, then recreate with ID 1
        superuser_data = {
            "username": superuser.username,
            "email": superuser.email,
            "password": superuser.password,  # Keep hashed password
            "is_superuser": True,
            "is_staff": superuser.is_staff,
        }
        
        superuser.delete()  # Delete the existing superuser

        # Reset SQLite sequence (needed to ensure next ID is 1)
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'auth_user';")

        # Step 4: Recreate the superuser with ID=1
        new_superuser = User.objects.create(**superuser_data)
        new_superuser.id = 1
        new_superuser.save()

    # Step 5: Ensure new users start from ID 2
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'auth_user';")
    
    forumVars = [
        {'max_comments':100,
        'weather_data':'string'},
        {'max_comments':100,
        'weather_data':'string'},
        {'max_comments':100,
        'weather_data':'string'}, ]
    
    comments = [
        [ # list of comments per forum
        {'username':'weatherFan1',
        'user_id':1,
        'text': 'I love the weather here!'},
        {'username':'weatherHater2',
        'user_id':3,
        'text': 'I want to leave...'},
        ],
        [
        {'username':'weatherhater3',
        'user_id':2,
        'text': 'It is miserable out today'}, 
        ]
        ]
    
    
    locations = {'York': {'location_forum': forumVars,'rating': 5, 'weather_description': 'string'},
            'Madrid': {'location_forum': forumVars,'rating': 7, 'weather_description': 'string'},
            'Amsterdam': {'location_forum': forumVars,'rating': 2, 'weather_description': 'string'} }

    for cat, cat_data in locations.items():
        c = add_cat(cat)
        for p in cat_data['location_forum']:
            add_forum(c, p['max_comments'], p['weather_data'], f'{c}')
        c.rating, c.weather_description = cat_data['rating'], cat_data['weather_description']
        c.save()
    
    
    for c in Location.objects.all():
        for p in Forum.objects.filter(location=c):
            print(f'- {c}: Location created')
    print()
    
    
    forums = {'York': {'comments': comments[0],'max_comments':100,'weather_data':'string'},
            'Madrid': {'comments': comments[1],'max_comments':100,'weather_data':'string'},
            'Amsterdam': {'comments': {},'max_comments':100,'weather_data':'string'} }

    for cat, cat_data in forums.items():
        c = add_forum2(cat)
        for idx,p in enumerate(cat_data['comments']):
            add_comment(c, p['username'], p['user_id'], p['text'], idx)
        c.max_comments, c.weather_data = cat_data['max_comments'], cat_data['weather_data']
        c.save()
    
    
    for c in Forum.objects.all():
        for p in Comment.objects.filter(forum=c):
            print(f'- {c}: {p}')
            



def add_comment(cat, name, id, text, idx):
    p = Comment.objects.create(forum=cat, username=name, user_id=id, text=text)    
    p.save()
    return p
    
def add_forum2(name):
    c = Forum.objects.get_or_create(locationName=name)[0]
    c.save()
    return c


def add_forum(cat, comms, data, locName):
    p = Forum.objects.get_or_create(location=cat)[0]
    p.max_comments = comms
    p.weather_data = data
    p.locationName = locName
    p.save()
    return p
    
def add_cat(name):
    c = Location.objects.get_or_create(name=name)[0]
    c.save()
    return c

if __name__ == '__main__':
    print("Starting Weather population script...")
    populate()