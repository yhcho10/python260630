# 파이썬 기본 도구를 불러옵니다.
# io는 화면 출력 내용을 저장하는 도구이고,
# contextlib은 출력이 보이는 방식에 약간 손을 대는 도구입니다.
# unittest는 테스트를 자동으로 확인하는 도구입니다.
import io
import contextlib
import unittest


# Person 클래스는 사람이라는 기본 틀입니다.
# 이 틀에는 사람의 번호(id)와 이름(name)을 넣을 수 있습니다.
class Person:
    # 객체를 만들 때 자동으로 실행되는 만드는 함수입니다.
    # 즉, 사람에게 처음 정보를 주는 역할을 합니다.
    def __init__(self, id, name):
        # self.id는 이 사람만의 번호를 저장하는 상자입니다.
        self.id = id
        # self.name은 이 사람만의 이름을 저장하는 상자입니다.
        self.name = name

    # 사람 정보를 화면에 보여주는 함수입니다.
    # printInfo라고 이름 붙였습니다.
    def printInfo(self):
        # 번호와 이름을 예쁘게 출력합니다.
        print(f"ID: {self.id}, Name: {self.name}")


# Manager 클래스는 Person 클래스를 바탕으로 만든 특별한 사람입니다.
# 사람 기본 정보 외에 직책(title)도 추가로 가집니다.
class Manager(Person):
    # 관리자를 만들 때 번호, 이름, 직책을 받아서 저장합니다.
    def __init__(self, id, name, title):
        # Person 클래스의 만들기 기능을 먼저 실행해서 기본 정보도 넣어줍니다.
        super().__init__(id, name)
        # 이 관리자만의 직책을 저장합니다.
        self.title = title

    # 관리자 정보를 화면에 보여줍니다.
    def printInfo(self):
        # 먼저 Person의 printInfo를 실행해서 기본 정보부터 보여줍니다.
        super().printInfo()
        # 그다음 관리자만의 직책을 추가로 보여줍니다.
        print(f"Title: {self.title}")


# Employee 클래스도 Person 클래스를 바탕으로 만든 특별한 사람입니다.
# 사람 기본 정보 외에 기술(skill)도 추가로 가집니다.
class Employee(Person):
    # 직원을 만들 때 번호, 이름, 기술을 받아서 저장합니다.
    def __init__(self, id, name, skill):
        # Person 클래스의 기본 정보를 먼저 채워 넣습니다.
        super().__init__(id, name)
        # 이 직원만의 기술을 저장합니다.
        self.skill = skill

    # 직원 정보를 화면에 보여줍니다.
    def printInfo(self):
        # 먼저 Person의 기본 정보부터 보여줍니다.
        super().printInfo()
        # 그다음 직원만의 기술을 보여줍니다.
        print(f"Skill: {self.skill}")


# 테스트를 모아 둔 클래스입니다.
# 이 클래스 안의 함수들은 코드가 잘 동작하는지 확인하는 검사기입니다.
class TestPersonClasses(unittest.TestCase):
    # 객체의 printInfo 결과를 문자열로 받아오는 도우미 함수입니다.
    # 화면에 보이는 글을 잡아와서 비교하기 쉽게 만듭니다.
    def capture_output(self, obj):
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            obj.printInfo()
        return buffer.getvalue().strip()

    # Person이 번호와 이름을 잘 기억하는지 확인합니다.
    def test_person_has_id_and_name(self):
        person = Person(1, "Alice")
        self.assertEqual(person.id, 1)
        self.assertEqual(person.name, "Alice")

    # Person의 정보가 올바르게 출력되는지 확인합니다.
    def test_person_print_info_output(self):
        person = Person(1, "Alice")
        output = self.capture_output(person)
        self.assertEqual(output, "ID: 1, Name: Alice")

    # Manager가 Person을 상속받았는지 확인합니다.
    def test_manager_inherits_person(self):
        manager = Manager(2, "Bob", "Team Lead")
        self.assertIsInstance(manager, Person)

    # Manager가 직책 정보를 잘 갖고 있는지 확인합니다.
    def test_manager_has_title(self):
        manager = Manager(2, "Bob", "Team Lead")
        self.assertEqual(manager.title, "Team Lead")

    # Manager의 출력 내용이 올바른지 확인합니다.
    def test_manager_print_info_output(self):
        manager = Manager(2, "Bob", "Team Lead")
        output = self.capture_output(manager)
        self.assertEqual(output, "ID: 2, Name: Bob\nTitle: Team Lead")

    # Employee가 Person을 상속받았는지 확인합니다.
    def test_employee_inherits_person(self):
        employee = Employee(3, "Charlie", "Python")
        self.assertIsInstance(employee, Person)

    # Employee가 기술 정보를 잘 갖고 있는지 확인합니다.
    def test_employee_has_skill(self):
        employee = Employee(3, "Charlie", "Python")
        self.assertEqual(employee.skill, "Python")

    # Employee의 출력 내용이 올바른지 확인합니다.
    def test_employee_print_info_output(self):
        employee = Employee(3, "Charlie", "Python")
        output = self.capture_output(employee)
        self.assertEqual(output, "ID: 3, Name: Charlie\nSkill: Python")

    # 각각의 사람 객체가 서로 다른 정보를 따로 기억하는지 확인합니다.
    def test_person_attributes_are_separate_per_instance(self):
        person1 = Person(1, "Alice")
        person2 = Person(2, "Bob")
        self.assertNotEqual(person1.id, person2.id)
        self.assertNotEqual(person1.name, person2.name)

    # Manager와 Employee가 서로 다른 종류의 객체인지 확인합니다.
    def test_manager_and_employee_are_distinct_subclasses(self):
        manager = Manager(4, "Dana", "Director")
        employee = Employee(5, "Evan", "Java")
        self.assertIsInstance(manager, Manager)
        self.assertIsInstance(employee, Employee)
        self.assertNotIsInstance(manager, Employee)
        self.assertNotIsInstance(employee, Manager)


# 이 파일을 직접 실행하면 테스트를 시작합니다.
if __name__ == "__main__":
    unittest.main()
