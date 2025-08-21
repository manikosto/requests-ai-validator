from faker import Faker

faker = Faker()

class Payloads:

    @staticmethod
    def create_user(email=None, password=None, name=None, nickname=None):
        return {
          "email": email or faker.email(),
          "password": password or faker.password(),
          "name": name or faker.name(),
          "nickname": nickname or faker.user_name()
        }

    @staticmethod
    def create_user_with_invalid_email():
        return Payloads.create_user(email="@#$%.ru")

    @staticmethod
    def create_user_with_invalid_password():
        return Payloads.create_user(password="123r")

    @staticmethod
    def create_user_with_invalid_nickname():
        return Payloads.create_user(nickname=" ")
