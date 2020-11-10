from django.contrib import admin

# Register your models here.
from posts.models import Post


class PostModelAdmin(admin.ModelAdmin):
    list_display = ["title", "image", "last_updated", "timestamp"]
    list_display_links = ["last_updated"]
    list_filter = ["title", "last_updated", "timestamp"]
    list_editable = ["title"]
    search_fields = ["title", "content"]

    class Meta:
        model = Post


admin.site.register(Post, PostModelAdmin)
