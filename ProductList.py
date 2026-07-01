import sqlite3
from pathlib import Path


class ProductManager:
    def __init__(self, db_name: str = "MyProduct.db"):
        self.db_path = Path(__file__).resolve().parent / db_name
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def create_table(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Products (
                productID INTEGER PRIMARY KEY,
                productName TEXT NOT NULL,
                productPrice INTEGER NOT NULL
            )
            """
        )
        self.conn.commit()

    def insert_product(self, product_id: int, product_name: str, product_price: int):
        self.cursor.execute(
            "INSERT INTO Products (productID, productName, productPrice) VALUES (?, ?, ?)",
            (product_id, product_name, product_price),
        )
        self.conn.commit()

    def insert_many_products(self, products):
        self.cursor.executemany(
            "INSERT INTO Products (productID, productName, productPrice) VALUES (?, ?, ?)",
            products,
        )
        self.conn.commit()

    def update_product(self, product_id: int, product_name: str = None, product_price: int = None):
        if product_name is None and product_price is None:
            raise ValueError("수정할 값이 없습니다.")

        fields = []
        values = []

        if product_name is not None:
            fields.append("productName = ?")
            values.append(product_name)
        if product_price is not None:
            fields.append("productPrice = ?")
            values.append(product_price)

        values.append(product_id)
        self.cursor.execute(
            f"UPDATE Products SET {', '.join(fields)} WHERE productID = ?",
            values,
        )
        self.conn.commit()

    def delete_product(self, product_id: int):
        self.cursor.execute("DELETE FROM Products WHERE productID = ?", (product_id,))
        self.conn.commit()

    def select_products(self):
        self.cursor.execute("SELECT productID, productName, productPrice FROM Products ORDER BY productID")
        return self.cursor.fetchall()

    def select_product(self, product_id: int):
        self.cursor.execute(
            "SELECT productID, productName, productPrice FROM Products WHERE productID = ?",
            (product_id,),
        )
        return self.cursor.fetchone()

    def close(self):
        self.conn.close()


def generate_sample_products(count: int = 1000):
    products = []
    for i in range(1, count + 1):
        product_name = f"전자제품_{i:04d}"
        product_price = 10000 + (i % 100) * 500
        products.append((i, product_name, product_price))
    return products


if __name__ == "__main__":
    manager = ProductManager()
    manager.create_table()

    manager.cursor.execute("DELETE FROM Products")
    manager.conn.commit()

    sample_products = generate_sample_products(1000)
    manager.insert_many_products(sample_products)

    print(f"DB 경로: {manager.db_path}")
    print(f"총 제품 수: {len(manager.select_products())}")

    sample_product = manager.select_product(1)
    print("첫 제품:", dict(sample_product))

    manager.update_product(1, product_name="전자제품_0001_업데이트", product_price=15000)
    print("업데이트 후 첫 제품:", dict(manager.select_product(1)))

    manager.delete_product(2)
    print("제품 2 삭제 후 존재 여부:", manager.select_product(2))

    manager.close()
