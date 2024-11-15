from app.schemas import ExtendedBaseModel


class AddressSchema(ExtendedBaseModel):
    id: int
    email_address: str
    user_id: int


class UserSchema(ExtendedBaseModel):
    id: int
    first_name: str | None = ""
    last_name: str | None = ""
    age: int | None = ""
    addresses: list[AddressSchema] | None
