# urls.py
from django.urls import path
from . import views

from django.contrib.sitemaps.views import sitemap
from .sitemaps import BlogSitemap

sitemaps = {
 'posts': BlogSitemap,
}

urlpatterns = [
    path('', views.main_page, name='main_page'),
    path('tag/<slug:tag_slug>/', views.main_page, name='post_list_by_tag'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('posts/<int:year>/<int:month>/<int:day>/<slug:post>/', views.blog_post, name='blog_post'),
    path('create_blog/', views.create_blog_view, name='create_blog'),
    path('<int:post_id>/share/', views.blogpost_share, name='blogpost_share'),
    path('<int:post_id>/comment/', views.post_comment, name='post_comment'),

    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),

    path('confirm_email/<str:uid>/<str:token>/', views.confirm_email, name='confirm_email'),
    path('email_confirmed/', views.email_confirmed, name='email_confirmed'),
    path('email_confirmation_error/', views.email_confirmation_error, name='email_confirmation_error'),
    path('reset-password/', views.password_reset_view, name='password_reset'),
    path('password-reset-done/', views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset-password/<str:uidb64>/<str:token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset-complete/', views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('send-new-post-notification/', views.send_new_post_notification, name='send_new_post_notification'),
]
