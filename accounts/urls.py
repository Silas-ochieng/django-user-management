from django.contrib.auth.views import LogoutView
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('verify-email/<int:user_id>/<uuid:token>/', views.verify_email, name='verify-email'),
    path('resend-verification/', views.resend_verification, name='resend-verification'),
    path('login/', views.custom_login, name='login'),
    path('logout/', LogoutView.as_view(next_page='landing'), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
    
    # Admin views
    
    
    
    
    
   
    path('admin/users/', views.user_list, name='user_list'),
    
    
]