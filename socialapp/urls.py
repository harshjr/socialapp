"""
Root URL configuration for SocialApp.
Includes feed app URLs and serves media files in development.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('feed.urls')),  # All app routes delegated to feed/urls.py
]

# Serve uploaded media files during development
# In production with AWS S3, Django won't serve these — S3 will.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
