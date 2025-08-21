from pydantic import BaseModel

class UserResponseModel(BaseModel):
    email: str
    name: str
    nickname: str
    avatar_url: str
    uuid: str
