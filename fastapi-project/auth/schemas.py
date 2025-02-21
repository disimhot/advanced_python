import datetime
import uuid

from fastapi_users import schemas

#Это для get запроса
class UserRead(schemas.BaseUser[uuid.UUID]):
    id: int
    username: str
    email: str
class UserCreate(schemas.BaseUserCreate):
    id: int
    username: str
    email: str
    password: str

# class UserUpdate(schemas.BaseUserUpdate):
#     first_name: Optional[str]
#     birthdate: Optional[datetime.date]