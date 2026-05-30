from django.contrib import admin
from .models import Post, Vote, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'score')
    search_fields = ('title', 'author__username')
    list_filter = ('created_at',)


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'value')
    list_filter = ('value',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'parent', 'created_at')
    search_fields = ('author__username', 'body')
    list_filter = ('created_at',)
