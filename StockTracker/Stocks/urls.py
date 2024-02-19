from django.urls import path
from . import views

urlpatterns = [
    path('',views.index,name="index"),
    path('login/',views.user_login,name="user_login"),
    path('logout/',views.user_logout,name="user_logout"),
    path('verify/',views.verify,name="verify"),
    path('verify_password/',views.verify_password,name="verify_password"),
    path('subscription/', views.subscription, name='subscription'),
    path('leave_page/', views.leave_page, name='leave_page'),
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
    path('fetch_and_calculate_ema_sector/', views.fetch_and_calculate_ema_sector, name='fetch_and_calculate_ema_sector'),
    # path('display/', views.display_stock_data, name='display_stock_data'),
    # path('latest_rsi_data/', views.latest_rsi_data, name='latest_rsi_data'),
    # path('display_stock_data/', views.display_stock_data, name='display_stock_data'),
    # path('ema_counts/', views.ema_counts, name='ema_counts'),
    # path('count_ema/', views.count_function, name='ema_counts'),
    path('analyze_stocks/', views.analyze_closing_vs_ema, name='analyze_closing_vs_ema'),
    path('analyze_sector/', views.analyze_closing_vs_ema_sector, name='analyze_closing_vs_ema_sector'),
    # path('graph/', views.graph, name='graph'),
    path('graph/<str:symbol>/<int:ema_value>/', views.graph_partial, name='graph'),
    path('symbols/', views.symbols_and_ema_counts, name='symbols_and_closing_prices'),
    # path('dashboard/', views.sectoral_dashboard, name='sectoral_dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),  # URL for the sectoral dashboard
    path('dashboard/<int:ema>/', views.dashboard, name='dashboard_with_ema'),  # URL for the sectoral dashboard with selected EMA
    # path('logout/', views.logout_view, name='logout'),
    path('home_template/', views.home_temp, name='home_template'),
    path('stock_template/', views.stock_temp, name='stock_template'),
]
    # path('graph/<str:symbol>/<int:ema_value>/', views.graph, name='graph'),

