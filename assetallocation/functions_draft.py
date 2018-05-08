import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date, timedelta

# Basic functions for asset allocation tool

def invest_dataframe(filename, sep=','):
    """
    Loads a data set containing an investment (stock or bond index).
    Checks that the data set has two columns: a date and an index value.
    Creates a DateTimeIndex.
    Checks there is only one value per date.
    INPUT: filename = name of CSV file, sep = separator in CSV file
    """
    data = pd.read_csv(filename, sep=sep, index_col=0,
        parse_dates=[0], infer_datetime_format=True)
    #Get rid of misisng and non-numeric values
    data = data.apply(pd.to_numeric, errors='coerce').dropna()
    assert data.shape[1] == 1
    assert type(data.index) == pd.core.indexes.datetimes.DatetimeIndex
    assert data.index.nunique() == len(data)
    #Need to fill missing dates with most recent value

    return data


#May want a function to convert data frame to dictionary


def calc_return(data, start, end, kind='percent'):
    """
    Calculates rate of return on a data set between two dates.
    Allows for either percentage rate or log growth.
    INPUTS: start, end = datetimes; data = data frame of investment values
    """
    startval = data.loc[start]
    endval = data.loc[end]
    if kind == 'percent':
        return endval/startval - 1
    elif kind == 'log':
        return np.log(endval) - np.log(startval)
    else:
        raise "Return type must be percent or log."


def annualized_return(data, start, end, kind='percent'):
    pass
    #Write later

#We will want to cache this
def return_list(data, start, end, period=365, freq=1, kind='percent'):
    """
    Calculates a list of rates of return over a range of time.
    INPUTS:
    start = overall start date, end = overall end date
    periodperiod = # of days over which to calculate the rate of return
        Example: yearly return = 365
    freq = how often to sample
        Example: calculate return every day = 1, once a year = 365
    kind = measure of return (percent or log)
    Ignores partial periods at the end when freq > 1 day.
    """
    rates = []
    #Can't use "range" with dates instead of integers so using a while loop for now
    day = start
    while day < end:
        try:
            rates.append(calc_return(data, day, day + timedelta(days=period), kind=kind))
            day += timedelta(days=freq)
        except KeyError:
            day += timedelta(days=1) #Lazy - this will shift all the future dates too, but can fix
    return np.array(rates)


def calc_risk_stddev(data, start, end, period=365, kind='percent'):
    """
    Risk measure: standard deviation of rate of return.
    INPUTS:
    period = # of days over which to calculate rate of return
        Example: yearly return = 365
    kind = measure of return (percent or log)
    """
    return np.std(return_list(data, start, end, period, 
        freq=period, kind=kind))
    #Requires frequency and period to be the same...is this correct?


def calc_risk_proba(data, start, end, rate=0, period=365, freq=1, kind='percent'):
    """
    Risk measure: historical probability of return below a certain value.
    INPUTS:
    period = # of days over which to calculate rate of return
        Example: yearly return = 365
    freq = how often to sample
        Example: calculate return every day = 1, once a year = 365  
    rate = threshold rate of return
    kind = measure of return (percent or log)
    """
    return np.mean(return_list(data, start, end, period, 
        freq, kind) < rate)


#We will want to cache this
def track_portfolio(percent, rebal_time, start, end):
    """
    Computes values of a portfolio with given percentages of certain indices.
    INPUTS:
    percent = dictionary of investment data frames with percentages
        (values must add to 1)
    rebal_time = how often to rebalance the portfolio (# of days)
    start, end = start and end dates to compute values
    """
    assert np.isclose(sum(percent.values()), 1)
    portfolio_value = {}
    shares = {}
    #Standardize to value of 100 starting out
    day = start
    rebal = 0
    #Probably want to change this to an operation on entire DataFrames for time periods between rebalances
    while day < end:
        #Need to get around missing days for now
        try:
            for k, v in enumerate(percent):
                if rebal == rebal_time:
                    shares[k] = k.loc[day] / (v*100)
                    rebal = 0
                portfolio_value[day] = sum(v * k.loc[day] for k in percent.keys())
        except KeyError:
            pass
        day += 1
        rebal += 1
    #Need to add extra dates
    #Need to add DateTimeIndex
    return pd.DataFrame(portfolio_value)


def plot_risk_return(portfolios, start, end, return_type='percent', risk_type='stddev', period=365, freq=None, rate=None):
    """
    INPUTS:
    portfolios = list of portfolio data frames
    start, end = start and end dates for measuring risk and return
    period = period for measuring risk
    freq = how often to sample for measuring risk
    rate = threshold rate of return (for probability risk measure)
    return_type = percent or log
    risk_type = stddev or proba
    """
    x = [calc_return(p, start, end, kind) for p in portfolios]
    if risk_type == 'stddev':
        y = [calc_risk_stddev(p, start, end, period=period, kind=kind) 
            for p in portfolios]
    elif risk_type == 'proba':
        if freq == 'None' or rate == 'None':
            raise "You must specify freq and rate for probability risk measure."
        else:
            pass
        y = [calc_risk_proba(p, start, end, rate=rate, period=period, freq=freq, kind=kind) 
            for p in portfolios]
    else:
        raise "Risk type must be stddev or proba." #This will change as we add more risk measures.
    plt.scatter(x, y)
    plt.xlabel("Total %s return over given time period") %(return_type)
    plt.ylabel("Risk over given time period")
    #Need to label points with name of dataframe