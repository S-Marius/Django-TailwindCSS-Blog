from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from .models import BlogPost
from .forms import BlogPostForm

# Create your views here.

def main_page(request):
    blog_posts = BlogPost.objects.all().order_by('-pub_date')
    paginator = Paginator(blog_posts, 6)  # Show 10 posts per page
    
    page_number = request.GET.get('page')

    # For example, when a user visits /main_page/, the page_number will be None, and the view will render the first page of blog posts. If the user visits /main_page/?page=2, the page_number will be '2', and the view will render the second page of blog posts. This way, users can navigate through different pages of blog posts using the 'page' parameter in the URL.

    page_obj = paginator.get_page(page_number)

    return render(request, 'main_page.html', {'page_obj': page_obj})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('main_page')
    return render(request, 'login.html')

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

def blog_post(request, slug):
    # Get the blog post using the slug
    post = get_object_or_404(BlogPost, slug=slug)
    return render(request, 'blog_post.html', {'post': post})

@login_required(login_url='/login/')
def create_blog_view(request):
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)  # Include request.FILES to handle file upload
        if form.is_valid():
            blog_post = form.save(commit=False)
            blog_post.author = request.user
            blog_post.save()
            # Without this next line the tags won't be saved.
            form.save_m2m()
            return redirect('main_page')
    else:
        form = BlogPostForm()
    return render(request, 'create_blog.html', {'form': form})
