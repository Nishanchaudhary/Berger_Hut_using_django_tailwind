from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission


class CustomUser(AbstractUser):
    """Extended user model for customers"""
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)
    receive_promotions = models.BooleanField(default=True)

    groups = models.ManyToManyField(
        Group,
        related_name="accounts_customuser_set",  # Changed to unique name
        blank=True,
        verbose_name="groups",
        help_text="The groups this user belongs to."
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="accounts_customuser_set",  # Changed to unique name
        blank=True,
        verbose_name="user permissions",
        help_text="Specific permissions for this user."
    )

    def __str__(self):
        return self.get_full_name() or self.username