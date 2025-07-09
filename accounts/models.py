from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import uuid

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_email_verified = models.BooleanField(default=False)
    verification_token = models.UUIDField(default=uuid.uuid4, editable=False)
    token_created_at = models.DateTimeField(auto_now_add=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    user_type = models.CharField(
        max_length=10,
        choices=[('admin', 'Admin'), ('regular', 'Regular')],
        default='regular'
    )
    is_verified = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    def send_verification_email(self, request):
        """
        Sends a verification email to the user with a verification link.
        """
        verification_url = request.build_absolute_uri(
            f"/verify-email/{self.pk}/{self.verification_token}/"
        )

        subject = "Verify Your Email"
        message = f"Click this link to verify your email: {verification_url}"
        from_email = "noreply@yourdomain.com"

        self.email_user(subject, message, from_email)

    def is_verification_token_expired(self):
        """
        Returns True if the token is older than 24 hours.
        """
        return timezone.now() > self.token_created_at + timezone.timedelta(hours=24)

    def regenerate_verification_token(self):
        """
        Creates a new verification token and updates the timestamp.
        """
        self.verification_token = uuid.uuid4()
        self.token_created_at = timezone.now()
        self.save()
