from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class UserManager(BaseUserManager):
    """Custom manager for User model without username field."""
    
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and return a regular user with an email and password.
        """
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and return a superuser with an email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    WE_CHAT = 'wechat'
    MOBILE = 'mobile'
    LOGIN_CHOICES = [
        (WE_CHAT, 'WeChat'),
        (MOBILE, 'Mobile'),
    ]
    
    # Remove username field, we'll use email instead
    username = None
    email = models.EmailField(unique=True, null=True, blank=True)
    
    # Custom fields
    login_method = models.CharField(max_length=10, choices=LOGIN_CHOICES, default=MOBILE)
    wechat_openid = models.CharField(max_length=100, blank=True, null=True, unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True, unique=True)
    avatar_url = models.URLField(blank=True, null=True)
    country_code = models.CharField(max_length=5, default='+86')
    is_verified = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Use email as the username field and custom manager
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Remove 'email' from REQUIRED_FIELDS since it's USERNAME_FIELD
    
    # Assign the custom manager
    objects = UserManager()

    def __str__(self):
        if self.email:
            return self.email
        elif self.phone_number:
            return f"{self.country_code}{self.phone_number}"
        else:
            return f"User {self.id}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    company = models.CharField(max_length=100, blank=True, null=True)
    position = models.CharField(max_length=50, blank=True, null=True)
    usage_count = models.IntegerField(default=0)
    last_activity = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Profile of {self.user}"