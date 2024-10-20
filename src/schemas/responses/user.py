from pydantic import BaseModel


class AddressSchema(BaseModel):
    id: int
    email_address: str
    user_id: int


class UserSchema(BaseModel):
    id: int
    first_name: str | None = ""
    last_name: str | None = ""
    age: int | None = ""
    addresses: list[AddressSchema] | None
