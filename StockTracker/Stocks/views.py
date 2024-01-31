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
            login(request, user)  # Log in the user after signup
            return redirect('login')  # Redirect to the login page or any other desired page
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


## Adding new Stocks data
# views.py
# views.py
from django.shortcuts import render
from .models import FinancialData
from datetime import datetime, timedelta
from pandas_datareader import data as pdr
import yfinance as yf
import pandas as pd
import numpy as np

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

def fetch_and_calculate_ema(request):
    # Database setup
    stock_symbols = [
        'RELIANCE.NS', 'TATAMOTORS.NS', 'HDFCBANK.NS', 'INFY.NS', 'TATASTEEL.NS',
        'ZEEL.NS', 'HAVELLS.NS', 'HDFC.NS', 'ITC.NS', 'NESTLEIND.NS',
        'ICICIBANK.NS', 'HINDALCO.NS', 'DRREDDY.NS', 'WIPRO.NS', 'MARUTI.NS',
        'AXISBANK.NS', 'BAJAJFINSV.NS', 'ONGC.NS', 'GRASIM.NS', 'IOC.NS'
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
        start_date = end_date - timedelta(days=400)  # Fetch data for the last 200 days

        df_new = pdr.get_data_yahoo(symbol, start=start_date, end=end_date)
        df_new['Date'] = pd.to_datetime(df_new.index)  # Convert index to DatetimeIndex
        df_new = df_new.set_index('Date')  # Set 'Date' as the new index

        # Ensure 'close_price' column is present in the new dataframe
        if 'Close' not in df_new.columns:
            # Handle the situation where 'Close' is not present
            # You might want to log a message or handle it based on your requirements
            continue

        # Calculate EMA
        ema20 = df_new['Close'].ewm(span=20, adjust=False).mean()
        ema50 = df_new['Close'].ewm(span=50, adjust=False).mean()
        ema100 = df_new['Close'].ewm(span=100, adjust=False).mean()
        ema200 = df_new['Close'].ewm(span=200, adjust=False).mean()

        # Calculate RSI and RS
        rsi, rs = calculate_rsi_and_rs(df_new)

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


# views.py
from django.shortcuts import render
from .models import FinancialData, EmaCounts

def calculate_ema_counters(closing_prices, ema_values):
    ema_counter = 0

    for i, closing_price in enumerate(closing_prices):
        if i < len(ema_values):
            try:
                ema_value = float(ema_values[i])
                if i == 0:
                    # Initialize counter for the newest date
                    if closing_price > ema_value:
                        ema_counter = 1
                    else:
                        ema_counter = -1
                else:
                    # Compare closing price with EMA for the rest of the dates
                    if closing_price > ema_value:
                        ema_counter += 1
                    else:
                        break  # Break the loop if behavior changes
            except ValueError:
                # Handle the case where ema_values contain non-numeric values
                break
        else:
            # Handle the case where the ema_values list is shorter than the closing_prices list
            break

    return ema_counter

def calculate_ema_counts(stock_data):
    ema_counts, created = EmaCounts.objects.get_or_create(stock_data=stock_data)

    # Split ema_output fields only if they are not empty
    ema20_values = [value for value in ema_counts.ema20_output.split(',') if value]
    ema50_values = [value for value in ema_counts.ema50_output.split(',') if value]
    ema100_values = [value for value in ema_counts.ema100_output.split(',') if value]
    ema200_values = [value for value in ema_counts.ema200_output.split(',') if value]

    # Get historical financial data for the current stock, ordered by date
    historical_data = FinancialData.objects.filter(symbol=stock_data.symbol).order_by('-date')
    closing_prices = [data.close_price for data in historical_data]

    # Calculate counters for each EMA
    ema_counts.ema20_counter = calculate_ema_counters(closing_prices, ema20_values)
    ema_counts.ema50_counter = calculate_ema_counters(closing_prices, ema50_values)
    ema_counts.ema100_counter = calculate_ema_counters(closing_prices, ema100_values)
    ema_counts.ema200_counter = calculate_ema_counters(closing_prices, ema200_values)

    # Save the counters to the respective fields in EmaCounts model
    ema_counts.save()

    return ema_counts

def count_function(request):
    # Get all distinct stock symbols
    stocks_symbols = FinancialData.objects.values('symbol').distinct()

    ema_counts_list = []

    # Iterate over each stock symbol
    for stock_symbol in stocks_symbols:
        stock_symbol = stock_symbol['symbol']

        # Get the latest financial data for the current stock
        latest_data = FinancialData.objects.filter(symbol=stock_symbol).latest('date')

        # Calculate EMA counters for the current stock
        ema_counts = calculate_ema_counts(latest_data)
        ema_counts_list.append(ema_counts)

    context = {'ema_counts_list': ema_counts_list}

    # Render your template or perform other actions
    return render(request, 'count_ema.html', context)
  
# Ema Count
    
from django.shortcuts import render
from Stocks.models import FinancialData, EmaCounts
from datetime import timedelta
from django.utils import timezone

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
        ).order_by('-date').values_list('date', 'ema20', 'ema50', 'ema100', 'ema200', 'close_price')

        # Check if any data points were retrieved
        if not data_points:
            continue

        # Initialize counters
        ema20_counter = 0
        ema50_counter = 0
        ema100_counter = 0
        ema200_counter = 0

        # Iterate through data points from newest to oldest date for EMA20
        for date, ema20, _, _, _, close_price in data_points:
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
        for date, _, ema50, _, _, close_price in data_points:
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
        for date, _, _, ema100, _, close_price in data_points:
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
        for date, _, _, _, ema200, close_price in data_points:
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
            defaults={'ema20_output': ema20_counter, 'ema50_output': ema50_counter,
                      'ema100_output': ema100_counter, 'ema200_output': ema200_counter},
        )
        ema_counts_instance.save()

        # print(f"Starting ema20_counter for {stock_symbol} = {ema20_counter}")
        # print(f"Starting ema50_counter for {stock_symbol} = {ema50_counter}")
        # print(f"Starting ema100_counter for {stock_symbol} = {ema100_counter}")
        # print(f"Starting ema200_counter for {stock_symbol} = {ema200_counter}")

    # Pass the results to the template
    context = {'result_list': []}  # Empty list as no results are being passed to the template
    return render(request, 'analyze_output.html', context)
