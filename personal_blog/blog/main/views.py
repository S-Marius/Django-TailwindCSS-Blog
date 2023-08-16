from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mail
from django.template.loader import render_to_string
from taggit.models import Tag
from django.db.models import Count
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from .forms import PasswordResetForm
from django.core.cache import cache
from django.views.decorators.cache import cache_page


from django.contrib.auth.models import User

from .models import BlogPost, Comment
from .forms import BlogPostForm, EmailPostForm, CommentForm, CustomUserCreationForm

# Create your views here.

def user_is_active(user):
    return user.is_authenticated and user.is_active

def main_page(request, tag_slug=None):
    blog_posts = BlogPost.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        blog_posts = blog_posts.filter(tags__in=[tag])

    paginator = Paginator(blog_posts, 3)  # Show 3 posts per page
    
    page_number = request.GET.get('page')

    # For example, when a user visits /main_page/, the page_number will be None, and the view will render the first page of blog posts. If the user visits /main_page/?page=2, the page_number will be '2', and the view will render the second page of blog posts. This way, users can navigate through different pages of blog posts using the 'page' parameter in the URL.

    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)


    return render(request, 'main_page.html', {'page_obj': page_obj, 'tag': tag})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('main_page')
    return render(request, 'other/login.html')

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # Create user instance but don't save yet
            user.is_active = False
            user.save()  # Save the user instance with is_active set to False

            activateEmail(request, user, form.cleaned_data.get('email'))

            # Generate confirmation token
            token = default_token_generator.make_token(user)

            # Send confirmation email
            current_site = get_current_site(request)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            confirmation_link = f"http://{current_site.domain}/confirm_email/{uid}/{token}/"
            message = f"Click the following link to confirm your email: {confirmation_link}"
            send_mail("Confirm Your Email", message, "noreply@example.com", [user.email])

            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'other/signup.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')

def blog_post(request, year, month, day, post):
    # Get the blog post using the slug
    post = get_object_or_404(BlogPost,
            status=BlogPost.Status.PUBLISHED,
            pub_date__year=year,
            pub_date__month=month,
            pub_date__day=day,
            slug=post)
    
    comments = post.comments.filter(display=True)

    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = BlogPost.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    # First we use ".annotate()" to count all the tags, and store that value in a variable called "same__tags", then we order that query set by the amount of same tags and publication date. (Both in descending order)
    similar_posts = similar_posts.annotate(same__tags=Count('tags')).order_by('-same__tags', '-pub_date')[:4]

    form = CommentForm()

    return render(request, 'blog_post/blog_post.html', {'post': post, 'comments': comments, 'form': form, 'similar_posts': similar_posts})


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
    return render(request, 'other/create_blog.html', {'form': form})

def blogpost_share(request, post_id):

    blog_post = get_object_or_404(BlogPost, id=post_id, status=BlogPost.Status.PUBLISHED)
    sent = False

    if request.method == "POST":
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            post_url = request.build_absolute_uri(blog_post.get_absolute_url())

            subject = f"{cd['name']} recommends you to read '{blog_post.title}'"
            
            email_content = render_to_string('email.html', {
                'name': cd['name'],
                'blog_post': blog_post,
                'post_url': post_url,
                'comments': cd['comments'],
            })

            # message = f"Read {blog_post.title} at {post_url}\n\n {cd['name']}\'s comments: {cd['comments']}"

            send_mail(
                subject,
                '',  # No text version of the email content
                'moldorat@gmail.com',
                [cd['to']],
                html_message=email_content,  # Set the rendered HTML content
            )

            sent = True
    else:
        form = EmailPostForm()

    return render(request, 'other/share.html', {'post': blog_post, 'form': form, 'sent': sent})


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id, status=BlogPost.Status.PUBLISHED)
    comment = None

    comments = post.comments.filter(display=True)
    
    if request.method == "POST":
        # A comment was posted
        form = CommentForm(data=request.POST)

        if form.is_valid():
            cd = form.cleaned_data
            comment = Comment(
                post=post,
                name=request.user,
                body=cd['body'],
                display=True,
            )
            comment.save()

    return render(request, 'blog_post/blog_post.html', {'post': post, 'form': form, 'comments': comments, 'comment': comment})

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.shortcuts import redirect

def activateEmail(request, user, to_email):
    messages.success(request, f'Dear {user}, please go to your email "{to_email}" inbox and confirm your account!')

def confirm_email(request, uid, token):
    try:
        uid = (urlsafe_base64_decode(uid))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        # You can redirect to a success page
        return redirect('email_confirmed')
    else:
        # Token is invalid or user not found
        return redirect('email_confirmation_error')

def email_confirmed(request):
    return render(request, 'other/confirm_email.html')

def email_confirmation_error(request):
    return render(request, 'other/email_confirmation_error.html')

def password_reset_view(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.get(email=email)

            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            current_site = get_current_site(request)
            reset_link = f"http://{current_site.domain}/reset-password/{uid}/{token}/"

            subject = "Reset Your Password"
            email_content = render_to_string('other/password_reset_email.html', {
                'user': user,
                'reset_link': reset_link,
            })

            send_mail(
                subject,
                '',
                'noreply@example.com',
                [email],
                html_message=email_content,
            )

            return redirect('password_reset_done')
    else:
        form = PasswordResetForm()
    return render(request, 'other/password_reset.html', {'form': form})

# views.py
from django.contrib.auth.views import PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'other/password_reset_done.html'

# views.py
from django.contrib.auth.views import PasswordResetConfirmView

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'other/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')  # Redirect to password reset complete

    # Optionally, you can override the form_valid method to customize behavior
    # def form_valid(self, form):
    #     # Your custom logic here
    #     return super().form_valid(form)


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'other/password_reset_complete.html'


from django.shortcuts import render
from django.contrib.auth.models import User
from .utils import send_new_post_email

def send_new_post_notification(request):
    send_new_post_email()

    return render(request, 'other/email_sent.html')