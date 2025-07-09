from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    UserChangeForm,
    PasswordChangeForm,
    AuthenticationForm
)
from .models import CustomUser
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field
from django.contrib.auth import authenticate


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError("Email is required")
        if '@' not in email:
            raise forms.ValidationError("Enter a valid email address")
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use")
        return email


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'profile_picture')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('password', None)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'profile_picture']
        widgets = {
            'profile_picture': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.help_text = None


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password'
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Remember me'
    )

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request=request, *args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('username'),
            Field('password'),
            Field('remember_me'),
            Submit('submit', 'Login', css_class='btn btn-primary w-100')
        )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if email and password:
            user = authenticate(username=email, password=password)
            if user is None:
                raise forms.ValidationError("Invalid email or password.")
            if not user.is_email_verified:
                raise forms.ValidationError("Please verify your email first.")
        return cleaned_data