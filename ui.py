from flask import Flask, render_template
import pandas as pd
import plotly
import plotly.graph_objects as go
import plotly.express as px
import json
import requests

SYMBOLS = ['bitcoin', 'solana', 'ripple', 'dai', 'cardano', 'dogecoin', 'cosmos', 'tron', 'aptos', 'arbitrum']

def market_cap(symbol):
  url = f'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={symbol}'
  response = requests.get(url)
  data = response.json()
  if data:
      market_cap = data[0]['market_cap']
      return market_cap
  else:
      return -1

def market_caps(coins):
    caps = {}
    for coin in coins:
        caps[coin] = market_cap(coin)

    data = {"Currencies": caps.keys(), "Caps": caps.values()}
    frame = pd.DataFrame(data=data)
    return frame

app = Flask(__name__)

@app.route('/')
def index():
    df = pd.read_csv('data.csv')

    fig1 = go.Figure(data=[go.Candlestick(x=df['open_time'],
                    open=df['open_price'],
                    high=df['high_price'],
                    low=df['low_price'],
                    close=df['close_price'])])

    graph1JSON = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)

    fig2 = px.pie(market_caps(SYMBOLS),
                  values='Caps',
                  names='Currencies',
                  title='Piechart of market caps for 10 symbols')

    graph2JSON = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('index.html', graphJSON=graph1JSON, graph2JSON=graph2JSON)

if __name__ == "__main__":
    app.run()
