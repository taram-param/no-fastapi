from pydantic import BaseModel, EmailStr


class CreateAddressSchema(BaseModel):
    email_address: EmailStr


class CreateUserSchema(BaseModel):
    first_name: str
    last_name: str
    age: int
    password: str
    addresses: list[CreateAddressSchema]


class UpdateUserSchema(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    age: int | None = None
    addresses: list[CreateAddressSchema] | None = None
