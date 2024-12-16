import yfinance as yf
import pandas as pd
import time
import threading
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands
from ta.trend import SMAIndicator

# Define Indian stock symbols (with ".NS" suffix for Yahoo Finance)
STOCKS = ["TCS.NS", "INFY.NS", "RELIANCE.NS", "HDFCBANK.NS", "ICICIBANK.NS"]

# Define RSI thresholds
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

# Function to fetch and analyze stock data
def fetch_and_analyze_data(symbol):
    stock = yf.Ticker(symbol)
    df = stock.history(period="1d", interval="1m")  # Fetch 1-minute intraday data for today

    if not df.empty:
        # Get latest price
        current_price = df['Close'][-1]

        # Calculate technical indicators
        rsi = RSIIndicator(df['Close']).rsi()[-1]
        sma_20 = SMAIndicator(df['Close'], window=20).sma_indicator()[-1]
        bollinger = BollingerBands(df['Close'])
        bollinger_upper = bollinger.bollinger_hband()[-1]
        bollinger_lower = bollinger.bollinger_lband()[-1]

        # Determine Buy/Sell signals
        buy_signal = current_price < bollinger_lower and rsi < RSI_OVERSOLD
        sell_signal = current_price > bollinger_upper and rsi > RSI_OVERBOUGHT

        return {
            "Symbol": symbol,
            "Current Price": current_price,
            "Buy Signal": buy_signal,
            "Sell Signal": sell_signal,
            "RSI": rsi,
            "SMA 20": sma_20,
            "Bollinger Upper": bollinger_upper,
            "Bollinger Lower": bollinger_lower
        }
    else:
        print(f"No data available for {symbol}")
        return None

# Function to update CSV with analyzed data
def update_csv(data):
    # Create a pandas DataFrame from the data
    df = pd.DataFrame(data)

    # Save the data to CSV
    df.to_csv('Intraday_Stock_Analysis.csv', index=False)

    print("CSV file updated with intraday data.")

# Function to display real-time data in the terminal
def display_real_time_data(stock_data):
    for entry in stock_data:
        print(f"Symbol: {entry['Symbol']}")
        print(f"Current Price: {entry['Current Price']}")
        print(f"Buy Signal: {entry['Buy Signal']}")
        print(f"Sell Signal: {entry['Sell Signal']}")
        print(f"RSI: {entry['RSI']}")
        print(f"SMA 20: {entry['SMA 20']}")
        print(f"Bollinger Upper: {entry['Bollinger Upper']}")
        print(f"Bollinger Lower: {entry['Bollinger Lower']}")
        print("-" * 40)

# Main loop to fetch, analyze, and save data every 30 seconds
def main_loop():
    while True:
        stock_data = []
        for symbol in STOCKS:
            result = fetch_and_analyze_data(symbol)
            if result:
                stock_data.append(result)

        if stock_data:
            update_csv(stock_data)
            display_real_time_data(stock_data)

        # Wait for 30 seconds before refreshing
        print("Data updated. Waiting 30 seconds for the next update...\n")
        time.sleep(30)

# Run the script in the background
if __name__ == "__main__":
    # Running the main loop in a separate thread so it doesn't block the main program
    threading.Thread(target=main_loop, daemon=True).start()

    # Keep the script running to allow real-time updates in the background
    while True:
        time.sleep(1)
