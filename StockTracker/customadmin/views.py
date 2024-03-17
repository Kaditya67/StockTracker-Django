from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.urls import reverse
from Stocks.models import *

def admin_login(request):
    if request.user.is_authenticated:
        return redirect('admindashboard/')

    if request.method == 'POST':
        username = request.POST.get('username') 
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user is not None and user.is_superuser:
            login(request, user)
            return redirect('admindashboard/')
        else:
            messages.error(request, 'Invalid credentials')
            return redirect(reverse('admin_login'))  # Redirect back to login page with error message

    return render(request, 'login.html')

def admin_dashboard(request):
    return render(request, 'admindashboard.html')

def ema_counts_sectors(request):
    obj = EmaCountsSector.objects.all()
    unique_symbols = EmaCountsSector.objects.values_list('stock_data__symbol', flat=True).distinct()
    return render(request, 'Ema_counts_sectors.html', {'obj': obj, 'unique_symbols': unique_symbols})

def ema_counts_stocks(request):
    obj = EmaCounts.objects.all()
    unique_symbols = EmaCounts.objects.values_list('stock_data__symbol', flat=True).distinct()
    return render(request, 'Ema_counts_stocks.html', {'obj': obj, 'unique_symbols': unique_symbols})


def financial_data(request):
    obj=FinancialData.objects.all()
    unique_symbols=FinancialData.objects.values_list('symbol', flat=True).distinct()
    # print(unique_symbols)
    return render(request, 'financial_data.html',{'obj':obj,'unique_symbols':unique_symbols})

def sector_data(request):
    obj=SectorData.objects.all()
    unique_symbols=SectorData.objects.values_list('symbol', flat=True).distinct()
    # print(unique_symbols)
    return render(request, 'sector_data.html',{'obj':obj,'unique_symbols':unique_symbols})
    