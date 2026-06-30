# 클래스연습.py

#1) 클래스 정의
class person:
    #초기화 메서드
    def __init__(self):
        self.name = "default name"
    def printInfo(self):
        print("my name is {0}".format(self.name))
        
#2)인스턴스 생성
p1 = person()
p2 = person()
p2.name= "전우치"
p1.printInfo()
p2.printInfo()

