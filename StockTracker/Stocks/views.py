from django.shortcuts import render, redirect,HttpResponse
from django.contrib import messages
from .models import ContactInformation

def index(request):
    
    if request.method == 'POST':
        name=request.POST.get('name')
        email=request.POST.get('email')
        address=request.POST.get('address')
        contactinfo=ContactInformation(name=name,email=email,address=address)
        contactinfo.save()
        messages.success(request,"Contact Form Submitted !")

    return render(request,'index.html')
        


def login(request):
    return render(request,'login.html')

def signup(request):
    return render(request,'signup.html')

def forgetpassword(request):
    return render(request,'forgetpassword.html')

def home(request):
    return render(request,'home.html')

def stocks(request):
    return render(request, 'stocks.html')

def sectors(request):
    return render(request, 'sectors.html')

def portfolio(request):
    return render(request, 'portfolio.html')

def home(request):
    # stock_data = {
    #     'labels': ['Nifty 50', 'Bank Nifty', 'Nifty IT ', 'Nifty Auto'],
    #     'performance': [12, 19, 3, 15]
    # }
    return render(request, 'home.html')


def settings(request):
    return render(request, 'settings.html')


def help(request):
    return render(request, 'help.html')


def about(request):
    return render(request, 'about.html')
