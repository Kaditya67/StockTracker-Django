from django.shortcuts import render,HttpResponse
from django.contrib import messages


# Create your views here.
def index(request):
    # messages.success(request,"This is the test message")
    return render(request,'templates\index.html')