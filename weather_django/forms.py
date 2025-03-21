from django import forms
from weather_django.models import MAX_CHAR_LENGTH, UserProfile, Comment
from django.contrib.auth.models import User

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    
    class Meta:
        model = User 
        fields = ('username', 'password',)
        
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('picture',)
        
class CommentForm(forms.ModelForm):
    text = forms.CharField(max_length=MAX_CHAR_LENGTH, help_text="Please enter your comment.")
    #user_id = # get users id, pass in context dict? 
    
    class Meta:
        model = Comment
        exclude = ('forum',)