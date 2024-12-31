from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
from .models import CustomUser,ContactMessage
from django.core.exceptions import ValidationError

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']

class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        fields = ['username', 'password']

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'password1', 'password2',
            'phone_number', 'address', 'profile_picture', 
        ]

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'phone_number', 'address', 
            'profile_picture', 
        ]

class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'w-full border border-gray-300  rounded-lg shadow-sm focus:ring-red-600 focus:border-red-600',
            'placeholder': 'Username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full border-gray-300 rounded-lg shadow-sm focus:ring-red-600 focus:border-red-600',
            'placeholder': 'Password'
        })
    )

class CustomUserCreationForm(UserCreationForm):

    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        return password2


    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'phone_number', 'address']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full border-gray-300 rounded-lg px-3 py-2',
                'placeholder': 'Username'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full border-gray-300 rounded-lg px-3 py-2',
                'placeholder': 'Email'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'w-full border-gray-300 rounded-lg px-3 py-2',
                'placeholder': 'Phone Number'
            }),
            'address': forms.Textarea(attrs={
                'class': 'w-full border-gray-300 rounded-lg px-3 py-2',
                'placeholder': 'Address',
                'rows': 3
            }),
            'profile_image': forms.FileInput(attrs={
                'class': 'w-full border-gray-300 rounded-lg px-3 py-2',
            }),
        }
        help_texts = {
            'username': None,
            'password1': None,
            'password2': None,
        }

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-600',
                'placeholder': 'Your Name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-600',
                'placeholder': 'Your Email'
            }),
            'message': forms.Textarea(attrs={
                'class': 'w-full border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-600',
                'placeholder': 'Your Message',
                'rows': 5
            }),
        }