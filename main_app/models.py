from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group, Permission

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} ({self.email})"

class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.TextField(blank=True, null=True)  # Optional description field
    image = models.ImageField(upload_to='menu_images/', blank=True, null=True)  # Optional image field

    def __str__(self):
        return self.name

class Order(models.Model):
    is_completed = models.BooleanField(default=False)  
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,null=True, blank=True )  

    def __str__(self):
        return f"Order #{self.id}"

    def cart_item_count(self):
        return sum(item.quantity for item in self.items.all())

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        return self.menu_item.price * self.quantity
        
    def __str__(self):
        return f"{self.quantity} x {self.menu_item.name} in Order #{self.order.id}"

class CustomUser(AbstractUser):
    # Add additional fields if necessary
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)  # To store user's address
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    # Override default related names to avoid clashes
    groups = models.ManyToManyField(
        Group,
        related_name="customuser_set",
        blank=True,
        verbose_name="groups",
        help_text="The groups this user belongs to."
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="customuser_set",
        blank=True,
        verbose_name="user permissions",
        help_text="Specific permissions for this user."
    )

    def __str__(self):
        return self.username