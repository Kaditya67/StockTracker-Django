# stockapp/admin.py
from django.contrib import admin
from Stocks.models import ContactInformation

admin.site.register(ContactInformation)


# stocks/admin.py
from .models import FinancialData

admin.site.register(FinancialData)
# stocks/admin.py
from .models import SectorData

admin.site.register(SectorData)

# from .models import IndicatorValues

# admin.site.register(IndicatorValues)
from .models import EmaCounts

admin.site.register(EmaCounts)


# User SignUp

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserProfile

class CustomUserAdmin(UserAdmin):
    model = UserProfile
    # Customize the display fields if needed
    list_display = ['username', 'email', 'is_staff', 'is_active']

# Register the UserProfile model with the custom admin
admin.site.register(UserProfile, CustomUserAdmin)




 