from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import uuid
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.models import BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_superuser(self, email, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_verified', True)  # Auto-verify superusers
        extra_fields.setdefault('user_type', 'admin')  # Default to admin type

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, username, password, **extra_fields)

class CustomUser(AbstractUser):
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)

    # If you use user_type
    USER_TYPE_CHOICES = (
        ('admin', 'Admin'),
        ('regular', 'Regular User'),
    )
    # User Fields
    user_type = models.CharField(
        max_length=10, 
        choices=USER_TYPE_CHOICES, 
        default='regular',
        verbose_name="User Type"
    )
    email = models.EmailField(
        unique=True,
        verbose_name="Email Address",
        error_messages={
            'unique': "A user with that email already exists.",
        }
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name="Verified Status",
        help_text="Designates whether this user has verified their email."
    )
    verification_token = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        verbose_name="Verification Token"
    )
    verification_token_created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Token Creation Time"
    )
    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        null=True,
        blank=True,
        verbose_name="Profile Picture"
    )
    last_activity = models.DateTimeField(
        default=timezone.now,
        verbose_name="Last Activity"
    )

    # Override the default username field to make email the unique identifier
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ['-date_joined']
        permissions = [
            ("can_verify_users", "Can verify other users"),
        ]

    def __str__(self):
        return self.email if self.email else self.username

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def send_verification_email(self):
        """
        Send verification email to the user with a unique verification link
        """
        subject = "Verify Your Account"
        message = render_to_string('accounts/emails/verification_email.html', {
            'user': self,
            'verification_url': self.get_verification_url(),
        })
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [self.email],
            fail_silently=False,
            html_message=message
        )

    def get_verification_url(self):
        """
        Generate the verification URL for the user
        """
        from django.urls import reverse
        return settings.BASE_URL + reverse('verify-account', kwargs={
            'token': str(self.verification_token),
            'user_id': self.pk
        })

    def is_verification_token_expired(self):
        """
        Check if the verification token has expired (after 24 hours)
        """
        expiration_time = self.verification_token_created_at + timezone.timedelta(hours=24)
        return timezone.now() > expiration_time

    def regenerate_verification_token(self):
        """
        Generate a new verification token and update the creation time
        """
        self.verification_token = uuid.uuid4()
        self.verification_token_created_at = timezone.now()
        self.save()
        return self.verification_token

    def verify_user(self):
        """
        Mark the user as verified
        """
        self.is_verified = True
        self.save()
     
    VERIFICATION_METHODS = [
        ('email', 'Email Verification'),
        ('admin', 'Admin Approval'),
        ('none', 'No Verification Required'),
    ]
    
    verification_method = models.CharField(
        max_length=10,
        choices=VERIFICATION_METHODS,
        default='email',
        help_text="Select how users should be verified"
    )
    
    verified_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_users'
    )
    verification_date = models.DateTimeField(null=True, blank=True)
def requires_verification(self):
    """Check if user needs verification to login"""
    return not (self.is_superuser or self.is_verified)
objects = CustomUserManager()
    
def has_full_privileges(self):
        """Check if user has superuser or equivalent privileges"""
        return self.is_superuser or (self.user_type == 'admin' and self.is_verified)