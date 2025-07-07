from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.views.decorators.http import require_POST
from django.contrib.auth.forms import AuthenticationForm
from .forms import (
    CustomUserChangeForm,
    CustomUserCreationForm, 
    ProfileUpdateForm,
    CustomPasswordChangeForm,
    CustomAuthenticationForm,
    AdminVerificationForm  # Now this will work
)
from .models import CustomUser
import uuid
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse
from django.conf import settings

def landing(request):
    return render(request, 'accounts/landing.html')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_verified = False
            user.verification_token = uuid.uuid4()
            user.token_created_at = timezone.now()
            user.save()
            
            verification_url = request.build_absolute_uri(
                f"/verify-email/{user.id}/{user.verification_token}/"
            )
            print(f"Verification URL (dev only): {verification_url}")
            
            messages.success(request, 'Registration successful! Please check your email for verification.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

def custom_login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                # Auto-verify superusers on login
                if user.is_superuser and not user.is_verified:
                    user.is_verified = True
                    user.save()
                
                if user.is_verified or user.is_superuser:
                    login(request, user)
                    messages.success(request, f"Welcome back, {user.username}!")
                    return redirect('profile')
                else:
                    messages.error(request, 
                        'Account not verified. '
                        '<a href="{}">Resend verification email</a> or contact admin.'.format(
                            reverse('resend-verification')
                        ),
                        extra_tags='safe'
                    )
            else:
                messages.error(request, 'Invalid credentials.')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})
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
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
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

@user_passes_test(lambda u: u.is_superuser or (u.user_type == 'admin' and u.is_verified))
def admin_dashboard(request):
    unverified_users = CustomUser.objects.filter(is_verified=False)
    return render(request, 'accounts/admin/verify_users.html', {
        'unverified_users': unverified_users
    })

@user_passes_test(lambda u: u.is_superuser or u.user_type == 'admin')
def admin_verify_user(request, user_id):
    # Get the user to be verified
    user = get_object_or_404(CustomUser, id=user_id)
    
    # Prevent self-verification and verify only non-superusers
    if user.is_superuser:
        messages.error(request, "Cannot verify another superuser.")
        return redirect('admin-verify-users')
    
    # Prevent admins from verifying other admins (unless superuser)
    if user.user_type == 'admin' and not request.user.is_superuser:
        messages.error(request, "Only superusers can verify other admins.")
        return redirect('admin-verify-users')
    
    # Prevent verifying already verified users
    if user.is_verified:
        messages.warning(request, f"User {user.username} is already verified.")
        return redirect('admin-verify-users')
    
    if request.method == 'POST':
        form = AdminVerificationForm(request.POST)
        if form.is_valid():
            # Perform verification
            user.is_verified = True
            user.verified_by = request.user
            user.verification_date = timezone.now()
            
            # Add verification notes if provided
            verification_notes = form.cleaned_data.get('verification_notes')
            if verification_notes:
                user.verification_notes = verification_notes
            
            user.save()
            
            # Send notification email to the user
            send_mail(
                'Account Verified by Admin',
                f'Your account has been verified by an administrator. You can now log in at {settings.BASE_URL}/login/',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            
            messages.success(request, f'Successfully verified user: {user.username}')
            return redirect('admin-verify-users')
    else:
        form = AdminVerificationForm()
    
    context = {
        'form': form,
        'user': user,
        'verifier': request.user,
        'can_verify': (request.user.is_superuser or 
                      (request.user.user_type == 'admin' and user.user_type != 'admin'))
    }
    
    return render(request, 'accounts/admin/verify_user.html', context)

@user_passes_test(lambda u: u.is_superuser or u.user_type == 'admin')
def user_list(request):
    users = CustomUser.objects.all()
    return render(request, 'accounts/user_list.html', {'users': users})

@user_passes_test(lambda u: u.is_superuser or u.user_type == 'admin')
def edit_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'User updated successfully!')
            return redirect('user_list')
    else:
        form = CustomUserChangeForm(instance=user)
    return render(request, 'accounts/edit_user.html', {'form': form, 'user': user})

def verify_email(request, user_id, token):
    try:
        user = CustomUser.objects.get(id=user_id, verification_token=token)
        
        if timezone.now() > user.token_created_at + timedelta(hours=24):
            messages.error(request, 'Verification link has expired.')
            return redirect('resend-verification')
        
        user.is_verified = True
        user.verification_token = None
        user.save()
        messages.success(request, 'Email verified successfully! You can now log in.')
        return redirect('login')
    
    except (CustomUser.DoesNotExist, ValueError):
        messages.error(request, 'Invalid verification link.')
        return redirect('register')

def resend_verification(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = CustomUser.objects.get(email=email)
            if user.is_verified:
                messages.info(request, 'This account is already verified.')
                return redirect('login')
            
            user.verification_token = uuid.uuid4()
            user.token_created_at = timezone.now()
            user.save()
            
            verification_url = request.build_absolute_uri(
                f"/verify-email/{user.id}/{user.verification_token}/"
            )
            print(f"New verification URL (dev only): {verification_url}")
            
            messages.success(request, 'New verification email sent! Check console for link.')
            return redirect('login')
        
        except CustomUser.DoesNotExist:
            messages.error(request, 'No account found with this email address.')
    
    return render(request, 'accounts/resend_verification.html')