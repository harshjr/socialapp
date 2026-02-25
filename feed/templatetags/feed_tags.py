"""
templatetags/feed_tags.py — Custom template tags and filters.

Django Concept: Template tags extend the template engine.
Usage in templates: {% load feed_tags %}
"""
from django import template
from django.utils.timesince import timesince
from django.utils import timezone

register = template.Library()


@register.filter
def time_ago(value):
    """Returns human-readable time like '2 hours ago'."""
    if not value:
        return ''
    now = timezone.now()
    diff = now - value
    if diff.days == 0 and diff.seconds < 60:
        return 'just now'
    return timesince(value) + ' ago'


@register.filter
def is_liked_by(post, user):
    """Check if a post is liked by the given user. Usage: {{ post|is_liked_by:user }}"""
    return post.likes.filter(user=user).exists()


@register.simple_tag
def get_notification_count(user):
    """Returns unread notification count. Usage: {% get_notification_count user %}"""
    return user.notifications.filter(is_read=False).count()


@register.filter
def format_count(value):
    """Format large numbers: 1200 → 1.2K"""
    try:
        value = int(value)
        if value >= 1_000_000:
            return f"{value/1_000_000:.1f}M"
        elif value >= 1_000:
            return f"{value/1_000:.1f}K"
        return str(value)
    except (ValueError, TypeError):
        return value
