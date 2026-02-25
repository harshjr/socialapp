"""
admin.py — Register models with Django's admin interface.

Django Concept: Admin customization
- list_display: columns shown in the list view
- list_filter: sidebar filters
- search_fields: enables search box
- raw_id_fields: better UI for ForeignKey fields with many options
- readonly_fields: show computed/auto fields
- inlines: show related models inline
"""

from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Post, Comment, Like, UserProfile, Notification


class UserProfileInline(admin.StackedInline):
    """Show UserProfile inline within the User admin page."""
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


class CustomUserAdmin(BaseUserAdmin):
    """Extend default UserAdmin to include the profile inline."""
    inlines = [UserProfileInline]
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined']


# Re-register User with our custom admin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'location', 'website', 'created_at']
    search_fields = ['user__username', 'bio', 'location']
    readonly_fields = ['created_at']


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'post_type', 'content_preview', 'like_count', 'comment_count', 'created_at']
    list_filter = ['post_type', 'created_at']
    search_fields = ['content', 'author__username']
    readonly_fields = ['created_at', 'updated_at', 'post_type']
    raw_id_fields = ['author']
    date_hierarchy = 'created_at'

    def content_preview(self, obj):
        return obj.content[:60] + '...' if len(obj.content) > 60 else obj.content
    content_preview.short_description = 'Content'

    def like_count(self, obj):
        return obj.likes.count()
    like_count.short_description = 'Likes'

    def comment_count(self, obj):
        return obj.comments.count()
    comment_count.short_description = 'Comments'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'post', 'content_preview', 'created_at']
    search_fields = ['content', 'author__username']
    raw_id_fields = ['post', 'author']

    def content_preview(self, obj):
        return obj.content[:60]
    content_preview.short_description = 'Content'


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'created_at']
    raw_id_fields = ['post', 'user']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'sender', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read']
    raw_id_fields = ['recipient', 'sender', 'post']
