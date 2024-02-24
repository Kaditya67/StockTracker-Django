# stockapp/admin.py
from django.contrib import admin

from . models import stock_user
admin.site.register(stock_user)


# stocks/admin.py
from .models import FinancialData
admin.site.register(FinancialData)

from .models import SectorData
admin.site.register(SectorData)

from .models import EmaCounts
admin.site.register(EmaCounts)

from .models import EmaCountsSector
admin.site.register(EmaCountsSector)



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




 