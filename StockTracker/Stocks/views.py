from django.contrib.auth import login, authenticate
from .forms import SignUpForm
from django.shortcuts import render, redirect,HttpResponse
from django.contrib.auth.forms import AuthenticationForm
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
    

def user_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Successfully Logged In")
            return redirect('home')  # Redirect to the home page or any other desired page
        else:
            print(f"Failed login attempt for user: {username}")
            messages.error(request, "Invalid credentials! Please try again")
            return render(request, "user_login.html")

    return render(request, "user_login.html")


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request)  # Log in the user after signup
            return redirect('login')  # Redirect to the home page or any other desired page
    else:
        form = SignUpForm()

    return render(request, 'signup.html', {'form': form})


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
