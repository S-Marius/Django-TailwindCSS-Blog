# utils.py

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.models import User

def send_new_post_email():
    subject = 'New Blog Post Alert'
    message = render_to_string('other/new_post_notification_email.html', {
        'site': get_current_site(None),
    })
    from_email = 'noreply@example.com'
    recipient_list = [user.email for user in User.objects.all()]  # Assuming you have a User model
    
    send_mail(subject, message, from_email, recipient_list, html_message=message)
