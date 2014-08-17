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

	def batch_insert(self, models):
		self._repository.batch_insert(models)

	def find_highest_ratio(self, recipe_id, end_date, limit):
		return self._repository.find_highest_ratio(recipe_id, end_date, limit)

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

	def batch_insert(self, models):
		if len(models) == 0:
			return

		inserts = []
		for model in models:
			if model.ratio == model.ratio:
				inserts.append("(%d, %s, %f, '%s')" % (model.stock_id, model.recipe_id, model.ratio, model.date))
			else:
				# Use null if ratio is NaN.
				inserts.append("(%d, %s, null, '%s')" % (model.stock_id, model.recipe_id, model.date))

		cursor = self._database.cursor()
		cursor.execute('\
			INSERT IGNORE INTO `ratios`\
			(`stock_id`, `recipe_id`, `ratio`, `date`)\
			VALUES%s;' % (','.join(inserts),)
		)
		self._database.commit()

	def find_highest_ratio(self, recipe_id, end_date, limit):
		cursor = self._database.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM `ratios` WHERE recipe_id = %s AND `date` = %s ORDER BY ratio DESC LIMIT %s', (recipe_id, end_date.isoformat(), limit))
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

class RecipePrice(object):
	def __init__(self, recipe_id, date, closing_price, id = None):
		self.id = id
		self.recipe_id = recipe_id
		self.date = date
		self.closing_price = closing_price

class RecipePriceMapper(dm.Mapper):
	def insert(self, model):
		self._repository.insert(model)

	def find_by_recipe_id(self, recipe_id):
		return self._repository.find_by_recipe_id(recipe_id)

	def find_by_recipe_id_in_range(self, recipe_id, start_date, end_date):
		return self._repository.find_by_recipe_id_in_range(recipe_id, start_date, end_date)

	def find_by_recipe_id_until_day(self, recipe_id, until_date, limit=100000000):
		return self._repository.find_by_recipe_id_until_day(recipe_id, until_date, limit)

	def find_last_date(self):
		return self._repository.find_last_date()

class RecipePriceMysqlRepository(dm.MysqlRepository):
	def insert(self, model):
		if model.id == None:
			self._insert_no_pk(model)
		else:
			self._insert_full(model)

	def _insert_full(self, model):
		cursor = self._database.cursor()
		cursor.execute('\
			INSERT INTO `recipe_prices`\
			(`id`, `recipe_id`, `date`, `closing_price`)\
			VALUES(%s, %s, %s, %s)',
			(model.id, model.recipe_id, model.date, model.closing_price)
		)
		self._database.commit()

	def _insert_no_pk(self, model):
		cursor = self._database.cursor()
		cursor.execute('\
			INSERT INTO `recipe_prices`\
			(`recipe_id`, `date`, `closing_price`)\
			VALUES(%s, %s, %s)',
			(model.recipe_id, model.date, model.closing_price)
		)
		self._database.commit()

	def find_by_recipe_id(self, recipe_id):
		cursor = self._database.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM `recipe_prices` WHERE `recipe_id` = %s ORDER BY `date` ASC', (recipe_id,))
		return dm.Collection(RecipePrice, cursor)

	def find_by_recipe_id_in_range(self, recipe_id, start_date, end_date):
		cursor = self._database.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute("\
			SELECT *\
			FROM `recipe_prices`\
			WHERE `recipe_id` = %s\
			AND `date` >= %s\
			AND `date` <= %s\
			ORDER BY `date` ASC", (recipe_id, start_date.isoformat(), end_date.isoformat())
		)
		return dm.Collection(RecipePrice, cursor)

	def find_by_recipe_id_until_day(self, recipe_id, until_date, limit):
		cursor = self._database.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute("\
			SELECT *\
			FROM `recipe_prices`\
			WHERE `recipe_id` = %s\
			AND `date` <= %s\
			ORDER BY `date` DESC\
			LIMIT %s", (recipe_id, until_date.isoformat(), limit)
		)
		return dm.Collection(RecipePrice, cursor)

	def find_last_date(self):
		cursor = self._database.cursor()
		cursor.execute("\
			SELECT *\
			FROM `recipe_prices`\
			ORDER BY `date` DESC\
			LIMIT 1"
		)
		result = cursor.fetchone()
		return result[2]

class RecipeRatio(object):
	def __init__(self, recipe_id, ratio, date, id = None):
		self.id = id
		self.recipe_id = recipe_id
		self.ratio = ratio
		self.date = date

	def __str__(self):
		return "recipe_id: %d ratio: %d" % (self.recipe_id, self.ratio)

class RecipeRatioMapper(dm.Mapper):
	def insert(self, model):
		self._repository.insert(model)

	def find_highest_ratio(self, recipe_id, end_date, limit):
		return self._repository.find_highest_ratio(recipe_id, end_date, limit)

class RecipeRatioMysqlRepository(dm.MysqlRepository):
	def insert(self, model):
		cursor = self._database.cursor()
		cursor.execute('\
			INSERT INTO `ratios`\
			(`recipe_id`, `ratio`, `date`)\
			VALUES(%s, %s, %s)',
			(model.recipe_id, model.ratio, model.date)
		)
		self._database.commit()

	def find_highest_ratio(self, recipe_id, end_date, limit):
		cursor = self._database.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM `ratios` WHERE recipe_id = %s AND `date` = %s ORDER BY ratio DESC LIMIT %s', (recipe_id, end_date.isoformat(), limit))
		return dm.Collection(Ratio, cursor)


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

	def get_picks_for_recipe(self, recipe_id, date):
		return self._repository.get_picks_for_recipe(recipe_id, date)

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

	def get_picks_for_recipe(self, recipe_id, date):
		cursor = self._database.cursor(MySQLdb.cursors.DictCursor)
		# print "SELECT * FROM `picks` WHERE recipe_id = %s AND `date` = %s" % (recipe_id, date.isoformat(),)
		cursor.execute('SELECT * FROM `picks` WHERE recipe_id = %s AND `date` = %s AND `gain` IS NOT NULL', (recipe_id, date.isoformat(),))
		return dm.Collection(Pick, cursor)

