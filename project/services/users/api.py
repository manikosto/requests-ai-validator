import allure
import requests_ai_validator as requests

from project.utils.helper_ai import Helper
from project.config.headers import Headers
from project.services.users.endpoints import Endpoints
from project.services.users.payloads import Payloads
from project.services.users.models.model_user import UserResponseModel

class UsersAPI:

    def __init__(self):
        self.headers = Headers()
        self.endpoints = Endpoints()
        self.payloads = Payloads()
        self.helper = Helper()

    @allure.step("Create user")
    def create_user(self) -> UserResponseModel:
        response = requests.post(
            url=self.endpoints.create_user,
            json=self.payloads.create_user(),
            headers=self.headers.basic,
            ai_validation=True,
            ai_schema=UserResponseModel
        )
        return self.helper._validate_response(
            response=response,
            model=UserResponseModel,
            success=True
        )

