from django import forms
from .models import Comment
from .models import BlogPost
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth import get_user_model



class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text='Required. Enter a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


# ModelForm
class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ['title', 'content', 'thumbnail', 'tags', 'status']

# Form
class EmailPostForm(forms.Form):
    name = forms.CharField(max_length=150, label="Your Name:")
    email = forms.EmailField(label="Your Email: ")
    to = forms.EmailField(label="Email sent to:")
    comments = forms.CharField(required=False,
    widget=forms.Textarea, label="Comments:")

class CommentForm(forms.Form):
    body = forms.CharField(max_length=1000, label="")


class PasswordResetForm(forms.Form):
    email = forms.EmailField(label='Email')