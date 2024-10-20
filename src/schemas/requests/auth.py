from pydantic import BaseModel, EmailStr


class RegisterUserSchema(BaseModel):
    email: EmailStr
    password: str
    first_name: str | None = None
    last_name: str | None = None
    age: str | None = None


class LoginUserSchema(BaseModel):
    email: EmailStr
    password: str


class GoogleCode(BaseModel):
    code: str
