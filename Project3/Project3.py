import requests
import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd
import mplfinance as mpf
import plotly.graph_objects as go

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

# Ask the user for a valid date range
def get_date_range():
    while True:
        start_date = input("\nEnter the start date (YYYY-MM-DD): ").strip()
        end_date = input("Enter the end date (YYYY-MM-DD): ").strip()

        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")

            if end_dt >= start_dt:
                return start_date, end_date
            else:
                print("Error: End date cannot be before the start date. Please try again.")
        except ValueError:
            print("Invalid date format. Please enter dates in YYYY-MM-DD format.")


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

def plot_chart(data, symbol, chart_type):
    # Prepare data for plotting
    df = pd.DataFrame.from_dict(data, orient='index')
    df.index = pd.to_datetime(df.index)  # Convert index to datetime
    df = df.rename(columns={
        "1. open": "Open",
        "2. high": "High",
        "3. low": "Low",
        "4. close": "Close",
        "5. volume": "Volume"
    })

    # Ensure all required columns are numeric
    for col in ["Open", "High", "Low", "Close", "Volume"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')  # Convert to numeric, set invalid values to NaN

    # Drop rows with NaN values in required columns
    df = df.dropna(subset=["Open", "High", "Low", "Close"])

    if chart_type == "Candlestick Chart":
        # Create a candlestick chart
        fig = go.Figure(data=[go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close']
        )])
        fig.update_layout(
            title=f"{symbol} - Candlestick Chart",
            xaxis_title="Date",
            yaxis_title="Price",
            template="plotly_dark"
        )
    elif chart_type == "Line Chart":
        # Create a line chart
        fig = go.Figure(data=[go.Scatter(
            x=df.index,
            y=df['Close'],
            mode='lines',
            name='Close Price'
        )])
        fig.update_layout(
            title=f"{symbol} - Line Chart",
            xaxis_title="Date",
            yaxis_title="Price",
            template="plotly_dark"
        )
    elif chart_type == "Bar Chart":
        # Create a bar chart
        fig = go.Figure(data=[go.Bar(
            x=df.index,
            y=df['Close'],
            name='Close Price'
        )])
        fig.update_layout(
            title=f"{symbol} - Bar Chart",
            xaxis_title="Date",
            yaxis_title="Price",
            template="plotly_dark"
        )
    else:
        print("Invalid chart type.")
        return

    # Open the chart in the browser
    fig.show()

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
    
    start_date, end_date = get_date_range()  # Ask for date range

    stock_data = fetch_stock_data(stock_symbol, time_series_function, interval)

    if stock_data:
        print(f"\nDisplaying data for {stock_symbol} from {start_date} to {end_date} using a {chart_type.lower()}.")

        # Filter data within the selected date range
        filtered_data = {date: values for date, values in stock_data.items() if start_date <= date <= end_date}

        if display_pref in ["Table", "Both"]:
            print("\nMost recent 3 data points in the selected range:")
            for date, values in list(filtered_data.items())[:3]:
                print(f"\nDate: {date}")
                for k, v in values.items():
                    print(f"  {k}: {v}")

        if display_pref in ["Chart", "Both"]:
            plot_chart(filtered_data, stock_symbol, chart_type)

        ask_to_download_csv(filtered_data, stock_symbol)
