from typing import Optional # Permite que un campo sea opcional (puede ser None)
from sqlmodel import Field, SQLModel
from app.schema import ProductBase
from datetime import datetime


# Clase que representa la tabla 'product' en la base de datos
class Product(ProductBase, table=True):
    # La ID es opcional al crear el objeto pero autogenerada por la DB
    id: Optional[int] = Field(default=None, primary_key=True)
    createdAt: datetime = Field(default_factory=datetime.now)