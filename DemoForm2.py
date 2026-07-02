# DemoForm2.py
# DemoForm2.ui(화면단) + DemoForm2.py(로직단)
# 사용하는 라이브러리들을 선언
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6 import uic
#웹크롤링을 위한 선언
from bs4 import BeautifulSoup
#웹서버에 요청
import urllib.request

#디자인 파일 로딩(이름 변경)
form_class = uic.loadUiType("DemoForm2.ui")[0]

#윈도우 클래스 정의(상속받는 클래스 변경)
class DemoForm(QMainWindow, form_class):
    #초기화메서드
    def __init__(self):
        super().__init__()
        self.setupUi(self)
    #슬롯메서드 추가
    def firstClick(self):
        self.label.setText("첫번째 버튼 클릭")
        
    def secondClick(self):
        self.label.setText("두번째 버튼 클릭!!")

    def thirdClick(self):
        self.label.setText("세번째 버튼 클릭했습니다.")


#진입점 체크
if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo_window = DemoForm()
    demo_window.show()
    sys.exit(app.exec())