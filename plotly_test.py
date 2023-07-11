import plotly.graph_objects as go

import pandas as pd
from datetime import datetime

df = pd.read_csv('data.csv')

fig = go.Figure(data=[go.Candlestick(x=df['open_time'],
                open=df['open_price'],
                high=df['high_price'],
                low=df['low_price'],
                close=df['close_price'])])

fig.show()
