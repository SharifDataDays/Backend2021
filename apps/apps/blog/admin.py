from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.db import models
from martor.widgets import AdminMartorWidget

from apps.blog.models import Post, Comment, Tag


@admin.register(Post)
class PostAdmin(ModelAdmin):
    list_display = ['title_fa', 'shown']
    list_editable = ['shown']
    formfield_overrides = {
        models.TextField: {'widget': AdminMartorWidget},
    }
    pass


@admin.register(Comment)
class CommentAdmin(ModelAdmin):
    comment_shown_editable = ['shown']
    formfield_overrides = {
        models.TextField: {'widget': AdminMartorWidget},
    }



@admin.register(Tag)
class TagAdmin(ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': AdminMartorWidget},
    }
    pass

