# stockapp/models.py
from django.db import models

class ContactInformation(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    address = models.CharField(max_length=120)

    def __str__(self):
        return self.name
