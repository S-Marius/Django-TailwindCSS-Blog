from django.db import models
from django.contrib.auth.models import User
from django.db.models.query import QuerySet
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill
from django.core.validators import MinLengthValidator
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.urls import reverse
from django.utils.text import slugify

from taggit.managers import TaggableManager
import uuid


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=BlogPost.Status.PUBLISHED)


class BlogPost(models.Model):
    # python manage.py sqlmigrate main 0001 (to display SqlLite code)
    class Status(models.TextChoices):
        DRAFT = 'DF', 'Draft'
        PUBLISHED = 'PB', 'Published'

    title = models.CharField(max_length=30, unique=True,
                             validators=[MinLengthValidator(5)])
    content = models.TextField(max_length=2500, validators=[
                               MinLengthValidator(100)])
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='blog_posts')
    slug = models.SlugField(max_length=250, editable=False, unique=True)
    tags = TaggableManager(blank=True)
    status = models.CharField(
        max_length=2, choices=Status.choices, default=Status.DRAFT)

    objects = models.Manager()  # Default manager
    # Custom manager for only PUBLISHED STATUS blog posts.
    published = PublishedManager()

    thumbnail = ProcessedImageField(
        upload_to='thumbnails/',
        processors=[ResizeToFill(1280, 720)],
        format='JPEG',
        options={'quality': 100},
        default='thumbnails/default_thumbnail.jpg',
        null=True,   # Allow the field to be empty (null)
        blank=True,  # Allow the field to be empty (blank)
    )

    class Meta:
        ordering = ['-pub_date']
        indexes = [
            models.Index(fields=['-pub_date'])
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        super(BlogPost, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Delete the associated thumbnail image if it exists
        if self.thumbnail:
            self.thumbnail.delete()
        super(BlogPost, self).delete(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        # return reverse('blog_post', kwargs={'slug': self.slug})
        return reverse('blog_post', args=[self.pub_date.year, self.pub_date.month, self.pub_date.day, self.slug])


@receiver(pre_delete, sender=BlogPost)
def delete_thumbnail_on_blogpost_delete(sender, instance, **kwargs):
    # Check if the thumbnail exists and is not the default thumbnail
    if instance.thumbnail and instance.thumbnail.name != BlogPost._meta.get_field('thumbnail').get_default():
        # Delete the associated thumbnail image if it exists and is not the default thumbnail
        instance.thumbnail.delete(False)

        # the 'False' argument of the .delete function is not what you might expect. In fact, this is what it does:
        # The argument False is passed to the delete() method to indicate that the model instance should not be saved after the thumbnail deletion.


class Comment(models.Model):
    post = models.ForeignKey(BlogPost,
                             on_delete=models.CASCADE,
                             related_name='comments')
    name = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    display = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created']),
        ]

    def __str__(self):
        return f'Comment by {self.name} on {self.post}'
