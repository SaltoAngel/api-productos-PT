from typing import Optional # Permite que un campo sea opcional (puede ser None)
from sqlmodel import Field, SQLModel

# Clase base que define los campos comunes para un producto
# Se usa para validación y reutilización de código
class ProductBase(SQLModel):
    name: str = Field(index=True, min_length=1, max_length=100) # Nombre del producto, indexado para búsquedas rápidas
    price: float = Field(gt=0)    # Precio del producto, debe ser mayor a 0 (greater than)
    stock: int = Field(default=0, ge=0) # Cantidad disponible, mínimo 0 (greater or equal)
    active: bool = Field(default=True)  # Estado de disponibilidad (activo por defecto)

# Clase utilizada para recibir los datos al crear un producto
# Hereda todos los campos de ProductBase
class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    name: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    active: Optional[bool] = None