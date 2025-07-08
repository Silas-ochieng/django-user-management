from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.custom_login, name='login'),
    path('logout/',views. custom_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
    
    # Admin views
    path('users/create/', views.create_user, name='create_user'),
    path('users/', views.user_list, name='user_list'),
    path('users/<int:user_id>/edit/', views.edit_user, name='edit_user'),
    path('users/delete/<int:pk>/', views.delete_user, name='delete_user'),
    path('users/<int:user_id>/toggle-status/', views.toggle_user_status, name='toggle_user_status'),
    path('users/<int:user_id>/reset-password/', views.reset_password, name='reset_password'),
    path('users/<int:user_id>/send-verification/', views.send_verification_email, name='send_verification_email'),
    path('resend-verification/', views.resend_verification_email, name='resend_verification_email'),
    path('verify-email/<str:token>/', views.verify_email, name='verify_email')
]