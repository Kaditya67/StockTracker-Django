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



    # views.py
def display_stock_data(request):
    stock_data = StockData.objects.all()
    return render(request, 'admin_stock_data.html', {'stock_data': stock_data})

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
from django.shortcuts import render
from .models import StockData, IndicatorValues
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
    stock_symbols = ['^NSEI', '^NSEBANK', '^CNXAUTO', '^CNXIT', '^CNXMETAL', '^CNXMEDIA', '^CNXCONS durables', '^NSE100', '^NSE200', '^NSENEXT50']

    # Override the data reader function
    yf.pdr_override()

    result_data = []

    for symbol in stock_symbols:
        # Check if data for the symbol is already present in the database
        latest_data = StockData.objects.filter(symbol=symbol).order_by('-date').first()

        if latest_data is not None:
            # Check if the latest data is up-to-date (within the last day)
            if (datetime.now().date() - latest_data.date).days <= 1:
                # Skip fetching new data if it's up-to-date
                continue

        # Fetch new data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=200)  # Fetch data for the last 200 days

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
            stock_data, created = StockData.objects.get_or_create(
                symbol=symbol,
                date=row.name,
                defaults={'close_price': row['Close']}
            )

            indicator_values, created = IndicatorValues.objects.get_or_create(
                stock_data=stock_data,
                defaults={
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
