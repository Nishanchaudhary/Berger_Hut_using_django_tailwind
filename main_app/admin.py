from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone
from .models import *

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_order', 'is_active')
    list_editable = ('display_order', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    list_filter = ('is_active',)
   

class MenuItemIngredientInline(admin.TabularInline):
    model = MenuItemIngredient
    extra = 1
    fields = ('ingredient', 'quantity')

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_available', 'is_featured')
    list_editable = ('price', 'is_available', 'is_featured')
    list_filter = ('category', 'is_available', 'is_featured')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [MenuItemIngredientInline]  # Using inline instead of filter_horizontal
    fieldsets = (
        (None, {
            'fields': ('name', 'category', 'price', 'description')
        }),
        ('Availability', {
            'fields': ('is_available', 'is_featured')
        }),
        ('Details', {
            'fields': ('image', 'preparation_time', 'calories')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_vegetarian', 'is_vegan', 'is_gluten_free')
    list_filter = ('is_vegetarian', 'is_vegan', 'is_gluten_free')
    search_fields = ('name',)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('price_at_order', 'total_price')
    fields = ('menu_item', 'quantity', 'price_at_order', 'total_price', 'special_requests')
    
    def total_price(self, instance):
        return instance.total_price()
    total_price.short_description = 'Total'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total_price', 'created_at', 'is_paid')
    list_filter = ('status', 'is_paid', 'payment_method', 'created_at')
    search_fields = ('id', 'user__username', 'contact_phone')
    readonly_fields = ('created_at', 'updated_at', 'total_price')
    inlines = [OrderItemInline]
    fieldsets = (
        (None, {
            'fields': ('user', 'status', 'total_price')
        }),
        ('Delivery Info', {
            'fields': ('delivery_address', 'contact_phone', 'estimated_delivery_time')
        }),
        ('Payment', {
            'fields': ('payment_method', 'is_paid')
        }),
        ('Instructions', {
            'fields': ('special_instructions',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    actions = ['mark_as_completed', 'mark_as_cancelled']

    def mark_as_completed(self, request, queryset):
        queryset.update(status='completed')
    mark_as_completed.short_description = "Mark selected orders as completed"

    def mark_as_cancelled(self, request, queryset):
        queryset.update(status='cancelled')
    mark_as_cancelled.short_description = "Mark selected orders as cancelled"

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'submitted_at', 'is_resolved')
    list_filter = ('is_resolved', 'submitted_at')
    search_fields = ('name', 'email', 'subject')
    readonly_fields = ('submitted_at',)
    actions = ['mark_as_resolved']

    def mark_as_resolved(self, request, queryset):
        queryset.update(is_resolved=True, resolved_at=timezone.now())
    mark_as_resolved.short_description = "Mark selected messages as resolved"

@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'discount_percentage', 'is_active')
    list_filter = ('is_active', 'start_date', 'end_date')
    search_fields = ('name', 'promo_code')
    filter_horizontal = ('applicable_items',)  # This works because applicable_items is a ManyToManyField
    date_hierarchy = 'start_date'
    list_editable = ('is_active',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('applicable_items')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'menu_item', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__username', 'menu_item__name')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('user', 'menu_item')
    
    def get_rating_display(self, obj):
        return obj.get_rating_display()
    get_rating_display.short_description = 'Rating'