from django.contrib.auth import login, authenticate
from .forms import SignUpForm
from django.shortcuts import render, redirect,HttpResponse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .models import ContactInformation
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import SectorData, EmaCountsSector
from django.db.models import Max
from django.shortcuts import render
from django.urls import resolve

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from json.decoder import JSONDecodeError  # Import JSONDecodeError
from .models import stock_user  # Import the stock_user model
import json

@login_required
def fetch_sector_data(request):
    if request.method == 'POST':
        symbol = request.POST.get('symbol')
        user = request.user  # Get the current logged-in user
        try:
            # Fetch the latest data for the symbol from the database
            sector_data = SectorData.objects.filter(symbol=symbol).latest('date')
            # Serialize the data dictionary
            serialized_data = {
                'date': sector_data.date.strftime('%Y-%m-%d'),
                'symbol': sector_data.symbol,
                'closing_price': float(sector_data.close_price),  # Convert Decimal to float
            }
            # Get the user's watchlist_sector
            watchlist_sector = user.watchlist_sector
            if watchlist_sector:  # Check if watchlist_sector is not empty
                try:
                    watchlist_sector = json.loads(watchlist_sector)
                except JSONDecodeError:
                    # Handle invalid JSON data
                    watchlist_sector = []
            else:
                watchlist_sector = []
            # Append the serialized data to the watchlist_sector
            watchlist_sector.append(serialized_data)
            # Save the updated watchlist_sector to the user
            user.watchlist_sector = json.dumps(watchlist_sector)
            user.save()
            print(serialized_data)
            return JsonResponse({'success': True, 'data': serialized_data})
        except SectorData.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Sector data not found for the symbol.'})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method.'})


def watchlist(request):
    current_path = resolve(request.path_info).url_name
    user = request.user
    watchlist_sector = json.loads(user.watchlist_sector)
    return render(request, 'watchlist.html', {'watchlist_sector': watchlist_sector})

# Email

import http

from django.contrib.auth import login, authenticate
from django.core.mail import send_mail

from .forms import SignUpForm
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .models import ContactInformation
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random
import string
from django.urls import reverse
from .email_alerts import email_alert
from .utils import generate_otp
from .email_alerts import email_password


def leave_page(request):
    return render(request, 'leave_page.html')
def verify_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        # Check if the email and username match with database records
        user = User.objects.filter(email=email, username=username).first()
        if user:
            # Email and username match, proceed with password change
            if new_password == confirm_password:
                # Change the user's password
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password changed successfully.')
                return redirect('leave_page')
            else:
                messages.error(request, "Passwords don't match.")

        else:
            # Email or username do not match
            messages.error(request, "Invalid email address or username.")

    return render(request, 'verify_password.html')
    
def dashboard(request):
    """
    A view function to render the dashboard page with the latest data for each stock.
    Takes a request object and returns an HTML response with the dashboard template.
    """
    # Get the latest date for each stock
    latest_dates = SectorData.objects.values('symbol').annotate(latest_date=Max('date'))
    
    sector_data = []
    ema_counts = []
    rs_values = []
    symbols = []
    for stock in latest_dates:
        latest_sector_data = SectorData.objects.filter(symbol=stock['symbol'], date=stock['latest_date']).first()
        if latest_sector_data:
            sector_data.append(latest_sector_data)
            ema_count = EmaCountsSector.objects.filter(stock_data=latest_sector_data).first()
            if ema_count:
                ema_counts.append(ema_count)
                rs_values.append(ema_count.rs_output)
                symbols.append(latest_sector_data.symbol)

    selected_ema = request.GET.get('ema', '20')
    current_path = resolve(request.path_info).url_name
    
    context = {
        'sector_data': sector_data,
        'ema_counts': ema_counts,
        'rs_values': rs_values,
        'symbols': symbols,
        'selected_ema': selected_ema,
        'current_path': current_path,
    }

    # current_path = resolve(request.path_info).url_name
    # return render(request, 'dashboard.html', {'current_path': current_path, 'context': context})
    return render(request, 'dashboard.html', context)


def symbols_and_ema_counts(request):
    """
    Retrieve the latest record for each stock symbol.
    Retrieve the EMA counts for each latest entry.
    Pass the data to the template.
    """
    # Retrieve the latest record for each stock symbol
    latest_entries = FinancialData.objects.values('symbol').annotate(
        latest_date=Max('date')
    )

    # Retrieve the EMA counts for each latest entry
    symbols_and_ema_counts = [
        {
            'symbol': entry['symbol'],
            'ema20_count': EmaCounts.objects.filter(stock_data__symbol=entry['symbol'], stock_data__date=entry['latest_date']).values_list('ema20_output', flat=True).first()
        }
        for entry in latest_entries
    ]

    # Pass the data to the template
    return render(request, 'symbols_and_ema_counts.html', {'symbols_and_ema_counts': symbols_and_ema_counts})

def index(request):
        
    if request.method == 'POST':
        name=request.POST.get('name')
        email=request.POST.get('email')
        address=request.POST.get('address')
        contactinfo=ContactInformation(name=name,email=email,address=address)
        contactinfo.save()
        messages.success(request,"Contact Form Submitted !")

    return render(request,'index.html')
        
## User logout and verify

def subscription(request):
    return render(request, 'subscription.html')

def verify(request):
    if request.method == 'POST':
        print('Form submitted via POST request')
        user_entered_otp = request.POST.get('otp')
        otp_sent_to_email = request.session.get('otp_sent_to_email')
        print('User-entered OTP:', user_entered_otp)
        print('OTP sent to email:', otp_sent_to_email)

        if user_entered_otp == otp_sent_to_email:
            # OTP is correct, perform further actions
            # For example, mark the user as verified
            return redirect('user_login')
        else:
            # OTP is incorrect, show error message
            messages.error(request, 'Incorrect OTP. Please try again.')
            return render(request, 'verify.html')

    else:
        messages.error(request, 'Invalid form submission.')
        return render(request, 'verify.html')

def user_logout(request):
    logout(request)
    messages.success(request, "successfully logged out")
    return redirect('signup')

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .models import stock_user  # Import your custom user model

def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
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
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password1']
        confirm_password = request.POST['password2']

        if stock_user.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return redirect('signup')

        if password != confirm_password:
            messages.error(request, "Passwords didn't match!")
            return redirect('signup')

        if len(username) > 10:
            messages.error(request, "Username too long! Must be 10 characters or less.")
            return redirect('signup')

        if not username.isalnum():
            messages.error(request, "Username must be alphanumeric characters.")
            return redirect('signup')

        if password == confirm_password:
            # Create the user using your custom user model
            my_user = stock_user.objects.create_user(username=username, email=email, password=password)
            messages.success(request, "Account created successfully")
            
            # Redirect the user to the appropriate page after sign up
            return redirect('verify')  # Replace 'verify' with the name of your verification page
        else:
            messages.error(request, "Passwords don't match")
            return redirect('signup')

    return render(request, 'signup.html')


def forgetpassword(request):
    if request.method == 'GET':
        return render(request, 'forgetpassword.html')

    elif request.method == 'POST':
        email = request.POST.get('email')

        # Check if the email is valid (you may want to add more thorough validation)
        if email:


            # Compose the email body with the verification link
            email_subject = "Password Reset Request"
            email_body = f"Click the following link to reset your password: http://127.0.0.1:8000/verify_password/"

            # Send the verification email
            email_password(email_subject, email_body, email)

            # Optionally, you can display a success message
            messages.success(request, "An email with instructions to reset your password has been sent to your email address.")

        else:
            # If the email is empty, display an error message
            messages.error(request, "Please provide a valid email address.")

        return redirect('user_login')

    return render(request, 'forgetpassword.html')


# def home(request):
#     return render(request,'home.html')

from datetime import timedelta
from django.utils import timezone
from django.shortcuts import render
from .models import FinancialData, EmaCounts
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
import logging

def calculate_Stocks_ema20(stock_symbol):

    # Get the current date
    current_date = timezone.now().date()-timedelta(days=40)

    # Calculate the date 20 days ago
    start_date = current_date - timedelta(days=200)

    # Retrieve the most recent 20 data points for the stock symbol
    data_points = FinancialData.objects.filter(
        symbol=stock_symbol,
        date__range=[start_date, current_date]
    ).order_by('-date').values_list('symbol', 'date', 'ema20', 'close_price')[:20]

    if not data_points:
        return 0

    ema20_counter = 0
    for symbol, date, ema20, close_price in data_points:

        if close_price > ema20:
            if ema20_counter < 0:
                ema20_counter = 1
            else:
                ema20_counter += 1
        elif close_price < ema20:
            if ema20_counter > 0:
                ema20_counter = -1
            else:
                ema20_counter -= 1
    print(stock_symbol, ema20_counter)
    return ema20_counter

@login_required
def stocks(request):
    unique_symbols =FinancialData.objects.values_list('symbol', flat=True).distinct()
    unique_symbols = unique_symbols[:20]

    result = []
    for stock_symbol in unique_symbols:
        # Get the current date
        current_date = timezone.now().date()

        # Calculate the date 20 days ago
        start_date = current_date - timedelta(days=40)

        # Retrieve the most recent 20 data points for the stock symbol
        data_points = FinancialData.objects.filter(
            symbol=stock_symbol,
            date__range=[start_date, current_date]
        ).order_by('date').values_list('symbol', 'date', 'ema20', 'close_price')[:20]

        if not data_points:
            continue
        date_list=[]

        ema20_counter = calculate_Stocks_ema20(stock_symbol)
        for symbol, date, ema20, close_price in data_points:
            if date not in date_list:
                date_list.append(date)
            if ema20_counter > 0:
                if close_price < ema20:
                    ema20_counter =-1
                else:
                    ema20_counter += 1
            else:
                if close_price > ema20:
                    ema20_counter =1
                else:
                    ema20_counter -= 1
            result.append((symbol, date, ema20_counter))

    print(date_list)
    current_path = resolve(request.path_info).url_name
    context = {
        'result': result,
        'unique_symbols': unique_symbols,
        'date_list': date_list,
        'current_path': current_path
    }
    return render(request, 'stocks.html', context)



# def stocks(request):
    # # Get the distinct stock symbols
    # stock_symbols = FinancialData.objects.values_list('symbol', flat=True).distinct()
    
    # # Get the selected stock symbol from the query parameter
    # symbol = request.GET.get('symbol')
    
    # # Initialize variables to store closing prices and calculate EMA20
    # closing_prices = []
    # ema20_values = []
    
    # if symbol:
    #     # Get the current date
    #     current_date = timezone.now().date()
        
    #     # Calculate the date 20 days ago
    #     start_date = current_date - timedelta(days=20)
        
    #     # Query financial data for the selected stock and date range
    #     financial_data = FinancialData.objects.filter(symbol=symbol, date__range=[start_date, current_date]).order_by('date')
        
    #     # Calculate EMA20 for the past 20 days
    #     k = 2 / (20 + 1)  # EMA smoothing factor
    #     for data_point in financial_data:
    #         closing_prices.append(data_point.close_price)
    #         if len(closing_prices) == 1:
    #             ema20 = data_point.close_price
    #         else:
    #             ema20 = (data_point.close_price - ema20_values[-1]) * k + ema20_values[-1]
    #         ema20_values.append(ema20)
        
    #     # Save the EMA20 count to the database
    #     ema20_count = sum(1 for price in closing_prices[-20:] if price > ema20_values[-1])
    #     ema_counts_instance, created = EmaCounts.objects.get_or_create(
    #         stock_data=financial_data.last(),
    #         defaults={'ema20_output': ema20_count}
    #     )
    # else:
    #     financial_data = None
    #     ema20_count = None
    
    # current_path = resolve(request.path_info).url_name

    # return render(request, 'stocks.html', {'current_path': current_path, 'stock_symbols': stock_symbols, 'financial_data': financial_data, 'ema20_values': ema20_values, 'ema20_count': ema20_count})

def calculate_ema20(stock_symbol):

    # Get the current date
    current_date = timezone.now().date()-timedelta(days=40)

    # Calculate the date 20 days ago
    start_date = current_date - timedelta(days=200)

    # Retrieve the most recent 20 data points for the stock symbol
    data_points = SectorData.objects.filter(
        symbol=stock_symbol,
        date__range=[start_date, current_date]
    ).order_by('-date').values_list('symbol', 'date', 'ema20', 'close_price')[:20]

    if not data_points:
        return 0

    ema20_counter = 0
    for symbol, date, ema20, close_price in data_points:

        if close_price > ema20:
            if ema20_counter < 0:
                ema20_counter = 1
            else:
                ema20_counter += 1
        elif close_price < ema20:
            if ema20_counter > 0:
                ema20_counter = -1
            else:
                ema20_counter -= 1
    #print(stock_symbol, ema20_counter)
    return ema20_counter

@login_required
def sectors(request):
    unique_symbols = SectorData.objects.values_list('symbol', flat=True).distinct()
    unique_symbols = unique_symbols[:20]

    result = []
    for stock_symbol in unique_symbols:
        # Get the current date
        current_date = timezone.now().date()

        # Calculate the date 20 days ago
        start_date = current_date - timedelta(days=40)

        # Retrieve the most recent 20 data points for the stock symbol
        data_points = SectorData.objects.filter(
            symbol=stock_symbol,
            date__range=[start_date, current_date]
        ).order_by('date').values_list('symbol', 'date', 'ema20', 'close_price')[:20]

        if not data_points:
            continue
        date_list=[]

        ema20_counter = calculate_ema20(stock_symbol)
        for symbol, date, ema20, close_price in data_points:
            if date not in date_list:
                date_list.append(date)
            if ema20_counter > 0:
                if close_price < ema20:
                    ema20_counter =-1
                else:
                    ema20_counter += 1
            else:
                if close_price > ema20:
                    ema20_counter =1
                else:
                    ema20_counter -= 1
            result.append((symbol, date, ema20_counter))

    # print(date_list)
    current_path = resolve(request.path_info).url_name
    context = {
        'result': result,
        'unique_symbols': unique_symbols,
        'date_list': date_list,
        'current_path': current_path
    }
    return render(request, 'sectors.html', context)


@login_required
def portfolio(request):
    current_path = resolve(request.path_info).url_name
    return render(request, 'portfolio.html',{'current_path': current_path})

def home_temp(request):
    current_path = resolve(request.path_info).url_name
    return render(request, 'home_template.html',{'current_path': current_path})
    
import logging
from datetime import timedelta
from django.shortcuts import render
from django.utils import timezone
from django.urls import resolve
from .models import FinancialData

logger = logging.getLogger(__name__)

def stock_temp(request):
    logger.debug("Os Errors come to me")

    unique_symbols = FinancialData.objects.values_list('symbol', flat=True).distinct()
    unique_symbols = unique_symbols[:20]

    result = []
    for stock_symbol in unique_symbols:
        current_date = timezone.now().date()
        start_date = current_date - timedelta(days=200)

        data_points = FinancialData.objects.filter(
            symbol=stock_symbol,
            date__range=[start_date, current_date]
        ).order_by('-date').values_list('date', 'ema20', 'close_price')

        if not data_points:
            continue

        ema20_counter = 0
        for date, ema20, close_price in data_points:
            if ema20 is None:
                continue
            if close_price > ema20:
                if ema20_counter < 0:
                    break
                ema20_counter += 1
                result.append((date, ema20_counter))
            elif close_price < ema20:
                if ema20_counter > 0:
                    break
                ema20_counter -= 1
                result.append((date, ema20_counter))

    logger.debug(f"Result: {result}")

    context = {
        'result': result
    }
    logger.debug("Rendering stock_template.html template with context")
    current_path = resolve(request.path_info).url_name
    return render(request, 'stock_template.html', context)


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
    current_path = resolve(request.path_info).url_name
    return render(request, 'settings.html', {'current_path': current_path})

@login_required
def help(request):
    current_path = resolve(request.path_info).url_name
    return render(request, 'help.html', {'current_path': current_path})

@login_required
def about(request):
    current_path = resolve(request.path_info).url_name
    return render(request, 'about.html', {'current_path': current_path})

########################################## Calculating Values ##################################
## Adding new Stocks data
# views.py
from django.shortcuts import render
from .models import FinancialData
from datetime import datetime, timedelta
from pandas_datareader import data as pdr
# import yfinance as yf
import yahoo_fin as yf
import pandas as pd
import numpy as np
from django.shortcuts import render
from .models import FinancialData,SectorData
from datetime import datetime, timedelta
from pandas_datareader import data as pdr
import yfinance as yf
import pandas as pd
import numpy as np

def calculate_rsi(df, n=14):
    """
    Calculate the Relative Strength Index (RSI) for the given dataframe.

    Parameters:
    df (DataFrame): The input dataframe containing the 'Close' prices.
    n (int): The number of periods to consider for the RSI calculation (default is 14).

    Returns:
    rsi (Series): The calculated Relative Strength Index.
    """
    close_price_changes = df['Close'].diff()

    gains = close_price_changes.where(close_price_changes > 0, 0)
    losses = -close_price_changes.where(close_price_changes < 0, 0)

    average_gain = gains.rolling(window=n, min_periods=1).mean()
    average_loss = losses.rolling(window=n, min_periods=1).mean()

    rs = average_gain / average_loss
    rsi = 100 - (100 / (1 + rs))

    # Replace NaN and -inf values with None
    rsi.replace([np.nan, -np.inf], None, inplace=True)

    return rsi

def calculate_rs(df, nifty_df, n=14, start_column='Open', close_column='Close'):
    """
    Calculate the Relative Strength (RS) for the given dataframe over a span of n days.

    Parameters:
    df (DataFrame): The input dataframe containing the asset's prices.
    nifty_df (DataFrame): The Nifty 50 dataframe containing the NIFTY50's prices.
    n (int): The number of periods to consider for the RS calculation (default is 14).
    start_column (str): The column name representing the starting price of the asset (default is 'Open').
    close_column (str): The column name representing the closing price of the asset (default is 'Close').

    Returns:
    rs (Series): The calculated Relative Strength.
    """
    # Calculate percentage change in asset's price over the past n days
    asset_percentage_change = ((df[close_column] - df[start_column].shift(n)) / df[start_column].shift(n)) * 100

    # Calculate percentage change in NIFTY50's price over the past n days
    nifty_percentage_change = ((nifty_df[close_column] - nifty_df[start_column].shift(n)) / nifty_df[start_column].shift(n)) * 100

    # Calculate RS
    rs = asset_percentage_change / nifty_percentage_change

    return rs

def fetch_and_calculate_ema(request):
    """
    Fetches stock data, calculates EMA, RSI, RS, and stores the data in the database.
    Args:
        request: The HTTP request object.
    Returns:
        A rendered HTML page with the result data.
    """
    # Database setup
    stock_symbols = [
        'RELIANCE.NS', 'TATAMOTORS.NS', 'HDFCBANK.NS', 'INFY.NS', 'TATASTEEL.NS',
        'ZEEL.NS', 'HAVELLS.NS', 'HDFC.NS', 'ITC.NS', 'NESTLEIND.NS',
        'ICICIBANK.NS', 'HINDALCO.NS', 'DRREDDY.NS', 'WIPRO.NS', 'MARUTI.NS'
    ]

    # Override the data reader function
    yf.pdr_override()

    result_data = []

    for symbol in stock_symbols:
        # Check if data for the symbol is already present in the database
        latest_data = FinancialData.objects.filter(symbol=symbol).order_by('-date').first()

        if latest_data is not None:
            # Check if the latest data is up-to-date (within the last day)
            if (datetime.now().date() - latest_data.date).days <= 1:
                # Skip fetching new data if it's up-to-date
                continue

        # Fetch new data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=400)  # Fetch data for the last 400 days

        try:
            df_new = pdr.get_data_yahoo(symbol, start=start_date, end=end_date)
        except Exception as e:
            print(f"Failed to fetch data for {symbol}: {e}")
            continue

        df_new['Date'] = pd.to_datetime(df_new.index)  # Convert index to DatetimeIndex
        df_new = df_new.set_index('Date')  # Set 'Date' as the new index

        # Ensure 'Close' column is present in the new dataframe
        if 'Close' not in df_new.columns:
            # Handle the situation where 'Close' is not present
            # You might want to log a message or handle it based on your requirements
            continue

        # Calculate EMA
        ema20 = df_new['Close'].ewm(span=20, adjust=False).mean()
        ema50 = df_new['Close'].ewm(span=50, adjust=False).mean()
        ema100 = df_new['Close'].ewm(span=100, adjust=False).mean()
        ema200 = df_new['Close'].ewm(span=200, adjust=False).mean()

        # Calculate RSI
        rsi = calculate_rsi(df_new)

        # Fetch NIFTY50 data
        try:
            nifty_df = pdr.get_data_yahoo('^NSEI', start=start_date, end=end_date)
        except Exception as e:
            print(f"Failed to fetch NIFTY50 data: {e}")
            continue

        # Calculate RS
        rs = calculate_rs(df_new, nifty_df)

        # Store in the database
        for idx, row in df_new.iterrows():
            financial_data, created = FinancialData.objects.get_or_create(
                symbol=symbol,
                date=row.name,
                defaults={
                    'close_price': row['Close'],
                    'ema20': None if pd.isna(ema20.loc[idx]) else ema20.loc[idx],
                    'ema50': None if pd.isna(ema50.loc[idx]) else ema50.loc[idx],
                    'ema100': None if pd.isna(ema100.loc[idx]) else ema100.loc[idx],
                    'ema200': None if pd.isna(ema200.loc[idx]) else ema200.loc[idx],
                    'rsi': None if pd.isna(rsi.loc[idx]) else rsi.loc[idx],
                    'rs': None if pd.isna(rs.loc[idx]) else rs.loc[idx],
                    # Add other indicator values as needed
                }
            )

            result_data.append({
                'symbol': symbol,
                'date': row.name,
                'close_price': row['Close'],
                'ema20': ema20.loc[idx],
                'ema50': ema50.loc[idx],
                'ema100': ema100.loc[idx],
                'ema200': ema200.loc[idx],
                'rsi': rsi.loc[idx],
                'rs': rs.loc[idx],
                # Add other indicator values as needed
            })

    return render(request, 'fetch_and_calculate_ema.html', {'result_data': result_data})

def fetch_and_calculate_ema_sector(request):
    """
    Fetches stock data, calculates EMA, RSI, RS, and stores the data in the database.
    Args:
        request: The HTTP request object.
    Returns:
        A rendered HTML page with the result data.
    """
    # Database setup
    stock_symbols = [
        '^NSEI','^CNXAUTO','^NSEBANK','^NIFTYFIN','^CNXFMCG','^CNXPHARMA','^CNXIT','^CNXMEDIA','^CNXMETAL','^CNXPHARMA','^CNXPSUBANK','^CNXIT','^CNXPSUBANK','^CNXREALTY','^CNXCONSUMERDUR','^NSEI:ONGC-NSEI:RELIANCE-NSEI:GAIL-NSEI:BPCL-NSEI:IOC'  
    ]

    # Override the data reader function
    yf.pdr_override()

    result_data = []

    for symbol in stock_symbols:
        # Check if data for the symbol is already present in the database
        latest_data = SectorData.objects.filter(symbol=symbol).order_by('-date').first()

        if latest_data is not None:
            # Check if the latest data is up-to-date (within the last day)
            if (datetime.now().date() - latest_data.date).days <= 1:
                # Skip fetching new data if it's up-to-date
                continue

        # Fetch new data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=400)  # Fetch data for the last 400 days

        try:
            df_new = pdr.get_data_yahoo(symbol, start=start_date, end=end_date)
        except Exception as e:
            print(f"Failed to fetch data for {symbol}: {e}")
            continue

        df_new['Date'] = pd.to_datetime(df_new.index)  # Convert index to DatetimeIndex
        df_new = df_new.set_index('Date')  # Set 'Date' as the new index

        # Ensure 'Close' column is present in the new dataframe
        if 'Close' not in df_new.columns:
            # Handle the situation where 'Close' is not present
            # You might want to log a message or handle it based on your requirements
            continue

        # Calculate EMA
        ema20 = df_new['Close'].ewm(span=20, adjust=False).mean()
        ema50 = df_new['Close'].ewm(span=50, adjust=False).mean()
        ema100 = df_new['Close'].ewm(span=100, adjust=False).mean()
        ema200 = df_new['Close'].ewm(span=200, adjust=False).mean()

        # Calculate RSI
        rsi = calculate_rsi(df_new)

        # Fetch NIFTY50 data
        try:
            nifty_df = pdr.get_data_yahoo('^NSEI', start=start_date, end=end_date)
        except Exception as e:
            print(f"Failed to fetch NIFTY50 data: {e}")
            continue

        # Calculate RS
        rs = calculate_rs(df_new, nifty_df)

        # Store in the database
        for idx, row in df_new.iterrows():
            sector_data, created = SectorData.objects.get_or_create(
                symbol=symbol,
                date=row.name,
                defaults={
                    'close_price': row['Close'],
                    'ema20': None if pd.isna(ema20.loc[idx]) else ema20.loc[idx],
                    'ema50': None if pd.isna(ema50.loc[idx]) else ema50.loc[idx],
                    'ema100': None if pd.isna(ema100.loc[idx]) else ema100.loc[idx],
                    'ema200': None if pd.isna(ema200.loc[idx]) else ema200.loc[idx],
                    'rsi': None if pd.isna(rsi.loc[idx]) else rsi.loc[idx],
                    'rs': None if pd.isna(rs.loc[idx]) else rs.loc[idx],
                    # Add other indicator values as needed
                }
            )

            result_data.append({
                'symbol': symbol,
                'date': row.name,
                'close_price': row['Close'],
                'ema20': ema20.loc[idx],
                'ema50': ema50.loc[idx],
                'ema100': ema100.loc[idx],
                'ema200': ema200.loc[idx],
                'rsi': rsi.loc[idx],
                'rs': rs.loc[idx],
                # Add other indicator values as needed
            })

    return render(request, 'fetch_and_calculate_ema.html', {'result_data': result_data})


# # views.py
# from django.shortcuts import render
# from .models import FinancialData, EmaCounts

# def calculate_ema_counters(closing_prices, ema_values):
#     ema_counter = 0

#     for i, closing_price in enumerate(closing_prices):
#         if i < len(ema_values):
#             try:
#                 ema_value = float(ema_values[i])
#                 if i == 0:
#                     # Initialize counter for the newest date
#                     if closing_price > ema_value:
#                         ema_counter = 1
#                     else:
#                         ema_counter = -1
#                 else:
#                     # Compare closing price with EMA for the rest of the dates
#                     if closing_price > ema_value:
#                         ema_counter += 1
#                     else:
#                         break  # Break the loop if behavior changes
#             except ValueError:
#                 # Handle the case where ema_values contain non-numeric values
#                 break
#         else:
#             # Handle the case where the ema_values list is shorter than the closing_prices list
#             break

#     return ema_counter

#def calculate_ema_counts(stock_data):
#   ema_counts, created = EmaCounts.objects.get_or_create(stock_data=stock_data)

    # Split ema_output fields only if they are not empty
#    ema20_values = [value for value in ema_counts.ema20_output.split(',') if value]
#    ema50_values = [value for value in ema_counts.ema50_output.split(',') if value]
#    ema100_values = [value for value in ema_counts.ema100_output.split(',') if value]
#    ema200_values = [value for value in ema_counts.ema200_output.split(',') if value]

    # Get historical financial data for the current stock, ordered by date
#    historical_data = FinancialData.objects.filter(symbol=stock_data.symbol).order_by('-date')
#    closing_prices = [data.close_price for data in historical_data]

    # Calculate counters for each EMA
#    ema_counts.ema20_counter = calculate_ema_counters(closing_prices, ema20_values)
#    ema_counts.ema50_counter = calculate_ema_counters(closing_prices, ema50_values)
#    ema_counts.ema100_counter = calculate_ema_counters(closing_prices, ema100_values)
#    ema_counts.ema200_counter = calculate_ema_counters(closing_prices, ema200_values)

    # Save the counters to the respective fields in EmaCounts model
#    ema_counts.save()

#    return ema_counts

# Ema Count
    
from django.shortcuts import render
from Stocks.models import FinancialData, EmaCounts,SectorData
from datetime import timedelta
from django.utils import timezone

def home(request):
    # Fetch distinct stock symbols from the database
    stock_symbols = FinancialData.objects.values_list('symbol', flat=True).distinct()

    # Fetch the latest EMA values for each EMA period
    ema20_values = FinancialData.objects.values_list('ema20', flat=True).order_by('-date')[:1]
    ema50_values = FinancialData.objects.values_list('ema50', flat=True).order_by('-date')[:1]
    ema100_values = FinancialData.objects.values_list('ema100', flat=True).order_by('-date')[:1]
    ema200_values = FinancialData.objects.values_list('ema200', flat=True).order_by('-date')[:1]

    context = {
        'stock_symbols': stock_symbols,
        'ema20_values': ema20_values,
        'ema50_values': ema50_values,
        'ema100_values': ema100_values,
        'ema200_values': ema200_values,
    }

    current_path = resolve(request.path_info).url_name
    return render(request, 'home.html', {'current_path': current_path, 'context': context})
def analyze_closing_vs_ema(request):
    """
    This function analyzes the closing vs EMA for a given request. It retrieves financial data for unique stock symbols, calculates various moving averages and closing prices, and then creates and saves EmaCounts instances for each stock. Finally, it passes the results to the template for rendering.
    """
    # Get the unique stock symbols
    unique_symbols = FinancialData.objects.values_list('symbol', flat=True).distinct()

    # Limit the number of EmaCounts records to 20 (one for each distinct stock)
    unique_symbols = unique_symbols[:20]


    # Iterate through each stock symbol
    for stock_symbol in unique_symbols:
        # Get the current date
        current_date = timezone.now().date()

        # Calculate the date 200 days ago
        start_date = current_date - timedelta(days=200)

        # Retrieve ema20, ema50, ema100, and ema200, and closing prices for the specified stock and date range
        data_points = FinancialData.objects.filter(
            symbol=stock_symbol,
            date__range=[start_date, current_date]
        ).order_by('-date').values_list('date', 'ema20', 'ema50', 'ema100', 'ema200', 'close_price','rsi','rs')

        # Check if any data points were retrieved
        if not data_points:
            continue

        # Initialize counters
        ema20_counter = 0
        ema50_counter = 0
        ema100_counter = 0
        ema200_counter = 0
        rsi_counter=0
        rs_counter=0

        for date, _, _, _,_, _,rsi,_ in data_points:
            # Calculate starting counters for EMA200
            if rsi >= 50.00:
                if rsi_counter < 0:
                    break
                rsi_counter += 1
            else:
                if rsi_counter > 0:
                    break
                rsi_counter -= 1
        for date, _, _, _,_, _,_,rs in data_points:
            # Calculate starting counters for EMA200
            if rs >= 1:
                if rs_counter < 0:
                    break
                rs_counter += 1
            else:
                if rs_counter > 0:
                    break
                rs_counter -= 1

        # Iterate through data points from newest to oldest date for EMA20
        for date, ema20, _, _, _, close_price,_,_ in data_points:
            # Calculate starting counters for EMA20
            if close_price > ema20:
                if ema20_counter < 0:
                    break
                ema20_counter += 1
            elif close_price < ema20:
                if ema20_counter > 0:
                    break
                ema20_counter -= 1

        # Repeat the same structure for EMA50
        for date, _, ema50, _, _, close_price,_,_ in data_points:
            # Calculate starting counters for EMA50
            if close_price > ema50:
                if ema50_counter < 0:
                    break
                ema50_counter += 1
            elif close_price < ema50:
                if ema50_counter > 0:
                    break
                ema50_counter -= 1

        # Repeat the same structure for EMA100
        for date, _, _, ema100, _, close_price,_,_ in data_points:
            # Calculate starting counters for EMA100
            if close_price > ema100:
                if ema100_counter < 0:
                    break
                ema100_counter += 1
            elif close_price < ema100:
                if ema100_counter > 0:
                    break
                ema100_counter -= 1

        newest_date = None
        # Repeat the same structure for EMA200
        for date, _, _, _, ema200, close_price,_,_ in data_points:
            # Calculate starting counters for EMA200
            if close_price > ema200:
                if ema200_counter < 0:
                    break
                ema200_counter += 1
            elif close_price < ema200:
                if ema200_counter > 0:
                    break
                ema200_counter -= 1
        

         # Store the newest date
            if newest_date is None or date > newest_date:
                newest_date = date

        # Create and save only one EmaCounts instance for each stock
        name = f"{stock_symbol}_{newest_date}"  # Modify the name-like field
        ema_counts_instance, created = EmaCounts.objects.get_or_create(
            stock_data=FinancialData.objects.get(symbol=stock_symbol, date=newest_date),
            defaults={
                'ema20_output': ema20_counter,
                'ema50_output': ema50_counter,
                'ema100_output': ema100_counter,
                'ema200_output': ema200_counter,
                'rsi_output': rsi_counter,
                'rs_output': rs_counter
            },
        )

        # ema_counts_instance, created = EmaCounts.objects.get_or_create(
        #     stock_data=FinancialData.objects.get(symbol=stock_symbol, date=newest_date),
        #     defaults={'ema20_output': ema20_counter, 'ema50_output': ema50_counter,
        #               'ema100_output': ema100_counter, 'ema200_output': ema200_counter,
        #               'rsi_output':rsi_counter,'rs_output':rs_counter
        #               },
        # )
        ema_counts_instance.save()

        # print(f"Starting ema20_counter for {stock_symbol} = {ema20_counter}")
        # print(f"Starting ema50_counter for {stock_symbol} = {ema50_counter}")
        # print(f"Starting ema100_counter for {stock_symbol} = {ema100_counter}")
        # print(f"Starting ema200_counter for {stock_symbol} = {ema200_counter}")

    # Pass the results to the template
    context = {'result_list': []}  # Empty list as no results are being passed to the template
    return render(request, 'analyze_output.html', context)

from django.shortcuts import render
from .models import SectorData, EmaCountsSector
from django.utils import timezone
from datetime import timedelta
from datetime import timedelta

def analyze_closing_vs_ema_sector(request):
    """
    This function analyzes the closing vs EMA for a given request. It retrieves financial data for unique stock symbols, calculates various moving averages and closing prices, and then creates and saves EmaCounts instances for each stock. Finally, it passes the results to the template for rendering.
    """
    # Get the unique stock symbols
    unique_symbols = SectorData.objects.values_list('symbol', flat=True).distinct()

    # Limit the number of EmaCounts records to 20 (one for each distinct stock)
    unique_symbols = unique_symbols[:20]

    # Iterate through each stock symbol
    for stock_symbol in unique_symbols:
        # Get the current date
        current_date = timezone.now().date()

        # Calculate the date 200 days ago
        start_date = current_date - timedelta(days=200)

        # Retrieve ema20, ema50, ema100, and ema200, and closing prices for the specified stock and date range
        data_points = SectorData.objects.filter(
            symbol=stock_symbol,
            date__range=[start_date, current_date]
        ).order_by('-date').values_list('date', 'ema20', 'ema50', 'ema100', 'ema200', 'close_price', 'rsi', 'rs')

        # Check if any data points were retrieved
        if not data_points:
            continue

        # Initialize counters
        ema20_counter = 0
        ema50_counter = 0
        ema100_counter = 0
        ema200_counter = 0
        rsi_counter = 0
        rs_counter = 0

        for date, _, _, _, _, _, rsi, _ in data_points:
            # Calculate starting counters for RSI
            if rsi is not None:
                if rsi >= 50.00:
                    if rsi_counter < 0:
                        break
                    rsi_counter += 1
                else:
                    if rsi_counter > 0:
                        break
                    rsi_counter -= 1

        for date, _, _, _, _, _, _, rs in data_points:
            # Calculate starting counters for RS
            if rs is not None:
                if rs >= 1:
                    if rs_counter < 0:
                        break
                    rs_counter += 1
                else:
                    if rs_counter > 0:
                        break
                    rs_counter -= 1

        # Iterate through data points from newest to oldest date for EMA20
        for date, ema20, _, _, _, close_price, _, _ in data_points:
            # Calculate starting counters for EMA20
            if ema20 is not None:
                if close_price > ema20:
                    if ema20_counter < 0:
                        break
                    ema20_counter += 1
                elif close_price < ema20:
                    if ema20_counter > 0:
                        break
                    ema20_counter -= 1

        # Repeat the same structure for EMA50
        for date, _, ema50, _, _, close_price, _, _ in data_points:
            # Calculate starting counters for EMA50
            if ema50 is not None:
                if close_price > ema50:
                    if ema50_counter < 0:
                        break
                    ema50_counter += 1
                elif close_price < ema50:
                    if ema50_counter > 0:
                        break
                    ema50_counter -= 1

        # Repeat the same structure for EMA100
        for date, _, _, ema100, _, close_price, _, _ in data_points:
            # Calculate starting counters for EMA100
            if ema100 is not None:
                if close_price > ema100:
                    if ema100_counter < 0:
                        break
                    ema100_counter += 1
                elif close_price < ema100:
                    if ema100_counter > 0:
                        break
                    ema100_counter -= 1

        # Repeat the same structure for EMA200
        for date, _, _, _, ema200, close_price, _, _ in data_points:
            # Calculate starting counters for EMA200
            if ema200 is not None:
                if close_price > ema200:
                    if ema200_counter < 0:
                        break
                    ema200_counter += 1
                elif close_price < ema200:
                    if ema200_counter > 0:
                        break
                    ema200_counter -= 1

        newest_date = None
        # Store the newest date
        for date, _, _, _, _, _, _, _ in data_points:
            if newest_date is None or date > newest_date:
                newest_date = date

        # Create and save only one EmaCounts instance for each stock
        name = f"{stock_symbol}_{newest_date}"  # Modify the name-like field
        ema_counts_instance, created = EmaCountsSector.objects.get_or_create(
            stock_data=SectorData.objects.get(symbol=stock_symbol, date=newest_date),
            defaults={
                'ema20_output': ema20_counter,
                'ema50_output': ema50_counter,
                'ema100_output': ema100_counter,
                'ema200_output': ema200_counter,
                'rsi_output': rsi_counter,
                'rs_output': rs_counter
            },
        )

        ema_counts_instance.save()

    # Pass the results to the template
    context = {'result_list': []}  # Empty list as no results are being passed to the template
    return render(request, 'analyze_output.html', context)

#### Graph Calculations ########

# views.py
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from io import BytesIO
import base64
import matplotlib.pyplot as plt
from django.urls import resolve
from .models import FinancialData

def graph_partial(request, symbol, ema_value):
    """
    Fetches the latest 200 records of financial data based on the provided symbol and plots the closing prices and EMA values over the past 200 records. 
    Parameters:
        request: The HTTP request object
        symbol: The symbol for the financial data
        ema_value: The value for the EMA calculation
    Returns:
        HTML rendering of the graph_partial.html template with the selected symbol, base64 encoded image, and distinct stock symbols
    """
    try:
        # Fetch the latest 200 records based on the symbol
        data = FinancialData.objects.filter(symbol=symbol).order_by('-id')[:200].values('date', 'close_price', f'ema{ema_value}')

        # Unpack the data into separate lists
        dates = [entry['date'] for entry in data][::-1]  # Reverse the order to show the progress from the past
        closing_prices = [entry['close_price'] for entry in data][::-1]
        ema_values = [entry[f'ema{ema_value}'] for entry in data][::-1]

        # Plotting
        plt.figure(figsize=(11, 6))
        plt.plot(dates, closing_prices, label=f'{symbol} Closing Prices')
        plt.plot(dates, ema_values, label=f'{symbol} EMA{ema_value}')  # Corrected this line

        plt.xlabel('Date')
        plt.ylabel('Values')
        plt.title(f'{symbol} Closing Prices and EMA Values Over the Past 200 Records')
        plt.legend(loc='upper left')

        # Encode the image as base64
        img_buf = BytesIO()
        plt.savefig(img_buf, format='png')
        plt.close()

        img_buf.seek(0)
        img_base64 = base64.b64encode(img_buf.getvalue()).decode('utf-8')

        stock = FinancialData.objects.values_list('symbol', flat=True).distinct()
        current_path = resolve(request.path_info).url_name
        # Render the graph as HTML
        current_path = resolve(request.path_info).url_name

        context = {
            'selected_symbol': symbol,
            'img_base64': img_base64,
            'stock': stock,
            'current_path': current_path,
        }
        return render(request, 'graph_partial.html', context)

    except Exception as e:
        # Handle specific exceptions if possible
        return HttpResponse(f"Error: {e}")

# views.py
def get_stock_data(request):
    symbol = request.GET.get('symbol', None)

    if symbol:
        stock_data = FinancialData.objects.filter(symbol=symbol)
        dates = [data_point.date for data_point in stock_data]
        closing_prices = [data_point.close_price for data_point in stock_data]
        ema20_values = [data_point.ema20 for data_point in stock_data]
        ema50_values = [data_point.ema50 for data_point in stock_data]
        ema100_values = [data_point.ema100 for data_point in stock_data]
        ema200_values = [data_point.ema200 for data_point in stock_data]

        return JsonResponse({
            'dates': dates,
            'closing_prices': closing_prices,
            'ema20_values': ema20_values,
            'ema50_values': ema50_values,
            'ema100_values': ema100_values,
            'ema200_values': ema200_values,
        })

    return JsonResponse({'error': 'Invalid symbol'})

def stock_list(request):
    stock_symbols = FinancialData.objects.values_list('symbol', flat=True).distinct()
    return render(request, 'home.html', {'stock_symbols': stock_symbols})

# views.py
from django.shortcuts import render
from django.urls import resolve
from .models import FinancialData



################################ Comments ####################################################

# def count_function(request):
#     # Get all distinct stock symbols
#     stocks_symbols = FinancialData.objects.values('symbol').distinct()

#     ema_counts_list = []

#     # Iterate over each stock symbol
#     for stock_symbol in stocks_symbols:
#         stock_symbol = stock_symbol['symbol']

#         # Get the latest financial data for the current stock
#         latest_data = FinancialData.objects.filter(symbol=stock_symbol).latest('date')

#         # Calculate EMA counters for the current stock
#         ema_counts = calculate_ema_counts(latest_data)
#         ema_counts_list.append(ema_counts)

#     context = {'ema_counts_list': ema_counts_list}

#     # Render your template or perform other actions
#     return render(request, 'count_ema.html', context)


# Data diaplay

# # closing_prices = StockData.objects.filter(symbol=stock).order_by('date').values_list('close_price', flat=True)
# from django.shortcuts import render
# from .models import StockData, IndicatorValues, EmaCounts

# def ema_counts(request):
#     stocks = StockData.objects.values_list('symbol', flat=True).distinct()
#     ema_values = ['ema20', 'ema50', 'ema100', 'ema200']  # Add other EMAs as needed

#     # Clear existing EmaCounts data
#     EmaCounts.objects.all().delete()

#     for stock in stocks:
#         ema_counts_entry = EmaCounts.objects.create(stock_data=StockData.objects.filter(symbol=stock).first())

#         # Fetch necessary data in a single query
#         stock_data = StockData.objects.filter(symbol=stock).order_by('-date')
#         indicator_values = IndicatorValues.objects.filter(stock_data__symbol=stock).order_by('-stock_data__date')

#         ema_data = {}  # Store trend data for each EMA
#         for ema in ema_values:
#             ema_data[ema] = {
#                 "current_trend": None,
#                 "consecutive_days": 0,
#                 "start_date": None,
#             }

#             # Fetch necessary values for the EMA
#             ema_values_for_stock = indicator_values.values_list(ema, flat=True)
#             closing_prices = stock_data.values_list('close_price', flat=True)
#             dates = stock_data.values_list('date', flat=True)

#             prev_closing_price = None
#             for date, closing_price, ema_value in zip(dates, closing_prices, ema_values_for_stock):
#                 if prev_closing_price is not None:
#                     if closing_price > ema_value and prev_closing_price <= ema_value:
#                         # New "Up" sequence starts
#                         ema_data[ema]["current_trend"] = "Up"
#                         ema_data[ema]["consecutive_days"] = 1
#                         ema_data[ema]["start_date"] = date
#                     elif closing_price < ema_value and prev_closing_price >= ema_value:
#                         # New "Down" sequence starts
#                         ema_data[ema]["current_trend"] = "Down"
#                         ema_data[ema]["consecutive_days"] = 1
#                         ema_data[ema]["start_date"] = date
#                     elif closing_price > ema_value and prev_closing_price > ema_value:
#                         # Continue "Up" sequence
#                         ema_data[ema]["consecutive_days"] += 1
#                     elif closing_price < ema_value and prev_closing_price < ema_value:
#                         # Continue "Down" sequence
#                         ema_data[ema]["consecutive_days"] += 1

#                 prev_closing_price = closing_price

#             # Build output strings for each EMA
#             ema_output = {
#                 ema: (
#                     f"Up: {ema_data[ema]['consecutive_days']} days (from {ema_data[ema]['start_date']} to {dates[0]})\n"
#                     if ema_data[ema]['current_trend'] == 'Up'
#                     else f"Down: {ema_data[ema]['consecutive_days']} days (from {ema_data[ema]['start_date']} to {dates[0]})\n"
#                 )
#             }

#             # Store the output strings in the EmaCounts object
#             ema_counts_entry.__dict__[f'{ema}_output'] = ema_output[ema]

#         ema_counts_entry.save()


#     ema_count_data = EmaCounts.objects.all()

#     return render(request, 'ema_counts.html', {'ema_count_data': ema_count_data})


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


## Adding 200 days old data
# # views.py
# from django.shortcuts import render
# from .models import StockData, IndicatorValues
# from datetime import datetime, timedelta
# from pandas_datareader import data as pdr
# import yfinance as yf
# import pandas as pd
# import numpy as np

# def calculate_rsi_and_rs(df, n=14):
#     close_price_changes = df['Close'].diff()

#     gains = close_price_changes.where(close_price_changes > 0, 0)
#     losses = -close_price_changes.where(close_price_changes < 0, 0)

#     average_gain = gains.rolling(window=n, min_periods=1).mean()
#     average_loss = losses.rolling(window=n, min_periods=1).mean()

#     rs = average_gain / average_loss
#     rsi = 100 - (100 / (1 + rs))

#     # Replace NaN and -inf values with None
#     rsi.replace([np.nan, -np.inf], None, inplace=True)
#     rs.replace([np.nan, -np.inf], None, inplace=True)

#     return rsi, rs

# def fetch_and_store_stock_data(request):
#     # Database setup
#     stock_symbols = ['^NSEI', '^NSEBANK', '^CNXAUTO', '^CNXIT', '^CNXMETAL', '^CNXMEDIA', '^CNXCONS durables', '^NSE100', '^NSE200', '^NSENEXT50']
#     num_days = 200  # Change to 200 to fetch data for the last 200 days
#     end_date = datetime.now()
#     start_date = end_date - timedelta(days=num_days * 2)

#     # Override the data reader function
#     yf.pdr_override()

#     for symbol in stock_symbols:
#         df = pdr.get_data_yahoo(symbol, start=start_date, end=end_date)
#         df['Date'] = pd.to_datetime(df.index)  # Convert index to DatetimeIndex
#         df = df.set_index('Date')  # Set 'Date' as the new index

#         df = df[['Close']].last(f'{num_days}D')  # Fetch data for the last 200 days

#         # Calculate EMA
#         ema20 = df['Close'].ewm(span=20, adjust=False).mean()
#         ema50 = df['Close'].ewm(span=50, adjust=False).mean()
#         ema100 = df['Close'].ewm(span=100, adjust=False).mean()
#         ema200 = df['Close'].ewm(span=200, adjust=False).mean()

#         # Calculate RSI and RS
#         rsi, rs = calculate_rsi_and_rs(df)

#         # Store in the database
#         for idx, row in df.iterrows():
#             stock_data = StockData.objects.create(
#                 symbol=symbol,
#                 date=row.name,
#                 close_price=row['Close']
#             )

#             indicator_values = IndicatorValues.objects.create(
#                 stock_data=stock_data,
#                 ema20=None if pd.isna(ema20.loc[idx]) else ema20.loc[idx],
#                 ema50=None if pd.isna(ema50.loc[idx]) else ema50.loc[idx],
#                 ema100=None if pd.isna(ema100.loc[idx]) else ema100.loc[idx],
#                 ema200=None if pd.isna(ema200.loc[idx]) else ema200.loc[idx],
#                 rsi=None if pd.isna(rsi.loc[idx]) else rsi.loc[idx],
#                 rs=None if pd.isna(rs.loc[idx]) else rs.loc[idx]
#                 # Add other indicator values as needed
#             )

#     return render(request, 'success.html')

  