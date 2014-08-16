import numpy as np
from itertools import combinations
import sys,os
# Add the root of the repo to the include path.
sys.path.append(os.path.abspath('.'))
import datamapper as dm

class Ratio(object):
    '''
    all list parameters are expected to be an one dimensional
    list of nominal prices, e.g. [1,1.2,.3,10,.3,25]
    '''
    def __init__(self, prices, benchmark = None):
        self.prices = prices
        self.n = len(self.prices)
        self.benchmark = self._prepare_benchmark(benchmark)
        self.ret = np.diff(self.prices)
        self.n_ret = len(self.ret)
        self.b_ret = np.diff(self.benchmark)
        self.adj_ret = None
        self.std = None
        self.avg = None
        self.neg_ret = None
        self.neg_ret_sum = None
        self.down_risk = None

    def sharpe(self):

        self.adj_ret = np.array([a - b for a, b in zip(self.ret, self.b_ret)])
        self.std = np.std(self.adj_ret, dtype=np.float64, ddof=1)

        return self._get_info_ratio()

    def sortino(self):
        '''
        sortino is an adjusted ratio which only takes the 
        standard deviation of negative returns into account
        '''
        self.adj_ret = np.array([a - b for a, b in zip(self.ret, self.b_ret)])
        self.avg = np.mean(self.adj_ret)

        # Take all negative returns.
        self.neg_ret = np.array([a ** 2 for a in self.adj_ret if a < 0])
        # Sum it.
        self.neg_ret_sum = np.sum(self.neg_ret)
        # And calculate downside risk as second order lower partial moment.
        self.down_risk = np.sqrt(self.neg_ret_sum / self.n_ret)

        sortino = self.avg / (1 + self.down_risk)

        return sortino

    def _get_info_ratio(self):

        self.avg = np.mean(self.adj_ret)

        return self.avg / (1 + self.std)

    def _prepare_benchmark(self, benchmark):

        if benchmark == None:
            benchmark = np.zeros(self.n)
        if len(benchmark) != self.n:
            raise Exception("benchmark mismatch")

        return benchmark

class InvertedCorrelationPicker(object):

    def __init__(self, stocks):

        '''
        stocks = {
                  "AAPL": [0.23, 0.24, 0.25, 0.26],
                  "TWTR": [-0.23, -0.24, -0.25, -0.26],
                  "FB"  : [0.23, 0.24, 0.25, 0.26],
                  "LNKD": [-0.23, -0.24, -0.25, -0.26],
                  "ZNGA": [0.23, 0.24, 0.25, 0.26],
                  "GRPN": [0.3, 0.29, 0.4, 0.23],
                  "IBM" : [0.23, 0.25, 0.26],
                  "MSFT": [0.23, 0.24, 0.25, 0.26],
                  "GOOG": [0.23, 0.24, 0.25, 0.26],
                 }
        picker = InvertedCorrelationPicker(stocks)
        '''
        self.dates = {}
        max_date_len = 0
        max_date_symbol = ""
        for symbol in stocks.keys():
            self.dates[symbol] = [price.date for price in stocks[symbol]]
            date_len = len(self.dates[symbol])
            if date_len > max_date_len:
                max_date_len = date_len
                max_date_symbol = symbol

        self.stocks = {}
        if max_date_symbol != "":
            for i, date in enumerate(self.dates[max_date_symbol]):
                for symbol in stocks.keys():
                    if self.stocks.has_key(symbol) is False:
                        self.stocks[symbol] = []

                    insert_price = None
                    for price in stocks[symbol]:
                        if price.date == date:
                            insert_price = price.closing_price
                            break

                    self.stocks[symbol].append(insert_price)

        # backward fill
        for symbol in self.stocks.keys():
            last_price = None
            for i, price in enumerate(self.stocks[symbol]):
                if price != None:
                    last_price = price
                else:
                    self.stocks[symbol][i] = last_price

        # forward fill
        for symbol in self.stocks.keys():
            last_price = None
            for i, price in reversed(list(enumerate(self.stocks[symbol]))):
                if price != None:
                    last_price = price
                else:
                    self.stocks[symbol][i] = last_price

        if len(self.stocks) == 0:
            self.stocks = stocks

        self.price_len = 0
        self.stocks_len = 0
        self.cov_data = []
        self.cormat = []
        self.portfolios = []
        self.total_corr = []
        self.nanmin = []

    def pick(self, portfolio_size=4):

        '''
        picker.pick(4)
        '''

        self.price_len = 0
        self.stocks_len = len(self.stocks)
        ids = [id for id in self.stocks.keys()]

        # Determine depth of matrix
        for symbol in ids:
            if isinstance(self.stocks[symbol], dm.Collection):
                length = self.stocks[symbol].count()
            else:
                length = len(self.stocks[symbol])
            if length > self.price_len:
                self.price_len = length

        if portfolio_size > self.stocks_len:
            # Pick everything!
            print "stocks length", self.stocks_len, "too small, pick everything!"
            return ids

        # Create an empty datastructure to hold the daily returns
        self.cov_data = np.zeros((self.price_len, self.stocks_len))

        # Grab the daily returns for those stocks and put them in cov index
        for i, symbol in enumerate(ids):
            prices = self.stocks[symbol]
            # n = len(prices)
            # if n < price_len:
                # Forward fill
                # prices += prices[-1:]*(price_len-n)
            self.cov_data[:,i] = prices

        # Make a correlation matrix
        self.cormat = np.corrcoef(self.cov_data.transpose())

        # Create all possible combinations of the n top equites for the given portfolio size.
        self.portfolios = list(combinations(range(0, self.stocks_len), portfolio_size))

        if len(self.portfolios) == 0:
            print "portfolio length is empty, return ids"
            return ids[:portfolio_size]

        # Add up all the correlations for each possible combination
        self.total_corr = [sum([self.cormat[x[0]][x[1]] for x in combinations(p, 2)]) for p in self.portfolios]

        # Find the portfolio with the smallest sum of correlations
        try:
            picks = [ids[i] for i in self.portfolios[self.total_corr.index(np.nanmin(self.total_corr))]]
        except Exception:
            print "something went wrong with picks, return ids"
            return ids[:portfolio_size]
            pass

        return picks[:portfolio_size]
