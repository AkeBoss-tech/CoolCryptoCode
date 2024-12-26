# import all libraries
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
import statsmodels
import yfinance as yf
import os

def get_data(ticker):
    # check if ticker.csv is in data folder if it is load the csv and return it
    if os.path.exists(f'data/{ticker}.csv'):
        data = pd.read_csv(f'data/{ticker}.csv')
        # make sure the date column is a datetime object
        data['Datetime'] = pd.to_datetime(data['Datetime'])
        # make it the index
        data.set_index('Datetime', inplace=True)
        # make all other columns numeric
        data = data.apply(pd.to_numeric, errors='coerce')
        return data
    
    # if the csv does not exist download the data from yahoo finance
    ticker_obj = yf.Ticker(ticker)
    data = ticker_obj.history(period='max', interval='15m')
    data.to_csv(f'data/{ticker}.csv')
    return data

