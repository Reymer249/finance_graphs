import numpy as np
import pandas as pd
import requests
from urllib.parse import urlencode
import time
import sys
import sqlite3


class BinanceSpotMarket():
    def __init__(self):
        super().__init__()
        self.trading_type = 'spot'
        self.base_url = "https://api.binance.com"
        return

    def dispatch_request(self, http_method: str):
        """ Prepare a request with given http method """
        session = requests.Session()
        session.headers.update({
            'Content-Type': 'application/json;charset=utf-8',
            'X-MBX-APIKEY': ""
        })
        response = {
            'GET': session.get,
            'DELETE': session.delete,
            'PUT': session.put,
            'POST': session.post,
        }.get(http_method, 'GET')
        return response

    def send_public_request(self, url_path: str, payload={}):
        """
        Prepare and send an unsigned request.
        Use this function to obtain public market data
        """
        query_string = urlencode(payload, True)
        url = self.base_url + url_path
        if query_string:
            url = url + '?' + query_string
        response = self.dispatch_request('GET')(url=url)
        return response.json()

    def server_time(self):
        """
        Test connectivity to the REST API and return server time.
        """
        url_path = "/api/v3/time"
        params = {}
        response = self.send_public_request(
            url_path=url_path,
            payload=params
        )
        return response['serverTime']

    def current_price(self, pair: str):
        """
        Latest price for a pair or pairs.
        """
        url_path = "/api/v3/ticker/price"
        params = {'symbol': pair}
        response = self.send_public_request(
            url_path=url_path,
            payload=params
        )
        return float(response['price'])


    def most_recent_market_data(self, pair: str, timeframe: str, n_candles_per_second: int):
        """
        Load the n_candles most recent ohlc candlesticks for the given pair and timeframe.
        """
        ohlc = []
        end_time = 0
        seconds = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400, 'w':604800}
        n_candles = int(timeframe[0]) * seconds[timeframe[1]] * n_candles_per_second
        while n_candles+10 > 0:
            limit = np.min([1000, n_candles+10])
            if end_time == 0:
                new_ohlc = self.klines(
                    pair=pair,
                    timeframe=timeframe,
                    limit=limit
                )
            else:
                new_ohlc = self.klines(
                    pair=pair,
                    timeframe=timeframe,
                    limit=limit,
                    end_time=end_time
                )
            new_ohlc = pd.DataFrame(
                new_ohlc,
                columns=[
                    'open_time', 'open_price', 'high_price',
                    'low_price', 'close_price', 'volume',
                    'close_time', 'quote_volume', 'n_trades',
                    'taker_buy_base_volume', 'taker_buy_quote_volume', 'ignore'
                ]
            )
            ohlc.append(new_ohlc)
            end_time = pd.Timestamp(pd.to_datetime(new_ohlc['close_time'], unit='ms').min())
            end_time = int(end_time.timestamp() * 1000)
            n_candles -= limit
        ohlc = pd.concat(ohlc, axis=0)
        ohlc.sort_values(by='open_time', inplace=True)
        ohlc.drop_duplicates(inplace=True)
        ohlc.index = [i for i in range(ohlc.shape[0])]
        if pd.to_datetime(ohlc['close_time'], unit='ms').max() > pd.Timestamp(int(time.time()), unit='s'):
            ohlc = ohlc.iloc[:-1].copy()
        for col in ohlc.columns:
            ohlc[col] = pd.to_numeric(ohlc[col])
        ohlc['close_time'] = ohlc['open_time'] + pd.Timedelta(timeframe).seconds * 1000
        ohlc['open_timestamp'] = pd.to_datetime(ohlc['open_time'], unit='ms')
        ohlc['close_timestamp'] = pd.to_datetime(ohlc['close_time'], unit='ms')
        ohlc = ohlc.drop('ignore', axis=1)
        return ohlc

    def klines(self, pair: str, timeframe: str, **kwargs):
        """
        Kline/candlestick bars for a symbol.
        Klines are uniquely identified by their open time.
        """
        url_path = "/api/v3/klines"
        params = {'symbol': pair, 'interval': timeframe}
        for key, value in kwargs.items():
            if key == 'start_time':
                params['startTime'] = int(value)
            if key == 'end_time':
                params['endTime'] = int(value)
            if key == 'limit':
                params['limit'] = np.min([value, 1000])
        response = self.send_public_request(
            url_path=url_path,
            payload=params
        )
        return response

if __name__ == "__main__":
    # the input arguments
    arguments = sys.argv[1:]

    # Output

    # print("Server time: ", BinanceSpotMarket().server_time())
    print("Current price for {}: ".format(arguments[1]), BinanceSpotMarket().current_price(arguments[1]))

    data = BinanceSpotMarket().most_recent_market_data(pair=arguments[1], timeframe=arguments[0], n_candles_per_second=arguments[2] if len(arguments)==3 else 1)
    print("An example of OHLCV data stored in {}_{}_data .csv and .db files:\n".format(arguments[0], arguments[1]), data.iloc[0])

    # Saving the data

    # csv
    data.to_csv('data.csv'.format(arguments[0], arguments[1]))

    # db
    conn = sqlite3.connect('data.db'.format(arguments[0], arguments[1]))
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS Candles(
                    Open_time INTEGER, 
                    Open_price REAL, 
                    High_price REAL, 
                    Low_price REAL, 
                    Close_price REAL,
                    Volume REAL, 
                    Close_time INTEGER, 
                    Quote_volume REAL, 
                    Number_of_trades INTEGER, 
                    Taker_bb_volume REAL,
                    Taker_bq_volume REAL, 
                    Open_timestamp TEXT, 
                    Close_timestamp TEXT);''')
    conn.commit()
    data.to_sql("Candles", conn, if_exists='replace', index = False)

    with open("ui.py") as u:
        exec(u.read())
