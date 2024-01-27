# stockapp/admin.py
from django.contrib import admin
from Stocks.models import ContactInformation

admin.site.register(ContactInformation)


# stocks/admin.py
from .models import StockData

admin.site.register(StockData)

from .models import IndicatorValues

admin.site.register(IndicatorValues)



 