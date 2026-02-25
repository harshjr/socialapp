"""
feed/urls.py — URL routing for all SocialApp views.

Django Concept: URL namespacing and named URLs
- Named URLs (name='feed') allow reverse lookups in templates: {% url 'feed' %}
- Avoids hardcoding paths throughout the codebase
- <int:pk> and <str:username> are path converters — Django validates the type
"""

from django.urls import path
from . import views

urlpatterns = [
    # ── Auth ──
    path('register/', views.register_view, name='register'),
    path('login/',    views.login_view,    name='login'),
    path('logout/',   views.logout_view,   name='logout'),

    # ── Feed (home) ──
    path('', views.feed_view, name='feed'),

    # ── Post CRUD ──
    path('post/<int:pk>/',        views.post_detail_view, name='post_detail'),   # READ
    path('post/<int:pk>/edit/',   views.post_edit_view,   name='post_edit'),     # UPDATE
    path('post/<int:pk>/delete/', views.post_delete_view, name='post_delete'),   # DELETE
    # CREATE is handled inline in feed_view via POST to '/'

    # ── Post interactions ──
    path('post/<int:pk>/like/',   views.toggle_like,   name='toggle_like'),

    # ── Profile ──
    path('profile/<str:username>/',      views.profile_view,    name='profile'),
    path('profile/edit/settings/',       views.edit_profile_view, name='edit_profile'),
    path('profile/<str:username>/follow/', views.toggle_follow, name='toggle_follow'),

    # ── Notifications & Search ──
    path('notifications/', views.notifications_view, name='notifications'),
    path('search/',        views.search_view,        name='search'),
]
