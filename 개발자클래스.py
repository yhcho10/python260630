#개발자클래스.py
#Developer 클래스를 정의
class Developer:


    #생성자 메서드 정의
    def __init__(self, name, age, language):
        self.name = name
        self.age = age
        self.language = language

    #개발자 정보 출력 메서드 정의
    def display_info(self):
        print(f"Name: {self.name}, Age: {self.age}, Language: {self.language}") 
        
#인스턴스 생성
dev1 = Developer("Alice", 30, "Python")

#인스턴스 메서드 호출
dev1.display_info()

