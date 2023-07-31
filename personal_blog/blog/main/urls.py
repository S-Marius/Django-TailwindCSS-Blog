# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('posts/<slug:slug>/', views.blog_post, name='blog_post'),
    path('', views.main_page, name='main_page'),
    path('create_blog/', views.create_blog_view, name='create_blog'),
]
