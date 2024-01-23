# stockapp/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class ContactInformation(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    address = models.CharField(max_length=120)

    def __str__(self):
        return self.name

class UserProfile(AbstractUser):
    # Add any additional fields you need for your user model
    # For example:
    bio = models.TextField(blank=True)
    birth_date = models.DateField(null=True, blank=True)

    # Add related_name to avoid clashes with auth.User
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='user_profiles',
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='user_profiles',
    )

    def save(self, *args, **kwargs):
        # You don't need to manually set_password when extending AbstractUser
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username


class StockData(models.Model):
    symbol = models.CharField(max_length=10)
    date = models.DateField()
    open_price = models.DecimalField(max_digits=10, decimal_places=4)
    high_price = models.DecimalField(max_digits=10, decimal_places=4)
    low_price = models.DecimalField(max_digits=10, decimal_places=4)
    close_price = models.DecimalField(max_digits=10, decimal_places=4)
    volume = models.IntegerField()

    def __str__(self):
        return f'{self.symbol} - {self.date}'
