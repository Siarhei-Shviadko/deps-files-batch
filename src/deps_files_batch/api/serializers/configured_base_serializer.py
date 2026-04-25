from pydantic import BaseModel

__all__ = ["ConfiguredSerializer"]


class ConfiguredSerializer(BaseModel):
    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        smart_union = True
        anystr_strip_whitespace = True
        use_enum_values = True
