# 🚀 SocialApp — Django Social Media Platform

A full-featured social media application built with Django, demonstrating core concepts like CRUD operations, ORM queries, signals, model relationships, and a modern dark UI.

---

## ✨ Features

| Feature | Details |
|---|---|
| **Auth** | Register, login, logout (built on Django's auth system) |
| **Posts** | Create tweet-style text posts, image posts, or both |
| **Feed** | Personalized feed of followed users + own posts |
| **CRUD** | Create, Read, Update, Delete posts with ownership checks |
| **Likes** | Toggle likes (AJAX, no page reload) |
| **Comments** | Comment on any post |
| **Follow system** | Follow/unfollow users (AJAX) |
| **Notifications** | Like, comment, and follow alerts |
| **Search** | Search users and posts |
| **Profile** | User profiles with bio, avatar, stats, post history |
| **Admin** | Full Django admin with custom display |

---

## 🏗️ Django Concepts Demonstrated

### Models (`feed/models.py`)
- **OneToOneField** — UserProfile ↔ User
- **ForeignKey** — Post → User, Comment → Post
- **ManyToManyField** — UserProfile followers (asymmetric)
- **ImageField** — Photo uploads with `upload_to` path
- **Model Meta** — `ordering`, `unique_together`, `verbose_name`
- **Django Signals** — `post_save` auto-creates UserProfile
- **Custom model methods** — `like_count()`, `post_count()`

### Views (`feed/views.py`)
- **Function-based views** with `@login_required`
- **CRUD pattern** — create (feed), read (detail), update (edit), delete (delete)
- **ORM queries** — `filter()`, `select_related()`, `prefetch_related()`, `Q()`, `annotate()`
- **`get_or_create()`** — atomic like/notification creation
- **JsonResponse** — AJAX endpoints for likes and follows
- **Pagination** — `Paginator` for the feed
- **Django messages** — Flash notifications

### Forms (`feed/forms.py`)
- **ModelForm** — auto-generates fields from models
- **Custom `clean()` validation** — cross-field rules
- **UserCreationForm extension** — adds email field

### Templates
- **Template inheritance** — `base.html` → child templates
- **Custom template tags** (`feed/templatetags/feed_tags.py`) — `time_ago`, `format_count`
- **CSRF tokens** — all forms protected
- **`{% url %}` tag** — named URL resolution

### URL Routing (`feed/urls.py`)
- Named URLs with `<int:pk>` and `<str:username>` path converters
- RESTful-style URL patterns

---

## 🚀 Quick Start

### 1. Clone and set up environment
```bash
git clone <your-repo>
cd socialapp
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run migrations
```bash
python manage.py migrate
```

### 4. Create a superuser (for admin access)
```bash
python manage.py createsuperuser
```

### 5. Run the dev server
```bash
python manage.py runserver
```

Open **http://127.0.0.1:8000** in your browser.  
Django Admin: **http://127.0.0.1:8000/admin/**

---

## 📁 Project Structure

```
socialapp/
├── manage.py
├── requirements.txt
├── socialapp/                  # Django project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── feed/                       # Main app
│   ├── models.py               # UserProfile, Post, Comment, Like, Notification
│   ├── views.py                # All views (FBV + CRUD)
│   ├── forms.py                # RegisterForm, PostForm, CommentForm, etc.
│   ├── urls.py                 # URL routing
│   ├── admin.py                # Admin customization
│   ├── templatetags/
│   │   └── feed_tags.py        # Custom template filters
│   ├── migrations/
│   └── templates/feed/
│       ├── base.html           # Sidebar nav layout
│       ├── auth.html           # Login / Register
│       ├── feed.html           # Main feed + composer
│       ├── profile.html        # User profile page
│       ├── post_detail.html    # Single post + comments
│       ├── post_form.html      # Edit post
│       ├── post_confirm_delete.html
│       ├── edit_profile.html
│       ├── notifications.html
│       └── search.html
├── static/
│   ├── css/main.css            # Full UI stylesheet (dark theme)
│   └── js/
│       ├── main.js             # Flash messages, dropdowns
│       └── feed.js             # AJAX likes/follows, image preview
└── media/                      # User uploads (gitignored in production)
    └── uploads/
```

---

## ☁️ AWS S3 Migration (Production)

When ready to deploy, replace local file storage with S3:

**1. Install packages:**
```bash
pip install django-storages boto3
```

**2. In `settings.py`, add:**
```python
INSTALLED_APPS += ['storages']

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_STORAGE_BUCKET_NAME = 'your-bucket-name'
AWS_S3_REGION_NAME = 'us-east-1'
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/'
```

**No model changes needed** — `ImageField` automatically uses S3 once `DEFAULT_FILE_STORAGE` is set.

---

## 🗺️ URL Reference

| URL | View | Description |
|---|---|---|
| `/` | `feed_view` | Main feed (GET) + post creation (POST) |
| `/login/` | `login_view` | Login |
| `/register/` | `register_view` | Register |
| `/post/<pk>/` | `post_detail_view` | View post + comments |
| `/post/<pk>/edit/` | `post_edit_view` | Edit own post |
| `/post/<pk>/delete/` | `post_delete_view` | Delete own post |
| `/post/<pk>/like/` | `toggle_like` | Like/unlike (AJAX POST) |
| `/profile/<username>/` | `profile_view` | User profile |
| `/profile/edit/settings/` | `edit_profile_view` | Edit own profile |
| `/profile/<username>/follow/` | `toggle_follow` | Follow/unfollow (AJAX POST) |
| `/notifications/` | `notifications_view` | Notification list |
| `/search/?q=` | `search_view` | Search users & posts |
| `/admin/` | Django Admin | Backend management |
