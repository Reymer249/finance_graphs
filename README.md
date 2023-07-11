# Finance graphs
This small program gets the data from the Binance and saves it and plots using Flask

## How to use

1. Install `virtualenv`:
```
$ pip install virtualenv
```

2. Open a terminal in the project root directory and run:
```
$ virtualenv env
```

3. Then run the command:
```
$ source env/bin/activate
```

4. Then install the dependencies:
```
$ (env) pip install -r requirements.txt
```

5. Finally run the program with arguments (**they are mandatory**):
```
$ (env) python main.py 1h BTCUSDT 1
```
*The code above is an example, the arguments mean the following:
* 1h - the interval of time you want to inspect (also may be in seconds(s), minutes(m), hours(d), days(d), or weeks(w))
* BTCUSDT - the symbol you want to inspect
* 1 - number of candles per second; may be omitted, then a default value is 1

The server will start on port 5000 by default. You can change this in `ui.py` by changing the following line to this:

```python
if __name__ == "__main__":
    app.run(port=<desired port>)

