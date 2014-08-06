import json
import MySQLdb
import datamapper as dm

class YahooSyncLog(object):
    def __init__(self, stock_id, year, month, is_successful, log = {'errors': []}, id = None):
        self.id = id
        self.stock_id = stock_id
        self.year = year
        self.month = month
        self.is_successful = is_successful
        self.log = log

    def append_error_log(self, error_log, set_failed = True):
        self.log['errors'].append(error_log)
        if set_failed:
            self.is_successful = False

    def reset_error_log(self, update_is_successful = False):
        self.log['errors'] = []
        if update_is_successful:
            self.is_successful = True


class YahooSyncLogMapper(dm.Mapper):
    def save(self, model):
        self._repository.save(model)

    def insert(self, model):
        self._repository.insert(model)

    def find_by_stock_year_and_month(self, stock_id, year, month):
        return self._repository.find_by_stock_year_and_month(stock_id, year, month)

class YahooSyncLogMysqlRepository(dm.MysqlRepository):
    def save(self, model):
        if model.id == None:
            return self.insert(model)
        else:
            return self.update(model)

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

    def update(self, model):
        cursor = self._database.cursor()
        cursor.execute('\
            UPDATE `yahoo_sync_logs`\
            SET\
                `stock_id` = %s,\
                `year` = %s,\
                `month` = %s,\
                `is_successful` = %s,\
                `log` = %s\
            WHERE `id` = %s',
            (
                model.stock_id,
                model.year,
                model.month,
                int(model.is_successful),
                json.dumps(model.log, indent = 4, separators = (',', ': ')),
                model.id
            )
        )
        self._database.commit()

    def find_by_stock_year_and_month(self, stock_id, year, month):
        cursor = self._database.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('\
            SELECT * FROM `yahoo_sync_logs`\
            WHERE `stock_id` = %s\
            AND `year` = %s\
            AND `month` = %s\
            LIMIT 1',
            (
                stock_id,
                year,
                month
            )
        )

        # Use the collection class for datamaps but return the first result.
        collection = dm.Collection(YahooSyncLog, cursor, self._datamap)
        for item in collection:
            return item

    def _datamap(self, data):
        data['is_successful'] = int(data['is_successful'])
        data['year'] = int(data['year'])
        data['month'] = int(data['month'])
        data['is_successful'] = data['is_successful'] == 1
        try:
            data['log'] = json.loads(data['log'])
        except ValueError:
            # Default to the empty list if we have json parsing errors.
            data['log'] = {'errors': []}

        return data
