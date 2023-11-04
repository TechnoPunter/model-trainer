import importlib
import logging
import os

import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine, Engine, insert
from sqlalchemy.orm import sessionmaker

from trainer.config.reader import cfg

# Create the base class for declarative models
Base = sqlalchemy.orm.declarative_base()

logger = logging.getLogger(__name__)


def table_repr(self):
    members = vars(self)
    members_string = ', '.join(f'{key}={value}' for key, value in members.items())
    return f'{self.__class__.__name__}({members_string})'


Base.__repr__ = table_repr


class DatabaseEngine:
    cfg: dict
    engine: Engine
    tables: list

    def __init__(self):
        self.cfg = cfg
        self.engine = self.get_connection()
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        self.package_name = 'trainer.datamodels'
        self.tables = self.load_tables('../../', self.package_name)

    def __del__(self):
        self.session.close()

    def get_connection(self):
        pg_config = self.cfg['postgres']
        username = pg_config['username']
        password = pg_config['password']
        host = pg_config['host']
        port = pg_config['port']
        database = pg_config['database']
        connection_string = f'postgresql://{username}:{password}@{host}:{port}/{database}'
        return create_engine(connection_string)

    def load_tables(self, base_path: str, package_name: str):
        result = []
        package_path = package_name.replace('.', '/')
        package_directory = os.path.dirname(__file__)
        package_directory = os.path.join(package_directory, base_path, package_path)

        # Loop through all files in the package directory
        for filename in os.listdir(package_directory):
            if filename.endswith('.py') and not (filename.startswith("__")):
                module_name = filename[:-3]  # Remove the '.py' extension
                module_path = f'{package_name}.{module_name}'
                try:
                    module = importlib.import_module(module_path)
                    result.append(module)
                except ImportError as e:
                    logger.error(f'Error importing module {module_path}: {e}')

        return result

    def log_entry(self, table, data):
        m = next((m for m in self.tables if m.__name__ == self.package_name + "." + table), None)
        assert m is not None, f"Invalid table name {table}"
        obj = eval(f"m.{table}(**data)")
        self._insert(obj)

    def _insert(self, obj):
        with self.Session.begin() as session:
            try:
                session.add(obj)
                session.commit()
            except Exception as ex:
                logger.error(f"Exception in inserting {obj}, exception {ex}")

    def query(self, table, predicate):
        m = next((m for m in self.tables if m.__name__ == self.package_name + "." + table), None)
        assert m is not None, f"Invalid table name {table}"
        results = eval(f"self.session.query(m.{table}).filter({predicate}).all()")
        return results

    def run_query(self, tbl: str, predicate: str = None):
        query = f'SELECT * FROM {tbl}'

        if predicate is not None:
            query += " WHERE "
            query += predicate

        # Read the data into a DataFrame
        logger.debug(query)
        df = pd.read_sql(query, self.engine)
        return df

    def delete_recs(self, table: str, predicate: str = None):
        m = next((m for m in self.tables if m.__name__ == self.package_name + "." + table), None)
        assert m is not None, f"Invalid table name {table}"
        delete = eval(f"self.session.query(m.{table}).filter({predicate}).delete(synchronize_session=False)")
        self.session.commit()
        return delete

    def create_table(self, table):
        m = next((m for m in self.tables if m.__name__ == self.package_name + "." + table), None)
        assert m is not None, f"Invalid table name {table}"
        result = eval(f"m.{table}.__table__.create(self.engine)")
        print(result)

    def bulk_insert(self, table: str, data: pd.DataFrame):
        m = next((m for m in self.tables if m.__name__ == self.package_name + "." + table), None)
        assert m is not None, f"Invalid table name {table}"
        if len(data) == 0:
            return
        eval(f'self.session.execute(insert(m.{table}), data.to_dict("records"))')
        self.session.commit()


if __name__ == "__main__":
    l = DatabaseEngine()
    # l.log_entry("Order", {"order_date": "2023-01-01", "price": 123.45, "direction": "BUY"})
    x = l.query("Order", "m.Order.order_id > 1")
    print(x)
    # l.create_table(table='TrainingResult')
    x = l.delete_recs(table='TrainingResult', predicate="m.TrainingResult.training_date == '2023-08-06'")
    print(x)
