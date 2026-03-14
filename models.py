from typing import Optional #permite que un campo sea opcional
from sqlmodel import Field, SQLModel

class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    price: float = Field(gt=0)
    stock: int = Field(default=0, ge=0)
    active: bool = Field(default=True)