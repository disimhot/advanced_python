from fastapi import Depends, FastAPI
from fastapi_users import FastAPIUsers
from auth.database import User
from auth.schemas import UserCreate, UserRead
from auth.auth import auth_backend  # , current_active_user, fastapi_users
from auth.manager import get_user_manager
import uvicorn

app = FastAPI()

# линкует объект юзера к менеджеру и бэкенду
fastapi_users = FastAPIUsers[User, int](get_user_manager, [auth_backend])

app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

current_user =  fastapi_users.current_user()

@app.get("/protected-route")
def protected_route(user: User = Depends(current_user)):
    return {"message": f"Hello, {user.username}!"}

@app.get("/unprotected-route")
def unprotected_route():
    return {"message": f"Hello, anonymous user!"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", log_level="info")