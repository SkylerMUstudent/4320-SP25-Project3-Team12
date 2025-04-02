import requests
import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd

# Alpha Vantage API key
API_KEY = '6P95RTQHO9NS644U'

# Prompt the user to enter a stock symbol (e.g., AAPL, MSFT)
def get_stock_symbol():
    while True:
        symbol = input("Enter the stock symbol for the company (e.g., AAPL, MSFT): ").strip().upper()
        if symbol.isalnum():
            return symbol
        else:
            print("Invalid symbol. Please enter a valid stock ticker.")

# Ask the user what kind of chart they want to see
def get_chart_type():
    chart_types = {
        "1": "Line Chart",
        "2": "Bar Chart",
        "3": "Candlestick Chart"  # Placeholder
    }

    print("\nSelect the chart type:")
    for key, value in chart_types.items():
        print(f"{key}. {value}")

    while True:
        choice = input("Enter the number corresponding to your chart type: ").strip()
        if choice in chart_types:
            print(f"\nYou selected: {chart_types[choice]}")
            return chart_types[choice]
        else:
            print("Invalid choice. Please select 1, 2, or 3.")

# Ask the user to choose the time series data type
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
        else:
            print("Invalid choice. Please select 1, 2, 3, or 4.")

# Ask the user how they want to view the data
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
        else:
            print("Invalid choice. Please select 1, 2, or 3.")

# Retrieve stock data from Alpha Vantage using the selected function and interval
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

    # Determine the correct key to access data from the response
    key_lookup = {
        "TIME_SERIES_INTRADAY": f"Time Series ({interval})",
        "TIME_SERIES_DAILY": "Time Series (Daily)",
        "TIME_SERIES_WEEKLY": "Weekly Time Series",
        "TIME_SERIES_MONTHLY": "Monthly Time Series"
    }

    data_key = key_lookup.get(function)

    if data_key in data:
        print(f"\nData successfully retrieved for {symbol} ({function}).")
        return data[data_key]
    elif "Error Message" in data:
        print("\nError: Invalid symbol or unsupported function.")
    elif "Note" in data:
        print("\nAPI call frequency limit reached. Please wait and try again.")
    else:
        print("\nFailed to retrieve data. Please check your input or API key.")
    
    return None

# Plot either a line or bar chart using the stock's closing prices
def plot_chart(data, symbol, chart_type):
    dates = []
    closes = []

    for date_str, values in list(data.items())[:30][::-1]:  # Last 30 points, ordered oldest to newest
        date_obj = datetime.strptime(date_str, "%Y-%m-%d" if "-" in date_str else "%Y-%m-%d %H:%M:%S")
        dates.append(date_obj)
        closes.append(float(values["4. close"]))

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

# Ask the user if they want to save the data to a CSV file
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
        print("Skipped CSV download.")

# Main program logic
if __name__ == "__main__":
    stock_symbol = get_stock_symbol()
    chart_type = get_chart_type()
    time_series_function, interval = get_time_series_function()
    display_pref = get_display_preference()

    stock_data = fetch_stock_data(stock_symbol, time_series_function, interval)

    if stock_data:
        print(f"\nDisplaying data for {stock_symbol} using a {chart_type.lower()}.")

        if display_pref in ["Table", "Both"]:
            print("\nMost recent 3 data points:")
            for date, values in list(stock_data.items())[:3]:
                print(f"\nDate: {date}")
                for k, v in values.items():
                    print(f"  {k}: {v}")

        if display_pref in ["Chart", "Both"]:
            plot_chart(stock_data, stock_symbol, chart_type)

        ask_to_download_csv(stock_data, stock_symbol)
