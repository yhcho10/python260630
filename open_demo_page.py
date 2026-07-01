import os
import webbrowser

html_path = os.path.abspath("DemoPage.html")
url = "file://" + html_path.replace("\\", "/")

webbrowser.open(url)
print("브라우저에서 열었습니다:")
print(html_path)
