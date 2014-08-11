import numpy as np
from itertools import combinations

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

	def pick(self, portfolio_size=4):

		'''
		picker.pick(4)
		'''

		price_len = 0
		stocks_len = len(self.stocks)
		ids = [id for id in self.stocks.keys()]

		# Determine depth of matrix
		for symbol in ids:
			length = len(self.stocks[symbol])
			if length > price_len:
				price_len = length

		if portfolio_size > price_len:
			# Pick everything!
			return ids

		# Create an empty datastructure to hold the daily returns
		cov_data = np.zeros((price_len, stocks_len))

		# Grab the daily returns for those stocks and put them in cov index
		for i, symbol in enumerate(ids):
			prices = self.stocks[symbol]
			# n = len(prices)
			# if n < price_len:
				# Forward fill
				# prices += prices[-1:]*(price_len-n)
			cov_data[:,i] = prices

		# Make a correlation matrix
		cormat = np.corrcoef(cov_data.transpose())

		# Create all possible combinations of the n top equites for the given portfolio size.
		portfolios = list(combinations(range(0, stocks_len), portfolio_size))

		if len(portfolios) == 0:
			return ids

		# Add up all the correlations for each possible combination
		total_corr = [sum([cormat[x[0]][x[1]] for x in combinations(p, 2)]) for p in portfolios]

		print "ids:", ids, "portfolios:", portfolios

		# Find the portfolio with the smallest sum of correlations
		picks = [ids[i] for i in portfolios[total_corr.index(np.nanmin(total_corr))]]

		return picks
