from uuid import UUID, uuid4

from sqlalchemy.orm import Query
from pydantic import BaseModel, validator


class CashifyResponse(BaseModel):
    """
    Cashify Base Response Class
    """
    pass


class CashifyLazyLoadResponse(BaseModel):
    """
    Cashify Base Response Class
    """
    @validator("*", pre=True)
    def evaluate_lazy_columns(cls, v):
        if isinstance(v, Query):
            return v.all()
        return v

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
