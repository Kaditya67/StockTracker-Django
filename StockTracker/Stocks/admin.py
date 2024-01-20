# stockapp/admin.py
from django.contrib import admin
from Stocks.models import ContactInformation

admin.site.register(ContactInformation)
