from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from .models import CustomUser
from django.contrib.auth.forms import AuthenticationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    user_type = forms.ChoiceField(
        choices=CustomUser.USER_TYPE_CHOICES,
        initial='regular',
        widget=forms.Select(attrs={'class': 'form-select'}))
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'user_type', 'password1', 'password2','verification_method', 'profile_picture')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.is_superuser:
            self.fields['verification_method'].choices = [
                ('email', 'Email Verification'),
                ('admin', 'Admin Approval')
            ]
        # Add Bootstrap classes to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'profile_picture')

class ProfileUpdateForm(UserChangeForm):
    # Remove password field from the form
    password = None
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'profile_picture']
        widgets = {
            'profile_picture': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'  # Only accept image files
            })
        }
class CustomPasswordChangeForm(PasswordChangeForm):
    pass
class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('username', css_class='form-control'),
            Field('password', css_class='form-control'),
            Submit('submit', 'Login', css_class='btn btn-primary')
        )

class AdminVerificationForm(forms.Form):
    verification_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Optional verification notes...'
        }),
        help_text="Add any notes about this verification"
    )