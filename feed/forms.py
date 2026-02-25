"""
forms.py — Django Forms for SocialApp.

Django Concepts Demonstrated:
- ModelForm (auto-generates form fields from model)
- Form validation with clean() methods
- Custom widgets for styling
- UserCreationForm extension
- File upload handling (ImageField)
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Post, Comment, UserProfile


class RegisterForm(UserCreationForm):
    """
    Extends Django's built-in UserCreationForm to add email field.
    UserCreationForm already handles password hashing and validation.
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'your@email.com'
        })
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'username'
        })
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Password'
        })
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Confirm password'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        """Custom validation: ensure email is unique."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email


class LoginForm(AuthenticationForm):
    """Extends Django's AuthenticationForm with custom styling."""
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Password'
        })
    )


class PostForm(forms.ModelForm):
    """
    ModelForm for creating/editing posts.
    Django automatically creates form fields from the Post model.
    """
    content = forms.CharField(
        required=False,
        max_length=280,
        widget=forms.Textarea(attrs={
            'class': 'post-textarea',
            'placeholder': "What's happening?",
            'rows': 3,
            'id': 'post-content'
        })
    )
    image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'hidden',
            'id': 'post-image',
            'accept': 'image/*'
        })
    )

    class Meta:
        model = Post
        fields = ['content', 'image']

    def clean(self):
        """Cross-field validation: post must have text OR image (or both)."""
        cleaned_data = super().clean()
        content = cleaned_data.get('content', '').strip()
        image = cleaned_data.get('image')

        if not content and not image:
            raise forms.ValidationError("A post must have text, an image, or both.")
        return cleaned_data


class CommentForm(forms.ModelForm):
    """Simple inline comment form."""
    content = forms.CharField(
        max_length=280,
        widget=forms.TextInput(attrs={
            'class': 'comment-input',
            'placeholder': 'Add a comment...'
        })
    )

    class Meta:
        model = Comment
        fields = ['content']


class ProfileEditForm(forms.ModelForm):
    """Form for editing UserProfile fields."""
    bio = forms.CharField(
        required=False,
        max_length=300,
        widget=forms.Textarea(attrs={
            'class': 'form-input',
            'rows': 3,
            'placeholder': 'Tell people about yourself...'
        })
    )
    website = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-input',
            'placeholder': 'https://yourwebsite.com'
        })
    )
    location = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'City, Country'
        })
    )
    avatar = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-input',
            'accept': 'image/*'
        })
    )

    class Meta:
        model = UserProfile
        fields = ['bio', 'avatar', 'website', 'location']


class UserEditForm(forms.ModelForm):
    """Form for editing the base User model fields."""
    first_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'First name'})
    )
    last_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Last name'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
