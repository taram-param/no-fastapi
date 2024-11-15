from pydantic import BaseModel


class ExtendedBaseModel(BaseModel):
    class ConfigDict:
        from_attributes = True
