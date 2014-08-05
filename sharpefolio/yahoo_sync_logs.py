import json
import MySQLdb
import datamapper as dm

class YahooSyncLog(object):
    def __init__(self, stock_id, year, month, is_successful, log, id = None):
        self.id = id
        self.stock_id = stock_id
        self.year = year
        self.month = month
        self.is_successful = is_successful
        self.log = log

class YahooSyncLogMapper(dm.Mapper):
    def insert(self, model):
        self._repository.insert(model)

class YahooSyncLogMysqlRepository(dm.MysqlRepository):
    def insert(self, model):
        cursor = self._database.cursor()
        cursor.execute('\
            INSERT INTO `yahoo_sync_logs`\
            (`stock_id`, `year`, `month`, `is_successful`, `log`)\
            VALUES(%s, %s, %s, %s, %s)',
            (
                model.stock_id,
                model.year,
                model.month,
                int(model.is_successful),
                json.dumps(model.log, indent = 4, separators = (',', ': '))
            )
        )
        self._database.commit()
