# stockapp/models.py
# from django.contrib.auth.models import AbstractUser
from django.db import models

class ContactInformation(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    address = models.CharField(max_length=120)

    def __str__(self):
        return self.name

# models.py
from django.contrib.auth.models import AbstractUser

# models.py
from django.contrib.auth.models import AbstractUser, Group, Permission

class UserProfile(AbstractUser):
    # Other fields if needed

    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='user_profiles_groups',  # Updated related_name
    )

    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='user_profiles_permissions',  # Updated related_name
    )

    def save(self, *args, **kwargs):
        # You don't need to manually set_password when extending AbstractUser
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username

# models.py
from django.db import models

class FinancialData(models.Model):
    symbol = models.CharField(max_length=10)
    date = models.DateField()
    close_price = models.DecimalField(max_digits=10, decimal_places=2)
    ema20 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    ema50 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    ema100 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    ema200 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    rsi = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    rs = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    # Add other fields as needed

    def __str__(self):
        return f"{self.symbol} - {self.date}"

# Indicator count 
# models.py
from django.db import models    

class EmaCounts(models.Model):
    stock_data = models.ForeignKey(FinancialData, on_delete=models.CASCADE)
    ema20_output = models.TextField(blank=True)
    ema50_output = models.TextField(blank=True)
    ema100_output = models.TextField(blank=True)
    ema200_output = models.TextField(blank=True)
    # Add other fields as needed


    def __str__(self):
        return f"{self.stock_data.symbol} - {self.stock_data.date}"