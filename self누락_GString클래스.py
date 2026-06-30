strName = "Not Class Member"

class DemoString:
    def __init__(self):
        self.strName = "" 
    def set(self, msg):
        self.strName = msg
    def print(self):
        #파이썬은 명시적으로 코딩하는 것이 좋다!
        print(self.strName)

d = DemoString()
d.set("First Message")
d.print()
