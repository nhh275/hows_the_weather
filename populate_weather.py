import os 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hows_the_weather.settings')

import django
django.setup()
from weather_django.models import Location, Forum, Comment, SavedLocationsList

def populate():
    Comment.objects.all().delete()
    Forum.objects.all().delete()
    Location.objects.all().delete()
    SavedLocationsList.objects.all().delete()
    
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