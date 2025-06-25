import psycopg2
from config.config import app_config


class Database:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=app_config.db.host,
            port=app_config.db.port,
            user=app_config.db.user,
            password=app_config.db.password,
            database=app_config.db.name
        )

    def execute(self, query: str, params=None):
        with self.conn.cursor() as cursor:
            try:
                cursor.execute(query, params)
                self.conn.commit()
            except Exception as e:
                self.conn.rollback()
                raise e

    def execute_with_result(self, query: str, params=None):
        with self.conn.cursor() as cursor:
            try:
                cursor.execute(query, params)
                self.conn.commit()
                affected_rows = cursor.rowcount
                return affected_rows
            except Exception as e:
                self.conn.rollback()
                raise e

    def select(self, query: str, params=None, fetch_one=False):
        with self.conn.cursor() as cursor:
            cursor.execute(query, params)
            if fetch_one:
                return cursor.fetchone()
            return cursor.fetchall()

    def commit(self):
        self.conn.commit()
