from django.urls import path
from . import views

urlpatterns = [
    path('',views.index,name="index"),
    path('login/',views.user_login,name="user_login"),
    # path('your-view/', your_view, name='your_view'),
    path('signup/',views.signup,name="signup"),
    path('forgotpassword/',views.forgetpassword,name="forgetpassword"),
    path('home/',views.home,name="home"),
    path('stocks/', views.stocks, name='stocks'),
    path('sectors/', views.sectors, name='sectors'),
    path('portfolio/', views.portfolio, name='portfolio'),
    path('closed-positions/', views.closed_positions, name='closed_positions'),
    path('settings/', views.settings, name='settings'),
    path('help/', views.help, name='help'),
    path('about/', views.about, name='about'),
    # path('fetch-and-store/', views.fetch_and_store_stock_data, name='fetch_and_store_stock_data'),
    path('fetch_and_calculate_ema/', views.fetch_and_calculate_ema, name='fetch_and_store_stock_data'),
    # path('display/', views.display_stock_data, name='display_stock_data'),
    # path('latest_rsi_data/', views.latest_rsi_data, name='latest_rsi_data'),
    # path('display_stock_data/', views.display_stock_data, name='display_stock_data'),
    # path('ema_counts/', views.ema_counts, name='ema_counts'),
    # path('count_ema/', views.count_function, name='ema_counts'),
    path('analyze/', views.analyze_closing_vs_ema, name='analyze_closing_vs_ema'),
    # path('graph/', views.graph, name='graph'),
    path('graph/<str:symbol>/<int:ema_value>/', views.graph, name='graph'),
]
    # path('graph/<str:symbol>/<int:ema_value>/', views.graph, name='graph'),

