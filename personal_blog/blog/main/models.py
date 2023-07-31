from django.db import models
from django.contrib.auth.models import User
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill
from django.core.validators import MinLengthValidator
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from taggit.managers import TaggableManager
import uuid

class BlogPost(models.Model):
    title = models.CharField(max_length=30, validators=[MinLengthValidator(5)])
    content = models.TextField(max_length=2500, validators=[MinLengthValidator(100)])
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    slug = models.SlugField(unique=True, editable=False)
    tags = TaggableManager(blank=True)

    thumbnail = ProcessedImageField(
        upload_to='thumbnails/',
        processors=[ResizeToFill(1280, 720)],
        format='JPEG',
        options={'quality': 100},
        default='thumbnails/default_thumbnail.jpg',
        null=True,   # Allow the field to be empty (null)
        blank=True,  # Allow the field to be empty (blank)
    )

    # Overwrite of the default save function
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = str(uuid.uuid4())  # Generate a new UUID for the slug
        super(BlogPost, self).save(*args, **kwargs) # First we are creating and adding the slug to itself if it doesn't exist, then we use the default save function provided by Django.

    def delete(self, *args, **kwargs):
        # Delete the associated thumbnail image if it exists
        if self.thumbnail:
            self.thumbnail.delete()
        super(BlogPost, self).delete(*args, **kwargs)

    def __str__(self):
        return self.title
    
@receiver(pre_delete, sender=BlogPost)
def delete_thumbnail_on_blogpost_delete(sender, instance, **kwargs):
    # Check if the thumbnail exists and is not the default thumbnail
    if instance.thumbnail and instance.thumbnail.name != BlogPost._meta.get_field('thumbnail').get_default():
        # Delete the associated thumbnail image if it exists and is not the default thumbnail
        instance.thumbnail.delete(False)

        # the 'False' argument of the .delete function is not what you might expect. In fact, this is what it does:
        # The argument False is passed to the delete() method to indicate that the model instance should not be saved after the thumbnail deletion.
