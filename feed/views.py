"""
views.py — All views for SocialApp.

Django Concepts Demonstrated:
- Function-based views (FBV) with @login_required decorator
- Class-based views (CBV): ListView, DetailView, UpdateView, DeleteView
- CRUD: Create (PostCreateView), Read (FeedView, PostDetailView),
         Update (PostUpdateView), Delete (PostDeleteView)
- Django ORM queries: filter(), select_related(), prefetch_related(),
                      get_or_create(), annotate(), Q objects
- HttpResponse, JsonResponse, redirect, render
- Django messages framework
- Pagination
- get_object_or_404 for safe lookups
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.generic import ListView, DetailView, UpdateView, DeleteView, CreateView
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from django.db.models import Q, Count, Prefetch
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST

from .models import Post, Comment, Like, UserProfile, Notification
from .forms import PostForm, CommentForm, ProfileEditForm, UserEditForm, RegisterForm, LoginForm


# ─── AUTH VIEWS ──────────────────────────────────────────────────────────────

def register_view(request):
    """Register a new user. On success, auto-login and redirect to feed."""
    if request.user.is_authenticated:
        return redirect('feed')

    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, f"Welcome to SocialApp, @{user.username}! 🎉")
        return redirect('feed')

    return render(request, 'feed/auth.html', {'form': form, 'mode': 'register'})


def login_view(request):
    """Login with Django's AuthenticationForm."""
    if request.user.is_authenticated:
        return redirect('feed')

    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        next_url = request.GET.get('next', 'feed')
        return redirect(next_url)
    elif request.method == 'POST':
        messages.error(request, "Invalid username or password.")

    return render(request, 'feed/auth.html', {'form': form, 'mode': 'login'})


@login_required
def logout_view(request):
    """Logout and redirect to login page."""
    logout(request)
    return redirect('login')


# ─── FEED VIEW ───────────────────────────────────────────────────────────────

@login_required
def feed_view(request):
    """
    Main feed: shows posts from users the current user follows + own posts.
    Demonstrates: ORM filtering with Q objects, select_related, prefetch_related.
    """
    # Get who the current user follows
    following_users = request.user.profile.following.values_list('user', flat=True)

    # Show posts from followed users + own posts
    posts = Post.objects.filter(
        Q(author__in=following_users) | Q(author=request.user)
    ).select_related(        # Avoids N+1: joins User and UserProfile in one query
        'author',
        'author__profile'
    ).prefetch_related(      # Efficiently prefetches related likes and comments
        'likes',
        'comments',
        'comments__author'
    ).order_by('-created_at')

    # Post creation form
    post_form = PostForm()
    if request.method == 'POST':
        post_form = PostForm(request.POST, request.FILES)
        if post_form.is_valid():
            post = post_form.save(commit=False)  # Don't save yet — set author first
            post.author = request.user
            post.save()
            messages.success(request, "Post created!")
            return redirect('feed')

    # Pagination: 10 posts per page
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Suggestions: users the current user doesn't follow yet
    suggested_users = UserProfile.objects.exclude(
        Q(user=request.user) | Q(followers=request.user.profile)
    ).annotate(
        follower_count=Count('followers')
    ).order_by('-follower_count')[:5]

    # Get IDs of posts the current user has liked (for UI toggle)
    liked_post_ids = Like.objects.filter(
        user=request.user
    ).values_list('post_id', flat=True)

    unread_notifs = request.user.notifications.filter(is_read=False).count()

    context = {
        'page_obj': page_obj,
        'post_form': post_form,
        'suggested_users': suggested_users,
        'liked_post_ids': set(liked_post_ids),
        'unread_notifs': unread_notifs,
    }
    return render(request, 'feed/feed.html', context)


# ─── POST CRUD ───────────────────────────────────────────────────────────────

@login_required
def post_detail_view(request, pk):
    """READ: View a single post with its comments."""
    post = get_object_or_404(
        Post.objects.select_related('author', 'author__profile'),
        pk=pk
    )
    comments = post.comments.select_related('author', 'author__profile').all()
    comment_form = CommentForm()

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            # Create notification for post author
            if post.author != request.user:
                Notification.objects.create(
                    recipient=post.author,
                    sender=request.user,
                    notification_type='comment',
                    post=post
                )
            return redirect('post_detail', pk=pk)

    liked = Like.objects.filter(post=post, user=request.user).exists()

    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'liked': liked,
    }
    return render(request, 'feed/post_detail.html', context)


@login_required
def post_edit_view(request, pk):
    """UPDATE: Edit own post (text content only; image can be changed)."""
    post = get_object_or_404(Post, pk=pk, author=request.user)  # 404 if not owner
    form = PostForm(request.POST or None, request.FILES or None, instance=post)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Post updated.")
        return redirect('post_detail', pk=pk)

    return render(request, 'feed/post_form.html', {'form': form, 'edit': True, 'post': post})


@login_required
def post_delete_view(request, pk):
    """DELETE: Remove own post with confirmation."""
    post = get_object_or_404(Post, pk=pk, author=request.user)

    if request.method == 'POST':
        post.delete()
        messages.success(request, "Post deleted.")
        return redirect('feed')

    return render(request, 'feed/post_confirm_delete.html', {'post': post})


# ─── LIKE (Toggle CRUD) ───────────────────────────────────────────────────────

@login_required
@require_POST
def toggle_like(request, pk):
    """
    Toggle like on a post. Uses get_or_create for atomic create/delete.
    Returns JSON for AJAX calls from the frontend.
    """
    post = get_object_or_404(Post, pk=pk)
    like, created = Like.objects.get_or_create(post=post, user=request.user)

    if not created:
        # Already liked — unlike it
        like.delete()
        liked = False
    else:
        liked = True
        # Create notification
        if post.author != request.user:
            Notification.objects.get_or_create(
                recipient=post.author,
                sender=request.user,
                notification_type='like',
                post=post
            )

    return JsonResponse({'liked': liked, 'count': post.like_count()})


# ─── PROFILE VIEWS ───────────────────────────────────────────────────────────

@login_required
def profile_view(request, username):
    """View any user's profile with their posts."""
    profile_user = get_object_or_404(User, username=username)
    profile = profile_user.profile
    posts = profile_user.posts.select_related('author').prefetch_related('likes', 'comments')

    is_following = request.user.profile.following.filter(user=profile_user).exists()
    is_own_profile = request.user == profile_user

    liked_post_ids = Like.objects.filter(
        user=request.user
    ).values_list('post_id', flat=True)

    context = {
        'profile_user': profile_user,
        'profile': profile,
        'posts': posts,
        'is_following': is_following,
        'is_own_profile': is_own_profile,
        'liked_post_ids': set(liked_post_ids),
    }
    return render(request, 'feed/profile.html', context)


@login_required
def edit_profile_view(request):
    """UPDATE: Edit own profile (bio, avatar, website, location)."""
    profile = request.user.profile
    profile_form = ProfileEditForm(
        request.POST or None, request.FILES or None, instance=profile
    )
    user_form = UserEditForm(request.POST or None, instance=request.user)

    if request.method == 'POST':
        if profile_form.is_valid() and user_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile updated!")
            return redirect('profile', username=request.user.username)

    return render(request, 'feed/edit_profile.html', {
        'profile_form': profile_form,
        'user_form': user_form,
    })


@login_required
@require_POST
def toggle_follow(request, username):
    """Toggle follow/unfollow a user. Returns JSON."""
    target_user = get_object_or_404(User, username=username)

    if target_user == request.user:
        return JsonResponse({'error': "You can't follow yourself."}, status=400)

    current_profile = request.user.profile
    target_profile = target_user.profile

    if current_profile.following.filter(user=target_user).exists():
        current_profile.following.remove(target_profile)
        following = False
    else:
        current_profile.following.add(target_profile)
        following = True
        Notification.objects.get_or_create(
            recipient=target_user,
            sender=request.user,
            notification_type='follow'
        )

    return JsonResponse({
        'following': following,
        'follower_count': target_profile.follower_count()
    })


# ─── NOTIFICATIONS ────────────────────────────────────────────────────────────

@login_required
def notifications_view(request):
    """List and mark all notifications as read."""
    notifications = request.user.notifications.select_related(
        'sender', 'sender__profile', 'post'
    ).all()
    # Mark all as read
    notifications.update(is_read=True)

    return render(request, 'feed/notifications.html', {'notifications': notifications})


# ─── SEARCH ───────────────────────────────────────────────────────────────────

@login_required
def search_view(request):
    """Search users and posts using Q objects for multi-field queries."""
    query = request.GET.get('q', '').strip()
    users = []
    posts = []

    if query:
        # Search users by username or full name
        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        ).select_related('profile').exclude(pk=request.user.pk)[:10]

        # Search posts by content
        posts = Post.objects.filter(
            content__icontains=query
        ).select_related('author', 'author__profile')[:20]

    return render(request, 'feed/search.html', {
        'query': query,
        'users': users,
        'posts': posts,
    })
