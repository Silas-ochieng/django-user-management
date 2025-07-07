from django.test import TestCase
from django.urls import reverse
from .models import CustomUser
from .forms import CustomUserCreationForm

class UserModelTest(TestCase):
    def test_create_user(self):
        user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            user_type='regular'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertFalse(user.is_verified)

class RegistrationTest(TestCase):
    def test_registration_view(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Register')
        
    def test_registration_form(self):
        form_data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'user_type': 'regular'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())

class ProfileTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='profileuser',
            email='profile@example.com',
            password='testpass123'
        )
        self.client.login(username='profileuser', password='testpass123')
    
    def test_profile_view(self):
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'profileuser')