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
from django.http import JsonResponse
import json
from django.template.loader import render_to_string

from django.shortcuts import redirect
from .models import stock_user


def remove_from_watchlist(request):
    if request.method == 'POST':
        symbol_to_remove = request.POST.get('symbol')
        
        # Retrieve the StockUser instance for the current user
        current_user = request.user  # Get the current authenticated user
        try:
            stock_user_instance = stock_user.objects.get(username=current_user.username)
        except stock_user.DoesNotExist:
            # Handle case where StockUser instance does not exist for the user
            return redirect('watchlist')  # Redirect back to the watchlist page
        
        # Parse watchlist_sector into a list of dictionaries
        watchlist_data = json.loads(stock_user_instance.watchlist_sector)
        
        # Perform the removal logic
        updated_watchlist_data = [entry for entry in watchlist_data if entry['symbol'] != symbol_to_remove]
        
        # Save the updated watchlist_sector back to the stock_user instance
        stock_user_instance.watchlist_sector = json.dumps(updated_watchlist_data)
        stock_user_instance.save()

        return redirect('watchlist')  # Redirect back to the watchlist page

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from json.decoder import JSONDecodeError  # Import JSONDecodeError
from .models import stock_user  # Import the stock_user model
import json
from django.core import serializers  # Import Django's built-in serializer
import json

def send_watchlist_email(user):
    try:
        # Fetch the user's watchlist_sector
        watchlist_sector = user.watchlist_sector
        if watchlist_sector:  # Check if watchlist_sector is not empty
            try:
                # Parse existing JSON data
                watchlist_data = json.loads(watchlist_sector)
            except json.JSONDecodeError:
                # Handle invalid JSON data
                watchlist_data = []
        else:
            watchlist_data = []

        if watchlist_data:
            email_subject = "Watchlist Update"
            email_body = """
            <html>
            <head></head>
            <body>
                <h2>Your watchlist has been updated:</h2>
                <table border="1">
                    <tr>
                        <th>Symbol</th>
                        <th>Close Price</th>
                        <th>Date</th>
                    </tr>
            """

            # Add each symbol to the table body
            for entry in watchlist_data:
                symbol = entry.get('symbol', '')
                closing_price = entry.get('closing_price', '')
                date = entry.get('date', '')

                if symbol and closing_price and date:
                    email_body += f"""
                    <tr>
                        <td>{symbol}</td>
                        <td>{closing_price}</td>
                        <td>{date}</td>
                    </tr>
                    """

            email_body += """
                </table>
                <p>To know more about your stocks and sectors, click <a href="http://127.0.0.1:8000/watchlist/">here</a>.</p>
            </body>
            </html>
            """

            # Get the user's email address
            email_to = user.email

            # Send email
            email_watchlist(email_subject, email_body, [email_to])

            print("Email sent successfully to", email_to)
        else:
            print("Watchlist is empty. No email sent.")
    except Exception as e:
        print("Error sending watchlist email:", str(e))





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
                    # Parse existing JSON data
                    watchlist_data = json.loads(watchlist_sector)
                except json.JSONDecodeError:
                    # Handle invalid JSON data
                    watchlist_data = []
            else:
                watchlist_data = []
            
            # Check if symbol already exists in the watchlist
            symbol_exists = any(entry['symbol'] == symbol for entry in watchlist_data)
            if not symbol_exists:
                # Append new data to the existing JSON data
                watchlist_data.append(serialized_data)
                # Convert the updated JSON data back to a string
                user.watchlist_sector = json.dumps(watchlist_data)
                user.save()
                print(serialized_data)
                send_watchlist_email(user)
                return JsonResponse({'success': True, 'data': serialized_data})
            else:
                return JsonResponse({'success': False, 'message': 'Symbol already exists in the watchlist.'})
        except SectorData.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Sector data not found for the symbol.'})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method.'})

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import FinancialData
import json


@login_required
def fetch_stock_data(request):
    if request.method == 'POST':
        symbol = request.POST.get('symbol')
        user = request.user

        try:
            stock_data = FinancialData.objects.filter(symbol=symbol).latest('date')
        except FinancialData.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Stock data not found for the symbol.'})

        serialized_data = {
            'date': stock_data.date.strftime('%Y-%m-%d'),
            'symbol': stock_data.symbol,
            'closing_price': float(stock_data.close_price),
        }

        try:
            watchlist_sector = json.loads(user.watchlist_sector)
        except (json.JSONDecodeError, AttributeError):
            watchlist_sector = []

        symbol_exists = any(entry['symbol'] == symbol for entry in watchlist_sector)
        if not symbol_exists:
            watchlist_sector.append(serialized_data)
            user.watchlist_sector = json.dumps(watchlist_sector)
            user.save()
            return JsonResponse({'success': True, 'data': serialized_data})
        else:
            return JsonResponse({'success': False, 'message': 'Symbol already exists in the watchlist.'})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method.'})

# def watchlist(request):
#     current_path = resolve(request.path_info).url_name
#     user = request.user
#     watchlist_sector = json.loads(user.watchlist_sector)
#     current_path = resolve(request.path_info).url_name
#     return render(request, 'watchlist.html', {'watchlist_sector': watchlist_sector, 'current_path': current_path})
from django.shortcuts import resolve_url 

@login_required
def watchlist(request):
    try:
        watchlist_sector = json.loads(request.user.watchlist_sector)
    except (json.JSONDecodeError, AttributeError):
        watchlist_sector = []

    try:
        watchlist_stock = json.loads(request.user.watchlist_stock)
    except (json.JSONDecodeError, AttributeError):
        watchlist_stock = []

    current_path = resolve(request.path_info).url_name
    return render(request, 'watchlist.html', {'watchlist_sector': watchlist_sector, 'watchlist_stock': watchlist_stock, 'current_path': current_path})

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
from .email_alerts import email_alert, email_watchlist
from .utils import generate_otp
from .email_alerts import email_password

def alerts(request):
    return render(request, 'alerts.html')

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
    unique_symbols =FinancialData.objects.values_list('symbol', flat=True).distinct()

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
        'unique_symbols': unique_symbols,
        'ema_counts': ema_counts,
        'rs_values': rs_values,
        'symbols': symbols,
        'selected_ema': selected_ema,
        'current_path': current_path,
    }

    # current_path = resolve(request.path_info).url_name
    # return render(request, 'dashboard.html', {'current_path': current_path, 'context': context})
    return render(request, 'dashboard.html', context)

from .models import FinancialData
from .models import EmaCounts

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

    elif request.method == 'GET':
        # Handle GET request (e.g., display the verify page)
        return render(request, 'verify.html')

    else:
        messages.error(request, 'Invalid form submission.')
        return render(request, 'verify.html')

def user_logout(request):
    logout(request)
    messages.success(request, "successfully logged out")
    return redirect('index')

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
           # messages.success(request, "Successfully Logged In")
            return redirect('dashboard')  # Redirect to the home page or any other desired page
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
          #  messages.success(request, "Account created successfully")
            otp = generate_otp()

            request.session['otp_sent_to_email'] = otp

            email_alert("welcome to our website","thank you for signing up!",email,otp)
            
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
    return ema20_counter


@login_required
def stocks(request):
    unique_symbols =FinancialData.objects.values_list('symbol', flat=True).distinct()[:20]

    symbols_to_remove = []
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

        if not data_points or not all(data_point[2] for data_point in data_points):
            symbols_to_remove.append(stock_symbol)
            continue
        
        if len(data_points) == 1 and data_points[0][2] == data_points[0][3]:
            symbols_to_remove.append(stock_symbol)
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

    # print(date_list)
    unique_symbols = [symbol for symbol in unique_symbols if symbol not in symbols_to_remove]
    current_path = resolve(request.path_info).url_name
    context = {
        'result': result,
        'unique_symbols': unique_symbols,
        'date_list': date_list,
        'current_path': current_path
    }
    return render(request, 'stocks.html', context)

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
    unique_symbols = SectorData.objects.values_list('symbol', flat=True).distinct()[:20]
    
    symbols_to_remove = []
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
        
        if len(data_points) == 1 and data_points[0][2] == data_points[0][3]:
            symbols_to_remove.append(stock_symbol)
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
    unique_symbols = list(set(unique_symbols) - set(symbols_to_remove))
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

    # Calculate percentage change in asset's price over the past n days
    asset_percentage_change = ((df[close_column] - df[start_column].shift(n)) / df[start_column].shift(n)) * 100

    # Calculate percentage change in NIFTY50's price over the past n days
    nifty_percentage_change = ((nifty_df[close_column] - nifty_df[start_column].shift(n)) / nifty_df[start_column].shift(n)) * 100

    # Calculate RS
    rs = asset_percentage_change / nifty_percentage_change

    return rs

def fetch_and_calculate_ema(request):

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

    return render(request, 'fetch_and_calculate_ema.html', {'name': 'Stocks', 'result_data': result_data})

def fetch_and_calculate_ema_sector(request):

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
                'name':"Sector",
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

    return render(request, 'fetch_and_calculate_ema.html', {'name': 'Sector','result_data': result_data})

    
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

        ema_counts_instance.save()

    context = {'result_list': [],}  # Empty list as no results are being passed to the template
    return render(request, 'analyze_output.html',{ 'name':'Stocks', 'context':context})

from django.shortcuts import render
from .models import SectorData, EmaCountsSector
from django.utils import timezone
from datetime import timedelta
from datetime import timedelta

def analyze_closing_vs_ema_sector(request):

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
    return render(request, 'analyze_output.html',{ 'name':'Sector','context':context})

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
