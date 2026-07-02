import requests
from bs4 import BeautifulSoup
from openpyxl import Workbook
from urllib.parse import quote

query = "파이썬"
url = f"https://search.naver.com/search.naver?where=news&sm=tab_jum&query={quote(query)}"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

try:
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    results = []
    for a in soup.select("a.news_tit"):
        title = a.get_text(" ", strip=True)
        link = a.get("href", "")
        if title:
            results.append({"title": title, "link": link})
except Exception as e:
    print(f"Crawl failed: {e}")
    results = [{"title": "크롤링 실패", "link": str(e)}]

wb = Workbook()
ws = wb.active
ws.title = "Naver News"
ws.append(["title", "link"])

for item in results[:20]:
    ws.append([item["title"], item["link"]])

output_path = "naver_result.xlsx"
wb.save(output_path)
print(f"Saved {len(results)} results to {output_path}")
