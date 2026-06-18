from datetime import date

import pymssql

from autometrics_engine.domain.repositories.source_extractor import SourceExtractor
from autometrics_engine.domain.entities.product import Product
from autometrics_engine.domain.entities.store import Store


class PymssqlExtractor(SourceExtractor):

    def __init__(self, host: str, port: int, database: str, user: str, password: str):
        self._host = host
        self._port = port
        self._database = database
        self._user = user
        self._password = password

    def _connect(self):
        return pymssql.connect(
            server=self._host,
            port=self._port,
            user=self._user,
            password=self._password,
            database=self._database,
        )

    def get_products(self) -> list[Product]:
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, category, subcategory, brand, cost_price, sale_price FROM products")
            return [
                Product(id=r[0], name=r[1], category=r[2], subcategory=r[3],
                        brand=r[4], cost_price=float(r[5]) if r[5] else None,
                        sale_price=float(r[6]) if r[6] else None)
                for r in cursor.fetchall()
            ]
        finally:
            conn.close()

    def get_stores(self) -> list[Store]:
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, region, city, type FROM stores")
            return [
                Store(id=r[0], name=r[1], region=r[2], city=r[3], type=r[4])
                for r in cursor.fetchall()
            ]
        finally:
            conn.close()

    def get_sales_since(self, last_date: date) -> list[tuple]:
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, product_id, store_id, quantity, unit_price, total, sale_date, "
                "COALESCE(discount,0), COALESCE(customer_id,0) "
                "FROM sales WHERE sale_date > %s",
                (last_date,),
            )
            return list(cursor.fetchall())
        finally:
            conn.close()
