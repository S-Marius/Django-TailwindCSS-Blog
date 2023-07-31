from django.contrib import admin
from .models import BlogPost

# Register your models here.

# admin.site.register(BlogPost)
@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'get_tags', 'pub_date']

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('tags')

    def get_tags(self, obj):
        return ", ".join(o for o in obj.tags.names())