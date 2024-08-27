from flask import Flask, render_template, jsonify
import pandas as pd
from alpha_vantage.foreignexchange import ForeignExchange
from alpha_vantage.techindicators import TechIndicators

app = Flask(__name__)

# Alpha Vantage API Key
api_key = 'OGQ91PTBY6HNPTSO'

# Initialize API objects
fx = ForeignExchange(key=api_key, output_format='pandas')
ti = TechIndicators(key=api_key, output_format='pandas')

# Fetch real-time Forex data
def get_realtime_data(from_currency, to_currency):
    try:
        data, _ = fx.get_currency_exchange_rate(from_currency=from_currency, to_currency=to_currency)
        return data
    except Exception as e:
        print(f"Error fetching real-time data: {e}")
        return pd.DataFrame()

# Fetch RSI data
def get_rsi_data(symbol, interval='daily', time_period=14, series_type='close'):
    try:
        rsi_data, _ = ti.get_rsi(symbol=symbol, interval=interval, time_period=time_period, series_type=series_type)
        rsi_data.index = pd.to_datetime(rsi_data.index, errors='coerce', infer_datetime_format=True)
        rsi_data = rsi_data.dropna()
        return rsi_data
    except Exception as e:
        print(f"Error fetching RSI data: {e}")
        return pd.DataFrame()

# Route for the home page
@app.route('/')
def home():
    return render_template('index.html')

# API route to get Forex and RSI data
@app.route('/api/data')
def data():
    from_currency = 'EUR'
    to_currency = 'USD'
    exchange_rate = get_realtime_data(from_currency, to_currency)
    rsi_data = get_rsi_data('EURUSD', interval='daily')
    
    if not exchange_rate.empty and not rsi_data.empty:
        exchange_rate_value = float(exchange_rate['5. Exchange Rate'])
        rsi_value = float(rsi_data['RSI'].iloc[-1])
        decision = 'Buy' if rsi_value < 30 else 'Sell' if rsi_value > 70 else 'Hold'
        return jsonify({
            'exchange_rate': exchange_rate_value,
            'rsi_value': rsi_value,
            'decision': decision
        })
    else:
        return jsonify({'error': 'Data not available'})

if __name__ == '__main__':
    app.run(debug=True)
