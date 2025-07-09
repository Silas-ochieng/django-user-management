from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import timedelta
import uuid

from .forms import (
    CustomUserChangeForm,
    CustomUserCreationForm, 
    CustomPasswordChangeForm,
    CustomAuthenticationForm
)
from .models import CustomUser
from django.conf import settings
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator


def landing(request):
    return render(request, 'accounts/landing.html')


def verify_email(request, user_id, token):
    try:
        user = CustomUser.objects.get(pk=user_id, verification_token=token)

        # Check if token expired (24 hours)
        if timezone.now() > user.token_created_at + timedelta(hours=24):
            messages.error(request, "Verification link has expired.")
            return redirect('resend-verification')

        user.is_email_verified = True
        user.is_active = True  # Activate the account
        user.save()

        messages.success(request, "Email verified successfully! You can now log in.")
        return redirect('login')

    except CustomUser.DoesNotExist:
        messages.error(request, "Invalid verification link.")
        return redirect('register')


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Inactive until email verified
            user.save()

            # Send verification email
            try:
                user.send_verification_email(request)
                messages.success(request, "Verification email sent! Check your inbox.")
                return redirect('login')
            except Exception as e:
                user.delete()
                messages.error(request, f"Failed to send verification email: {str(e)}")
                return redirect('register')
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})


def custom_login(request):
    if request.method == 'POST':
        # For POST requests, pass both request and POST data
        form = CustomAuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if not user.is_email_verified:
                messages.error(request, "Please verify your email first.")
                return redirect('login')
            
            login(request, user)
            return redirect('home')
    else:
        # For GET requests, only pass the request object
        form = CustomAuthenticationForm(request=request)

    return render(request, 'accounts/login.html', {'form': form})

def resend_verification(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = CustomUser.objects.get(email=email)
            if user.is_email_verified:
                messages.info(request, 'This account is already verified.')
                return redirect('login')

            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            verification_link = f"{request.scheme}://{request.get_host()}/verify-email/{uid}/{token}/"

            subject = 'Verify your email address'
            html_message = render_to_string('accounts/verification_email.html', {
                'user': user,
                'verification_link': verification_link,
            })

            send_mail(
                subject,
                strip_tags(html_message),
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=html_message,
                fail_silently=False,
            )

            messages.success(request, 'New verification email sent! Please check your inbox.')
            return redirect('login')

        except CustomUser.DoesNotExist:
            messages.error(request, 'No account found with this email address.')

    return render(request, 'accounts/resend_verification.html')


@require_POST
def custom_logout(request):
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect('landing')


@login_required
def profile(request):
    return render(request, 'accounts/profile.html', {'user': request.user})


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        form = CustomUserChangeForm(instance=request.user)
    return render(request, 'accounts/edit_profile.html', {'form': form})


@login_required
def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password changed successfully!')
            return redirect('profile')
    else:
        form = CustomPasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {'form': form})


@login_required
@user_passes_test(lambda u: u.is_superuser)
def user_list(request):
    users = CustomUser.objects.all()
    return render(request, 'accounts/admin/user_list.html', {'users': users})
