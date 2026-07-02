import sqlite3
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

DB_FILE = "bike_products.db"

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS MyProduct (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price INTEGER NOT NULL
)
"""


class BikeProductManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("자전거 용품 관리")
        self.setGeometry(300, 200, 640, 520)

        self.setStyleSheet("""
            QWidget {
                background-color: #1f2937;
                color: #e5e7eb;
                font-family: 'Malgun Gothic', '맑은 고딕', Arial, sans-serif;
            }
            QLabel {
                font-size: 14px;
                color: #f8fafc;
            }
            QLineEdit {
                border: 2px solid #4b5563;
                border-radius: 8px;
                padding: 8px;
                background-color: #111827;
                color: #f8fafc;
            }
            QPushButton {
                background-color: #2563eb;
                color: #ffffff;
                border-radius: 10px;
                padding: 10px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
            QPushButton:pressed {
                background-color: #1e40af;
            }
            QTableWidget {
                background-color: #111827;
                gridline-color: #374151;
                border: 1px solid #374151;
            }
            QHeaderView::section {
                background-color: #111827;
                color: #f8fafc;
                border: 1px solid #374151;
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #2563eb;
                color: #ffffff;
            }
        """)

        self.conn = sqlite3.connect(DB_FILE)
        self.conn.row_factory = sqlite3.Row
        self._create_table()

        self.name_input = QLineEdit()
        self.price_input = QLineEdit()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("검색어를 입력하세요")

        self.add_button = QPushButton("입력")
        self.update_button = QPushButton("수정")
        self.delete_button = QPushButton("삭제")
        self.search_button = QPushButton("검색")
        self.show_all_button = QPushButton("전체보기")

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["id", "name", "price"])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(
            "QTableWidget { background-color: #111827; alternate-background-color: #1f2937; }"
        )

        self._build_ui()
        self._connect_signals()

        self.load_products()

    def _create_table(self):
        with self.conn:
            self.conn.execute(CREATE_TABLE_SQL)

    def _build_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("상품명:"))
        name_layout.addWidget(self.name_input)
        name_layout.addWidget(QLabel("가격:"))
        name_layout.addWidget(self.price_input)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.update_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch(1)
        button_layout.addWidget(self.search_input)
        button_layout.addWidget(self.search_button)
        button_layout.addWidget(self.show_all_button)

        main_layout = QVBoxLayout(central_widget)
        main_layout.addLayout(name_layout)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.table)

    def _connect_signals(self):
        self.add_button.clicked.connect(self.add_product)
        self.update_button.clicked.connect(self.update_product)
        self.delete_button.clicked.connect(self.delete_product)
        self.search_button.clicked.connect(self.search_products)
        self.show_all_button.clicked.connect(self.load_products)
        self.table.itemSelectionChanged.connect(self.on_table_selection)

    def load_products(self):
        cursor = self.conn.execute("SELECT id, name, price FROM MyProduct ORDER BY id")
        rows = cursor.fetchall()
        self._fill_table(rows)

    def _fill_table(self, rows):
        self.table.setRowCount(0)
        for row in rows:
            row_index = self.table.rowCount()
            self.table.insertRow(row_index)
            self.table.setItem(row_index, 0, QTableWidgetItem(str(row["id"])))
            self.table.setItem(row_index, 1, QTableWidgetItem(row["name"]))
            self.table.setItem(row_index, 2, QTableWidgetItem(str(row["price"])))
        self.table.resizeColumnsToContents()

    def add_product(self):
        name = self.name_input.text().strip()
        price_text = self.price_input.text().strip()
        if not name or not price_text:
            self._show_warning("상품명과 가격을 모두 입력하세요.")
            return

        if not price_text.isdigit():
            self._show_warning("가격은 숫자여야 합니다.")
            return

        price = int(price_text)
        with self.conn:
            self.conn.execute("INSERT INTO MyProduct (name, price) VALUES (?, ?)", (name, price))

        self._clear_inputs()
        self.load_products()

    def update_product(self):
        selected_id = self._selected_product_id()
        if selected_id is None:
            self._show_warning("수정할 항목을 먼저 선택하세요.")
            return

        name = self.name_input.text().strip()
        price_text = self.price_input.text().strip()
        if not name or not price_text:
            self._show_warning("상품명과 가격을 모두 입력하세요.")
            return

        if not price_text.isdigit():
            self._show_warning("가격은 숫자여야 합니다.")
            return

        price = int(price_text)
        with self.conn:
            self.conn.execute(
                "UPDATE MyProduct SET name = ?, price = ? WHERE id = ?",
                (name, price, selected_id),
            )

        self._clear_inputs()
        self.load_products()

    def delete_product(self):
        selected_id = self._selected_product_id()
        if selected_id is None:
            self._show_warning("삭제할 항목을 먼저 선택하세요.")
            return

        response = QMessageBox.question(
            self,
            "삭제 확인",
            f"ID {selected_id} 항목을 삭제하시겠습니까?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if response != QMessageBox.StandardButton.Yes:
            return

        with self.conn:
            self.conn.execute("DELETE FROM MyProduct WHERE id = ?", (selected_id,))

        self._clear_inputs()
        self.load_products()

    def search_products(self):
        keyword = self.search_input.text().strip()
        if not keyword:
            self.load_products()
            return

        cursor = self.conn.execute(
            "SELECT id, name, price FROM MyProduct WHERE name LIKE ? ORDER BY id",
            (f"%{keyword}%",),
        )
        rows = cursor.fetchall()
        self._fill_table(rows)

    def on_table_selection(self):
        selected_id = self._selected_product_id()
        if selected_id is None:
            return

        cursor = self.conn.execute(
            "SELECT id, name, price FROM MyProduct WHERE id = ?",
            (selected_id,),
        )
        row = cursor.fetchone()
        if row:
            self.name_input.setText(row["name"])
            self.price_input.setText(str(row["price"]))

    def _selected_product_id(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            return None
        return int(selected_items[0].text())

    def _clear_inputs(self):
        self.name_input.clear()
        self.price_input.clear()
        self.search_input.clear()
        self.table.clearSelection()

    def _show_warning(self, message):
        QMessageBox.warning(self, "경고", message)

    def closeEvent(self, event):
        self.conn.close()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BikeProductManager()
    window.show()
    sys.exit(app.exec())
