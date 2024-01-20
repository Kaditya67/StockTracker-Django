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