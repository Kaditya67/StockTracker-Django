from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.urls import reverse
from Stocks.models import *
from django.urls import resolve

def admin_login(request):
    if request.user.is_authenticated:
        return redirect('admin_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username') 
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user is not None and user.is_superuser:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid credentials')
            return redirect(reverse('admin_login'))  # Redirect back to login page with error message

    return render(request, 'login.html')


# views.py
from django.shortcuts import render
from Stocks.models import FinancialData, SectorData

def admin_dashboard(request):
    latest_financial_data = FinancialData.objects.order_by('-date').first()
    latest_sector_data = SectorData.objects.order_by('-date').first()
    current_path = resolve(request.path_info).url_name
    context = {
        'latest_financial_data': latest_financial_data,
        'latest_sector_data': latest_sector_data,
        'current_path': current_path
    }
    return render(request, 'admindashboard.html', context)

def ema_counts_sectors(request):
    current_path = resolve(request.path_info).url_name
    context = {'current_path': current_path}
    obj = EmaCountsSector.objects.all()
    unique_symbols = EmaCountsSector.objects.values_list('stock_data__symbol', flat=True).distinct()
    return render(request, 'Ema_counts_sectors.html', {'obj': obj, 'unique_symbols': unique_symbols, 'context': context})

def ema_counts_stocks(request):
    current_path = resolve(request.path_info).url_name
    context = {'current_path': current_path}
    obj = EmaCounts.objects.all()
    unique_symbols = EmaCounts.objects.values_list('stock_data__symbol', flat=True).distinct()
    return render(request, 'Ema_counts_stocks.html', {'obj': obj, 'unique_symbols': unique_symbols, 'context': context})

def financial_data(request):
    current_path = resolve(request.path_info).url_name
    context = {'current_path': current_path}
    obj = FinancialData.objects.all()
    unique_symbols = FinancialData.objects.values_list('symbol', flat=True).distinct()
    return render(request, 'financial_data.html', {'obj': obj, 'unique_symbols': unique_symbols, 'context': context})

def sector_data(request):
    current_path = resolve(request.path_info).url_name
    context = {'current_path': current_path}
    obj = SectorData.objects.all()
    unique_symbols = SectorData.objects.values_list('symbol', flat=True).distinct()
    return render(request, 'sector_data.html', {'obj': obj, 'unique_symbols': unique_symbols, 'context': context})
