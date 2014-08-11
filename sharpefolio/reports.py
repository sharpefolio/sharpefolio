import datetime
import MySQLdb
import datamapper as dm

class Report(object):
	def __init__(self, date, duration, formula, id=None):
		self.id = id
		self.date = date
		self.duration = duration
		self.formula = formula

	def start_date(self):
		start_date = self.date
		weekdays = 0;
		while weekdays < self.duration:
			start_date -= datetime.timedelta(days=1)
			if start_date.weekday() < 5:
				weekdays += 1

		return start_date

class ReportMapper(dm.Mapper):
	def insert(self, model):
		self._repository.insert(model)

	def find_all(self):
		return self._repository.find_all()

	def find_within_date(self, since_date, until_date):
		return self._repository.find_within_date(since_date, until_date)

	def find_until_date(self, until_date):
		return self._repository.find_until_date(until_date)

	def find_until_date_with_duration_and_formula(self, until_date, duration, formula):
		return self._repository.find_until_date_with_duration_and_formula(
			until_date, duration, formula
		)

class ReportMysqlRepository(dm.MysqlRepository):
	def insert(self, model):
		cursor = self._database.cursor()
		cursor.execute('\
			INSERT INTO `reports`\
			(`date`, `duration`, `formula`)\
			VALUES(%s, %s, %s)',
			(model.date, model.duration, model.formula)
		)
		self._database.commit()
		model.id = cursor.lastrowid

	def find_all(self):
		cursor = self._database.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM `reports`')
		return dm.Collection(Report, cursor, self._datamap)

	def find_within_date(self, since_date, until_date):
		cursor = self._database.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM `reports` WHERE `date` >= %s AND `date` <= %s ORDER BY `date` DESC', (since_date, until_date))
		return dm.Collection(Report, cursor, self._datamap)

	def find_until_date(self, until_date):
		cursor = self._database.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM `reports` WHERE date <= %s', (until_date,))
		return dm.Collection(Report, cursor, self._datamap)

	def find_until_date_with_duration_and_formula(self, until_date, duration, formula):
		cursor = self._database.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM `reports` WHERE date <= %s AND duration = %s AND formula = %s', 
			(until_date, duration, formula)
		)
		return dm.Collection(Report, cursor, self._datamap)

	def _datamap(self, data):
		data['date'] = datetime.datetime.strptime("%s" % data['date'], "%Y-%m-%d").date()
		return data

class Ratio(object):
	def __init__(self, stock_id, recipe_id, ratio, date, id = None):
		self.id = id
		self.stock_id = stock_id
		self.recipe_id = recipe_id
		self.ratio = ratio
		self.date = date

	def __str__(self):
		return "stock_id: %d recipe_id: %d ratio: %d" % (self.stock_id, self.recipe_id, self.ratio)

class RatioMapper(dm.Mapper):
	def insert(self, model):
		self._repository.insert(model)

	def find_highest_ratio(self, recipe_id, limit):
		return self._repository.find_highest_ratio(recipe_id, limit)

class RatioMysqlRepository(dm.MysqlRepository):
	def insert(self, model):
		cursor = self._database.cursor()
		cursor.execute('\
			INSERT INTO `ratios`\
			(`stock_id`, `recipe_id`, `ratio`, `date`)\
			VALUES(%s, %s, %s, %s)',
			(model.stock_id, model.recipe_id, model.ratio, model.date)
		)
		self._database.commit()

	def find_highest_ratio(self, recipe_id, limit):
		cursor = self._database.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM `ratios` WHERE recipe_id = %s ORDER BY ratio DESC LIMIT %s', (recipe_id, limit))
		return dm.Collection(Ratio, cursor)

class Recipe(object):
	def __init__(self, report_formula, report_duration, n_stocks=4, check_correlation=False, distribution='even', check_benchmark_id = 0, id=None):
		self.id = id
		self.n_stocks = n_stocks
		self.check_correlation = check_correlation
		self.distribution = distribution
		self.report_formula = report_formula
		self.report_duration = report_duration
		self.check_benchmark_id = check_benchmark_id

class RecipeMapper(dm.Mapper):
	def insert(self, model):
		self._repository.insert(model)

	def find_all(self):
		return self._repository.find_all()

	def truncate(self):
		self._repository.truncate()

class RecipeMysqlRepository(dm.MysqlRepository):
	def insert(self, model):
		cursor = self._database.cursor()
		# q = '\
		# 	INSERT INTO `recipes`\
		# 	(`n_stocks`, `check_correlation`, `distribution`,`report_duration`, `report_formula`)\
		# 	VALUES(%s, %s, %s, %s, %s)' % (model.n_stocks, int(model.check_correlation), model.distribution, model.report_duration, model.report_formula)
		# print q
		cursor.execute('\
			INSERT INTO `recipes`\
			(`n_stocks`, `check_correlation`, `distribution`,`report_duration`, `report_formula`, `check_benchmark_id`)\
			VALUES(%s, %s, %s, %s, %s, %s)',
			(model.n_stocks, int(model.check_correlation), model.distribution, model.report_duration, model.report_formula, model.check_benchmark_id)
		)
		self._database.commit()
		model.id = cursor.lastrowid

	def find_all(self):
		cursor = self._database.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM `recipes`')
		return dm.Collection(Recipe, cursor)

	def truncate(self):
		cursor = self._database.cursor()
		cursor.execute('TRUNCATE recipes')
		self._database.commit()

class Pick(object):
	def __init__(self, recipe_id, stock_id, weight, gain, date, id=None):
		self.id = id
		self.recipe_id = recipe_id
		self.stock_id = stock_id
		self.weight = weight
		self.gain = gain
		self.date = date

class PickMapper(dm.Mapper):
	def insert(self, model):
		self._repository.insert(model)

class PickMysqlRepository(dm.MysqlRepository):
	def insert(self, model):
		cursor = self._database.cursor()
		cursor.execute('\
			INSERT INTO `picks`\
			(`recipe_id`, `stock_id`, `weight`, `gain`, `date`)\
			VALUES(%s, %s, %s, %s, %s)',
			(model.recipe_id, model.stock_id, model.weight, model.gain, model.date)
		)
		self._database.commit()
		model.id = cursor.lastrowid
