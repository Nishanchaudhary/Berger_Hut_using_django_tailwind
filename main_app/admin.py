from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .models import MenuItem, Order, OrderItem,ContactMessage

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'description', 'image')
    list_filter = ('price',)
    search_fields = ('name',)

admin.site.register(Order)
admin.site.register(OrderItem)

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('phone_number', 'address', 'profile_picture',),
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('phone_number', 'address', 'profile_picture',),
        }),
    )

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'submitted_at')
    search_fields = ('name', 'email')
    list_filter = ('submitted_at',)

admin.site.register(CustomUser, CustomUserAdmin)