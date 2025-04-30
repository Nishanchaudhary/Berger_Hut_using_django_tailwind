from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('phone_number', 'address', 'profile_picture', 'birth_date', 'receive_promotions')}),
    )
    filter_horizontal = ()  # Remove favorite_items from here
    
    # If you want to manage favorite_items in admin, add it separately
    filter_horizontal = ('groups', 'user_permissions',)  # Only for many-to-many fields that exist in the model
    
admin.site.register(CustomUser, CustomUserAdmin)
