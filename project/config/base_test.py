# config/base_test.py (или где у тебя BaseTest)
import os

from project.services.users.api import UsersAPI

class BaseTest:

    def setup_method(self):

        self.users_api = UsersAPI()
