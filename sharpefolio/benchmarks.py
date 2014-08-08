import MySQLdb
import datamapper as dm

class Benchmark(object):
	def __init__(self, symbol, name, id = None):
		self.id = id
		self.symbol = symbol
		self.name = name

class BenchmarkMapper(dm.Mapper):

	def find_all(self):
		return self._repository.find_all()

class BenchmarkMysqlRepository(dm.MysqlRepository):

	def find_all(self):
		cursor = self._database.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM `benchmarks`')
		return dm.Collection(Benchmark, cursor)

class Price(object):
	def __init__(self, benchmark_id, date, closing_price, id = None):
		self.id = id
		self.benchmark_id = benchmark_id
		self.date = date
		self.closing_price = closing_price

class PriceMapper(dm.Mapper):
	def insert(self, model):
		self._repository.insert(model)

	def find_by_benchmark_id(self, benchmark_id):
		return self._repository.find_by_benchmark_id(benchmark_id)

	def find_by_benchmark_id_in_range(self, benchmark_id, start_date, end_date):
		return self._repository.find_by_benchmark_id_in_range(benchmark_id, start_date, end_date)

	def find_by_benchmark_id_until_day(self, benchmark_id, until_date, limit=100000000):
		return self._repository.find_by_benchmark_id_until_day(benchmark_id, until_date, limit)

	def find_last_date(self):
		return self._repository.find_last_date()

class PriceMysqlRepository(dm.MysqlRepository):
	def insert(self, model):
		if model.id == None:
			self._insert_no_pk(model)
		else:
			self._insert_full(model)

	def _insert_full(self, model):
		cursor = self._database.cursor()
		cursor.execute('\
			INSERT INTO `benchmark_prices`\
			(`id`, `benchmark_id`, `date`, `closing_price`)\
			VALUES(%s, %s, %s, %s)',
			(model.id, model.benchmark_id, model.date, model.closing_price)
		)
		self._database.commit()

	def _insert_no_pk(self, model):
		cursor = self._database.cursor()
		cursor.execute('\
			INSERT INTO `benchmark_prices`\
			(`benchmark_id`, `date`, `closing_price`)\
			VALUES(%s, %s, %s, %s)',
			(model.benchmark_id, model.date, model.closing_price)
		)
		self._database.commit()

	def find_by_benchmark_id(self, benchmark_id):
		cursor = self._database.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM `benchmark_prices` WHERE `benchmark_id` = %s ORDER BY `date` ASC', (benchmark_id,))
		return dm.Collection(Price, cursor)

	def find_by_benchmark_id_in_range(self, benchmark_id, start_date, end_date):
		cursor = self._database.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute("\
			SELECT *\
			FROM `benchmark_prices`\
			WHERE `benchmark_id` = %s\
			AND `date` >= %s\
			AND `date` <= %s\
			ORDER BY `date` ASC", (benchmark_id, start_date.isoformat(), end_date.isoformat())
		)
		return dm.Collection(Price, cursor)

	def find_by_benchmark_id_until_day(self, benchmark_id, until_date, limit):
		cursor = self._database.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute("\
			SELECT *\
			FROM `benchmark_prices`\
			WHERE `benchmark_id` = %s\
			AND `date` <= %s\
			ORDER BY `date` DESC\
			LIMIT %s", (benchmark_id, until_date.isoformat(), limit)
		)
		return dm.Collection(Price, cursor)

	def find_last_date(self):
		cursor = self._database.cursor()
		cursor.execute("\
			SELECT *\
			FROM `benchmark_prices`\
			ORDER BY `date` DESC\
			LIMIT 1"
		)
		result = cursor.fetchone()
		return result[2]

