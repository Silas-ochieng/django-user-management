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
    path('users/', views.user_list, name='user_list'),
    path('users/<int:user_id>/edit/', views.edit_user, name='edit_user'),
]