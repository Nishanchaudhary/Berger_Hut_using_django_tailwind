from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.urls import reverse


class Category(models.Model):
    """Model for menu item categories (Burgers, Sides, Drinks, etc.)"""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    display_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['display_order', 'name']
    

    def save(self, *args, **kwargs):
        if not self.slug:  # Only generate slug if it doesn't exist
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    
    
    def __str__(self):
        return self.name

class MenuItem(models.Model):
    """Model for food items in the menu"""
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='menu_items')
    price = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0)])
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='menu_images/', blank=True, null=True)
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False, verbose_name="Featured Item")
    preparation_time = models.PositiveSmallIntegerField(default=15, help_text="Estimated preparation time in minutes")
    calories = models.PositiveIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.category})"
    
    def get_absolute_url(self):
        return reverse('menu_item_detail', kwargs={'pk': self.pk})

    class Meta:
        ordering = ['category__display_order', 'name']

class Ingredient(models.Model):
    """Model for ingredients used in menu items"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_vegetarian = models.BooleanField(default=False)
    is_vegan = models.BooleanField(default=False)
    is_gluten_free = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class MenuItemIngredient(models.Model):
    """Through model for ingredients in menu items"""
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='ingredients')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.CharField(max_length=50, blank=True, null=True)  # e.g., "1 slice", "50g"

    class Meta:
        unique_together = ('menu_item', 'ingredient')

    def __str__(self):
        return f"{self.menu_item.name} - {self.ingredient.name}"


class Order(models.Model):
    """Model for customer orders"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready for Pickup'),
        ('delivering', 'Out for Delivery'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('khalti', 'Khalti'),
        ('e-sewa', 'E-sewa'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    promotions = models.ManyToManyField('Promotion', blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    delivery_address = models.TextField(blank=True, null=True)
    contact_phone = models.CharField(max_length=15, blank=True, null=True)
    special_instructions = models.TextField(blank=True, null=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='cash')
    is_paid = models.BooleanField(default=False)
    pidx = models.CharField(max_length=100, blank=True, null=True, verbose_name="Khalti Transaction ID")
    estimated_delivery_time = models.DateTimeField(blank=True, null=True)

    @classmethod
    def get_pending_order(cls, user):
        """
        Get or create a pending order for the current user
        """
        order, created = cls.objects.get_or_create(
            user=user,
            status='pending',
            defaults={
                'total_price': 0,
                'payment_method': 'cash',
                'is_paid': False
            }
        )
        return order

    def __str__(self):
        return f"Order #{self.id} - {self.get_status_display()}"

    def update_total(self):
        """Update the total price based on order items"""
        self.total_price = sum(item.total_price() for item in self.items.all())
        self.save()

    def cart_item_count(self):
        return sum(item.quantity for item in self.items.all())

    class Meta:
        ordering = ['-created_at']

class OrderItem(models.Model):
    """Model for items within an order"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    menu_item = models.ForeignKey(MenuItem, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    special_requests = models.TextField(blank=True, null=True)
    price_at_order = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)

    def save(self, *args, **kwargs):
        """Save the price at the time of ordering"""
        if not self.price_at_order:
            self.price_at_order = self.menu_item.price
        super().save(*args, **kwargs)
        self.order.update_total()

    def delete(self, *args, **kwargs):
        """Update order total when item is deleted"""
        super().delete(*args, **kwargs)
        self.order.update_total()

    def total_price(self):
        return (self.price_at_order or self.menu_item.price) * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.menu_item.name} in Order #{self.order.id}"

class ContactMessage(models.Model):
    """Model for customer contact messages"""
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True, null=True)
    subject = models.CharField(max_length=200, default="General Inquiry")
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.subject} from {self.name}"

    class Meta:
        ordering = ['-submitted_at']

class Promotion(models.Model):
    """Model for special offers and promotions"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    discount_percentage = models.PositiveSmallIntegerField(default=0)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    applicable_items = models.ManyToManyField(MenuItem, blank=True)
    promo_code = models.CharField(max_length=20, blank=True, null=True, unique=True)
    image = models.ImageField(upload_to='promo_images/', blank=True, null=True)


    @classmethod
    def get_active_promotions(cls):
        now = timezone.now()
        return cls.objects.filter(
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        ).order_by('-start_date')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-start_date']

class Review(models.Model):
    """Model for customer reviews of menu items"""
    RATING_CHOICES = [
        (1, '★☆☆☆☆'),
        (2, '★★☆☆☆'),
        (3, '★★★☆☆'),
        (4, '★★★★☆'),
        (5, '★★★★★'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    is_approved = models.BooleanField(default=False) 
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user}'s review of {self.menu_item}"

    class Meta:
        unique_together = ('user', 'menu_item')
        ordering = ['-created_at']

