from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm
import random

class SignupForm(UserCreationForm):
    email = forms.EmailField()
    photo = forms.ImageField(required=False, label='Profile Picture', help_text='Upload a profile picture')
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'photo']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            profile = UserProfile(user=user, photo=self.cleaned_data['photo'])
            profile.save()
        return user
        
class EmailPostForm(forms.Form):
    to = forms.EmailField()
    comments = forms.CharField(required=False, widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(EmailPostForm, self).__init__(*args, **kwargs)
        
        if user:
            self.fields['name'] = forms.CharField(max_length=25, initial=user.username)
            self.fields['email'] = forms.EmailField(initial=user.email)
        else:
            self.fields['name'] = forms.CharField(max_length=25)
            self.fields['email'] = forms.EmailField()

class CommentForm(forms.ModelForm):
    
    class Meta:
        model = Comment
        fields = ['body']

class EditProfileForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = UserProfile
        fields = ['username', 'email', 'password', 'photo']
        exclude = ['user', 'rate']

class PostForm(forms.ModelForm):
    body = forms.CharField(label='', widget=forms.Textarea)

    class Meta:
        model = Post
        fields = ['body']

    def save(self, commit=True):
        post = super().save(commit=False)
        post.title = ' '.join(self.cleaned_data['body'].split()[:2])
        post.slug = '-'.join(self.cleaned_data['body'].split()[:2])

        if commit:
            post.save()

        # Generate random tags from words in the post body
        words = self.cleaned_data['body'].split()
        tags = random.sample(words, min(3, len(words)))  # Generate up to 3 random tags

        # Check if the post has been saved and has a primary key value
        if post.pk:
            post.tags.set(*tags)  # Set the generated tags for the post

        return post
    
    
    
    
    
    