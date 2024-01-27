from django.contrib.auth import login, authenticate
from .forms import SignUpForm
from django.shortcuts import render, redirect,HttpResponse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .models import ContactInformation
from django.contrib.auth.decorators import login_required

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


@login_required
def stocks(request):
    return render(request, 'stocks.html')


@login_required
def sectors(request):
    return render(request, 'sectors.html')


@login_required
def portfolio(request):
    return render(request, 'portfolio.html')

@login_required
def closed_positions(request):
    return render(request, 'closedpositions.html')

# @login_required
# def home(request):
#     stock_data = {
#         'labels': ['Nifty 50', 'Bank Nifty', 'Nifty IT ', 'Nifty Auto'],
#         'performance': [12, 19, 3, 15]
#     }
#     return render(request, 'home.html', {'stock_data': stock_data})

@login_required
def settings(request):
    return render(request, 'settings.html')

@login_required
def help(request):
    return render(request, 'help.html')

@login_required
def about(request):
    return render(request, 'about.html')

@login_required
def stocks(request):
    return render(request, 'stocks.html')

# # views.py
# import requests
# from django.shortcuts import render
# from .models import StockData
# from datetime import datetime

# def save_stock_data(api_data):
#     if 'Time Series (Daily)' in api_data:
#         time_series_data = api_data['Time Series (Daily)']

#         # Extract the last 20 days
#         last_20_days = list(time_series_data.items())[:20]

#         for date, values in last_20_days:
#             stock_data = StockData(
#                 symbol=api_data['Meta Data']['2. Symbol'],
#                 date=datetime.strptime(date, '%Y-%m-%d').date(),
#                 open_price=float(values['1. open']),
#                 high_price=float(values['2. high']),
#                 low_price=float(values['3. low']),
#                 close_price=float(values['4. close']),
#                 volume=int(values['5. volume'])
#             )
#             stock_data.save()
#     else:
#         print('Error: "Time Series (Daily)" key not found in API response')

# def your_view(request):
#     api_key = 'OJMC16ULZR2R12NR'
#     symbol = 'AAPL'  # Replace with the actual stock symbol you want to retrieve, for example: AAPL, GOOGL, MSFT, etc.

#     # Make the API request
#     api_url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}'
#     response = requests.get(api_url)

#     if response.status_code == 200:
#         api_data = response.json()

#         # Print the entire API response
#         print(api_data)

#         # Assuming the API response structure is similar to what you provided
#         save_stock_data(api_data)

#         # Now the data of the past 20 days is saved in the database
#         # You can use the data in your template or perform other operations

#         return render(request, 'your_template.html', {'api_data': api_data})
#     else:
#         # Handle the API request error
#         print(f'API request failed with status code: {response.status_code}')
#         return render(request, 'error_template.html', {'error_message': 'Failed to fetch stock data'})



# views.py
def display_stock_data(request):
    stock_data = StockData.objects.all()
    return render(request, 'admin_stock_data.html', {'stock_data': stock_data})
# views.py
from django.shortcuts import render
from .models import StockData
from datetime import datetime, timedelta
from .models import StockData, IndicatorValues 
from pandas_datareader import data as pdr
import yfinance as yf
import pandas as pd
import numpy as np


# Function to calculate EMA
def calculate_ema(data, column, span):
    return data[column].ewm(span=span, adjust=False).mean()

def calculate_rsi_and_rs(df, n=14):
    close_price_changes = df['Close'].diff()

    gains = close_price_changes.where(close_price_changes > 0, 0)
    losses = -close_price_changes.where(close_price_changes < 0, 0)

    average_gain = gains.rolling(window=n, min_periods=1).mean()
    average_loss = losses.rolling(window=n, min_periods=1).mean()

    rs = average_gain / average_loss
    rsi = 100 - (100 / (1 + rs))

    # Replace NaN and -inf values with None
    rsi.replace([np.nan, -np.inf], None, inplace=True)
    rs.replace([np.nan, -np.inf], None, inplace=True)

    return rsi, rs
def fetch_and_store_stock_data(request):
    # Database setup
    stock_symbols = ['AAPL', 'MSFT', 'GOOGL']
    num_days = 200  # Change to 200 to fetch data for the last 200 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=num_days * 2)

    # Override the data reader function
    yf.pdr_override()

    for symbol in stock_symbols:
        df = pdr.get_data_yahoo(symbol, start=start_date, end=end_date)
        df = df[['Close']].last(f'{num_days}D')  # Fetch data for the last 200 days

        # Calculate EMA
        df['EMA20'] = calculate_ema(df, 'Close', 20)
        df['EMA50'] = calculate_ema(df, 'Close', 50)
        df['EMA100'] = calculate_ema(df, 'Close', 100)
        df['EMA200'] = calculate_ema(df, 'Close', 200)

        # Calculate RSI and RS
        rsi, rs = calculate_rsi_and_rs(df)

        # Store in the database
        for idx, row in df.iterrows():
            stock_data = StockData(
                symbol=symbol,
                date=row.name,
                close_price=row['Close']
            )
            stock_data.save()

            # Create and save IndicatorValues instance
            indicator_values = IndicatorValues(
                stock_data=stock_data,
                ema20=row['EMA20'],
                ema50=row['EMA50'],
                ema100=row['EMA100'],
                ema200=row['EMA200'],
                rsi=None if pd.isna(rsi.loc[idx]) else rsi.loc[idx],
                rs=None if pd.isna(rs.loc[idx]) else rs.loc[idx]
            )
            indicator_values.save()

    return render(request, 'success.html')