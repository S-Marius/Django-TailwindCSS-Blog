from django.contrib import admin
from .models import BlogPost, Comment

# Register your models here.

# admin.site.register(BlogPost)
@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'get_tags', 'pub_date', 'status']
    list_filter = ['author', 'status', 'pub_date']
    search_fields = ['title', 'content']
    raw_id_fields = ['author'] # look up widged in admin panel
    date_hierarchy = 'pub_date'
    ordering = ['status', 'pub_date']

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('tags')

    def get_tags(self, obj):
        return ", ".join(o for o in obj.tags.names())
    

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['name', 'post', 'created', 'display']
    list_filter = ['display', 'created']
    search_fields = ['name', 'email', 'body']
