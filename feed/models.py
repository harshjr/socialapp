"""
models.py — Core data models for SocialApp.

Django Concepts Demonstrated:
- Model inheritance (AbstractUser extension via UserProfile)
- OneToOneField, ForeignKey, ManyToManyField relationships
- ImageField for file uploads (stored locally; swap to S3 in production)
- Model Meta options (ordering, verbose names)
- __str__ methods for readable admin/shell representation
- Custom model methods
- Django signals (post_save) to auto-create UserProfile

AWS S3 Migration Note:
    To switch from local storage to S3, install django-storages and boto3,
    then in settings.py set:
        DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
        AWS_STORAGE_BUCKET_NAME = 'your-bucket'
    ImageField will automatically use S3 without changing model code.
"""

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class UserProfile(models.Model):
    """
    Extends Django's built-in User model via a OneToOneField.
    This is the recommended pattern ("Profile pattern") for adding
    extra user data without subclassing AbstractUser.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,        # If User deleted, Profile deleted too
        related_name='profile'           # Access via: user.profile
    )
    bio = models.TextField(max_length=300, blank=True, default='')
    avatar = models.ImageField(
        upload_to='avatars/',            # Stored in MEDIA_ROOT/avatars/
        blank=True,
        null=True
    )
    website = models.URLField(blank=True, default='')
    location = models.CharField(max_length=100, blank=True, default='')
    followers = models.ManyToManyField(
        'self',
        symmetrical=False,               # A follows B ≠ B follows A
        related_name='following',
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"@{self.user.username}"

    def follower_count(self):
        return self.followers.count()

    def following_count(self):
        return self.following.count()

    def post_count(self):
        return self.user.posts.count()


# --- Django Signal: Auto-create UserProfile when a new User is registered ---
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Signal receiver: fires after User.save(). Creates a profile automatically."""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Ensures profile is saved whenever the User object is saved."""
    if hasattr(instance, 'profile'):
        instance.profile.save()


class Post(models.Model):
    """
    A post can be a Tweet (text only), a Photo post, or both.
    Demonstrates:
    - ForeignKey (many posts → one user)
    - Optional ImageField
    - Model ordering via Meta
    - Custom properties
    """
    POST_TYPE_CHOICES = [
        ('tweet', 'Tweet'),
        ('photo', 'Photo'),
        ('mixed', 'Photo + Text'),
    ]

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,       # Delete posts if user is deleted
        related_name='posts'            # Access via: user.posts.all()
    )
    content = models.TextField(
        max_length=280,
        blank=True,
        default='',
        help_text="Text content (max 280 chars, like a tweet)"
    )
    image = models.ImageField(
        upload_to='posts/%Y/%m/%d/',    # Organized by date: posts/2024/01/15/
        blank=True,
        null=True,
        help_text="Optional image upload"
        # AWS NOTE: In production, this field automatically uploads to S3
        # when DEFAULT_FILE_STORAGE is set to S3Boto3Storage
    )
    post_type = models.CharField(
        max_length=10,
        choices=POST_TYPE_CHOICES,
        default='tweet'
    )
    created_at = models.DateTimeField(auto_now_add=True)  # Set once on creation
    updated_at = models.DateTimeField(auto_now=True)       # Updated on every save

    class Meta:
        ordering = ['-created_at']          # Newest posts first
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'

    def __str__(self):
        return f"{self.author.username}: {self.content[:50] or '[image]'}"

    def like_count(self):
        return self.likes.count()

    def comment_count(self):
        return self.comments.count()

    def save(self, *args, **kwargs):
        """Override save to auto-set post_type based on content/image."""
        if self.image and self.content:
            self.post_type = 'mixed'
        elif self.image:
            self.post_type = 'photo'
        else:
            self.post_type = 'tweet'
        super().save(*args, **kwargs)


class Comment(models.Model):
    """
    Comment on a post. Demonstrates nested ForeignKeys and
    how to structure threaded-style data.
    """
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'         # post.comments.all()
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    content = models.TextField(max_length=280)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']       # Oldest comments first (threaded feel)

    def __str__(self):
        return f"@{self.author.username} on Post #{self.post.id}: {self.content[:40]}"


class Like(models.Model):
    """
    Like/Unlike a post. Uses unique_together to prevent duplicate likes.
    Demonstrates constraint-level data integrity in Django.
    """
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')   # One like per user per post (DB-level)
        verbose_name = 'Like'

    def __str__(self):
        return f"@{self.user.username} liked Post #{self.post.id}"


class Notification(models.Model):
    """
    In-app notifications for likes, comments, follows.
    """
    NOTIFICATION_TYPES = [
        ('like', '❤️ Liked your post'),
        ('comment', '💬 Commented on your post'),
        ('follow', '👤 Started following you'),
    ]

    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_notifications'
    )
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for @{self.recipient.username} from @{self.sender.username}"
