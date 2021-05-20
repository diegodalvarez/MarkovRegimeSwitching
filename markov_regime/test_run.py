import pandas as pd
import yfinance as yf
import datetime as dt

from markov_regime import *

end = dt.datetime.today()
start = end - dt.timedelta(days = (365 * 10) + 5)
ticker = "^GSPC"
price_type = "Adj Close"
frequency = "daily"

df = Prices(start, end, ticker, price_type, frequency).getPrices()
plot = TimeSeries(df, ticker, frequency, price_type).plot_smoothed_probability()
regimes = TimeSeries(df, ticker, frequency, price_type).get_regime_data()
