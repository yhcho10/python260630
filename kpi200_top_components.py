import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from openpyxl import Workbook
from PyQt6.QtCore import QThread, pyqtSignal, QObject
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QMessageBox,
    QPushButton,
    QProgressBar,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

BASE_URL = 'https://finance.naver.com/sise/entryJongmok.naver?type=KPI200'
HEADERS = {'User-Agent': 'Mozilla/5.0'}
OUTPUT_FILE = 'kospi200.xlsx'


class ScrapeWorker(QObject):
    finished = pyqtSignal(list, str)
    progress = pyqtSignal(str)
    error = pyqtSignal(str)

    def run(self):
        try:
            all_rows = []
            for page in range(1, 21):
                soup = self.fetch_page(page)
                rows = self.parse_table_rows(soup)
                all_rows.extend(rows)
                self.progress.emit(f'페이지 {page}: {len(rows)}건 수집')

            self.save_excel(all_rows)
            self.finished.emit(all_rows, OUTPUT_FILE)
        except Exception as exc:
            self.error.emit(str(exc))

    @staticmethod
    def fetch_page(page_num: int):
        url = f'{BASE_URL}&page={page_num}'
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        response.encoding = 'euc-kr'
        return BeautifulSoup(response.text, 'html.parser')

    @staticmethod
    def parse_table_rows(soup: BeautifulSoup):
        table = soup.find('table')
        if table is None:
            raise RuntimeError('편입종목상위 테이블을 찾지 못했습니다.')

        headers = []
        rows = []

        for tr in table.find_all('tr'):
            cells = [td.get_text(' ', strip=True) for td in tr.find_all(['th', 'td'])]
            if not cells or not any(cells):
                continue

            if not headers:
                headers = cells
                continue

            rows.append(dict(zip(headers, cells)))

        return rows

    @staticmethod
    def save_excel(all_rows: list[dict]):
        wb = Workbook()
        ws = wb.active
        ws.title = '코스피200_편입종목상위'

        if all_rows:
            headers = list(all_rows[0].keys())
            ws.append(headers)
            for row in all_rows:
                ws.append([row.get(header, '') for header in headers])

        output_path = Path(OUTPUT_FILE)
        wb.save(output_path)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('코스피200 종목 수집기')
        self.resize(700, 500)

        self.title_label = QLabel('코스피200 편입종목 상위 데이터를 수집합니다.')
        self.start_button = QPushButton('수집 시작')
        self.start_button.clicked.connect(self.start_collection)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 20)
        self.progress_bar.setValue(0)

        self.log_edit = QTextEdit()
        self.log_edit.setReadOnly(True)
        self.log_edit.setPlainText('수집 버튼을 누르면 20페이지까지 데이터를 수집합니다.\n')

        layout = QVBoxLayout(self)
        layout.addWidget(self.title_label)
        layout.addWidget(self.start_button)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.log_edit)

        self.thread = None
        self.worker = None

    def start_collection(self):
        self.start_button.setEnabled(False)
        self.log_edit.clear()
        self.log_edit.append('수집을 시작합니다...')
        self.progress_bar.setValue(0)

        self.thread = QThread(self)
        self.worker = ScrapeWorker()
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.append_log)
        self.worker.finished.connect(self.on_finished)
        self.worker.error.connect(self.on_error)
        self.worker.finished.connect(self.thread.quit)
        self.worker.error.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.error.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def append_log(self, message: str):
        self.log_edit.append(message)
        self.progress_bar.setValue(self.progress_bar.value() + 1)

    def on_finished(self, all_rows: list[dict], output_file: str):
        self.log_edit.append(f'총 {len(all_rows)}건의 종목 데이터를 수집했습니다.')
        self.log_edit.append(f'엑셀 파일 저장 완료: {output_file}')
        self.progress_bar.setValue(20)
        self.start_button.setEnabled(True)

        QMessageBox.information(self, '완료', f'수집이 완료되어 {output_file} 파일로 저장되었습니다.')

    def on_error(self, message: str):
        self.log_edit.append(f'오류: {message}')
        self.start_button.setEnabled(True)
        QMessageBox.critical(self, '오류', message)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
