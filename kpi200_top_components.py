import requests
from bs4 import BeautifulSoup
from openpyxl import Workbook

BASE_URL = 'https://finance.naver.com/sise/entryJongmok.naver?type=KPI200'
HEADERS = {'User-Agent': 'Mozilla/5.0'}
OUTPUT_FILE = 'kospi200.xlsx'


def fetch_page(page_num: int):
    url = f'{BASE_URL}&page={page_num}'
    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    response.encoding = 'euc-kr'
    return BeautifulSoup(response.text, 'html.parser')


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


all_rows = []
for page in range(1, 21):
    soup = fetch_page(page)
    rows = parse_table_rows(soup)
    all_rows.extend(rows)
    print(f'페이지 {page}: {len(rows)}건 수집')

print(f'총 {len(all_rows)}건의 종목 데이터를 수집했습니다.')
for item in all_rows[:10]:
    print(item)

wb = Workbook()
ws = wb.active
ws.title = '코스피200_편입종목상위'

if all_rows:
    headers = list(all_rows[0].keys())
    ws.append(headers)
    for row in all_rows:
        ws.append([row.get(header, '') for header in headers])

wb.save(OUTPUT_FILE)
print(f'엑셀 파일 저장 완료: {OUTPUT_FILE}')
