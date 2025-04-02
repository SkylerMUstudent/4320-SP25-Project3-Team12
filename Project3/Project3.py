import requests
import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd
import mplfinance as mpf

# Alpha Vantage API key
API_KEY = '6P95RTQHO9NS644U'

# Prompt user to enter a valid stock ticker
def get_stock_symbol():
    while True:
        symbol = input("Enter the stock symbol for the company (e.g., AAPL, MSFT): ").strip().upper()
        if symbol.isalnum():
            return symbol
        print("Invalid symbol. Please enter a valid stock ticker.")

# Ask user to select the type of chart to display
def get_chart_type():
    chart_types = {
        "1": "Line Chart",
        "2": "Bar Chart",
        "3": "Candlestick Chart"
    }

    print("\nSelect the chart type:")
    for key, value in chart_types.items():
        print(f"{key}. {value}")

    while True:
        choice = input("Enter the number corresponding to your chart type: ").strip()
        if choice in chart_types:
            print(f"\nYou selected: {chart_types[choice]}")
            return chart_types[choice]
        print("Invalid choice. Please select 1, 2, or 3.")

# Ask user to choose the time series data function
def get_time_series_function():
    functions = {
        "1": ("TIME_SERIES_INTRADAY", "5min"),
        "2": ("TIME_SERIES_DAILY", None),
        "3": ("TIME_SERIES_WEEKLY", None),
        "4": ("TIME_SERIES_MONTHLY", None)
    }

    print("\nSelect the time series function:")
    print("1. Intraday (5 min intervals)")
    print("2. Daily")
    print("3. Weekly")
    print("4. Monthly")

    while True:
        choice = input("Enter the number corresponding to your selection: ").strip()
        if choice in functions:
            func, interval = functions[choice]
            print(f"\nYou selected: {func}")
            return func, interval
        print("Invalid choice. Please select 1, 2, 3, or 4.")

# Ask user how they want to view the data
def get_display_preference():
    options = {
        "1": "Table",
        "2": "Chart",
        "3": "Both"
    }

    print("\nHow would you like the data to be displayed?")
    for key, value in options.items():
        print(f"{key}. {value}")

    while True:
        choice = input("Enter the number of your preference: ").strip()
        if choice in options:
            print(f"\nYou selected: {options[choice]}")
            return options[choice]
        print("Invalid choice. Please select 1, 2, or 3.")

# Fetch stock data from Alpha Vantage API
def fetch_stock_data(symbol, function, interval=None):
    url = 'https://www.alphavantage.co/query'
    params = {
        'function': function,
        'symbol': symbol,
        'apikey': API_KEY,
        'datatype': 'json'
    }

    if function == 'TIME_SERIES_INTRADAY':
        params['interval'] = interval
        params['outputsize'] = 'compact'
    else:
        params['outputsize'] = 'full'

    response = requests.get(url, params=params)
    data = response.json()

    key_lookup = {
        "TIME_SERIES_INTRADAY": f"Time Series ({interval})",
        "TIME_SERIES_DAILY": "Time Series (Daily)",
        "TIME_SERIES_WEEKLY": "Weekly Time Series",
        "TIME_SERIES_MONTHLY": "Monthly Time Series"
    }

    data_key = key_lookup.get(function)

    if data_key in data:
        print(f"\nSuccessfully retrieved data for {symbol} ({function}).")
        return data[data_key]
    elif "Error Message" in data:
        print("\nError: Invalid symbol or unsupported function.")
    elif "Note" in data:
        print("\nAPI call frequency limit reached. Please wait and try again.")
    else:
        print("\nFailed to retrieve data. Please check your input or API key.")

    return None

# Plot the selected chart using matplotlib or mplfinance
def plot_chart(data, symbol, chart_type):
    df = pd.DataFrame.from_dict(data, orient='index')
    df.index = pd.to_datetime(df.index)
    df = df.astype(float)
    df = df.rename(columns={
        '1. open': 'Open',
        '2. high': 'High',
        '3. low': 'Low',
        '4. close': 'Close',
        '5. volume': 'Volume'
    })
    df = df.sort_index()

    if chart_type == "Candlestick Chart":
        mpf.plot(df.tail(30), type='candle', style='charles', title=f"{symbol} - Candlestick Chart", volume=True)
    else:
        dates = df.index[-30:]
        closes = df["Close"].tail(30)

        plt.figure(figsize=(12, 6))
        plt.title(f"{symbol} - {chart_type}")
        plt.xlabel("Date")
        plt.ylabel("Close Price")

        if chart_type == "Line Chart":
            plt.plot(dates, closes, linewidth=2)
        elif chart_type == "Bar Chart":
            plt.bar(dates, closes, width=0.8)

        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.grid(True)
        plt.show()

# Ask user if they want to export the data as a CSV file
def ask_to_download_csv(data, symbol):
    choice = input("\nWould you like to download this data as a CSV? (y/n): ").strip().lower()
    if choice == 'y':
        df = pd.DataFrame.from_dict(data, orient='index')
        df.index.name = 'Date'
        df.reset_index(inplace=True)
        filename = f"{symbol}_data.csv"
        df.to_csv(filename, index=False)
        print(f"Data saved as {filename}")
    else:
        print("CSV download skipped.")

# Program entry point
if __name__ == "__main__":
    stock_symbol = get_stock_symbol()
    chart_type = get_chart_type()
    time_series_function, interval = get_time_series_function()
    display_pref = get_display_preference()

    stock_data = fetch_stock_data(stock_symbol, time_series_function, interval)

    if stock_data:
        if display_pref in ["Table", "Both"]:
            print("\nMost recent 3 data points:")
            for date, values in list(stock_data.items())[:3]:
                print(f"\nDate: {date}")
                for k, v in values.items():
                    print(f"  {k}: {v}")

        if display_pref in ["Chart", "Both"]:
            print("\nA chart window will open. Please close it to continue.")
            plot_chart(stock_data, stock_symbol, chart_type)

        ask_to_download_csv(stock_data, stock_symbol)
