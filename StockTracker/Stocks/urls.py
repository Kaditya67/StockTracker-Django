from django.urls import path
from . import views

urlpatterns = [
    path('',views.index,name="index"),
    path('login/',views.login,name="login"),
    path('signup/',views.signup,name="signup"),
    path('forgotpassword/',views.forgetpassword,name="forgetpassword"),
    path('home/',views.home,name="home"),
    path('stocks/', views.stocks, name='stocks'),
    path('sectors/', views.sectors, name='sectors'),
    path('portfolio/', views.portfolio, name='portfolio'),
    path('settings/', views.settings, name='settings'),
    path('help/', views.help, name='help'),
    path('about/', views.about, name='about'),
]
