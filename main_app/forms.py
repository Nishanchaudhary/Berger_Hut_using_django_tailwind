from django import forms
from .models import *
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from accounts.models import CustomUser  

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.HiddenInput(),
            'comment': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border rounded focus:ring-2 focus:ring-yellow-500 focus:border-yellow-500',
                'rows': 4,
                'placeholder': 'Share your experience...'
            })
        }

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'})
        }

class PromotionForm(forms.ModelForm):
    code = forms.CharField(  # Rename to 'code' to match your view
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border rounded focus:ring-2 focus:ring-yellow-500 focus:border-yellow-500',
            'placeholder': 'Enter promo code'
        }))
    
    class Meta:
        model = Promotion
        fields = []  # Remove promo_code since we're defining it manually

class OrderItemForm(forms.ModelForm):
    special_requests = forms.CharField(required=False)
    class Meta:
        model = OrderItem
        fields = ['menu_item', 'quantity', 'special_requests']
        widgets = {
            'menu_item': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
            'special_requests': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Any special requests?'
            })
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email']  # Add the fields you want to include

class CheckoutForm(forms.Form):
    # Delivery information fields
    delivery_address = forms.CharField(
        label="Delivery Address",
        widget=forms.Textarea(attrs={'rows': 3}),
        required=True,
        max_length=500
    )
    
    contact_phone = forms.CharField(
        label="Contact Phone",
        required=True,
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            )
        ]
    )
    
    # Payment method choices
    PAYMENT_CHOICES = [
        ('khalti', 'Khelti'),
        ('e-sewa', 'E-sewa'),
        ('cash_on_delivery', 'Cash on Delivery'),
    ]
    
    payment_method = forms.ChoiceField(
        label="Payment Method",
        choices=PAYMENT_CHOICES,
        widget=forms.RadioSelect,
        required=True
    )
    
    additional_notes = forms.CharField(
        label="Additional Notes (optional)",
        widget=forms.Textarea(attrs={'rows': 2}),
        required=False,
        max_length=200
    )
    
    save_address = forms.BooleanField(
        label="Save this address for future orders",
        required=False,
        initial=True
    )