from fastapi import FastAPI, Depends, HTTPException, Query
from app.database import create_db_and_tables, get_session
from sqlmodel import Session, select
from app.models import Product
from app.schema import ProductCreate # Se añade ProductCreate para el POST

# Inicialización de la aplicación FastAPI
app = FastAPI(title="API de Productos")

# Evento que se ejecuta al iniciar la aplicación
@app.on_event("startup")
def on_startup():
    # Crea la base de datos y las tablas si no existen
    create_db_and_tables()

# ==========================================
# Seccion "GET" - Lectura de Datos
# ==========================================

# Endpoint para listar productos con paginación
@app.get("/products/", response_model=list[Product])
def read_products(
    session: Session = Depends(get_session),
    offset: int = 0, # Desplazamiento (desde qué registro empezar)
    limit: int = Query(default=10, le=100) # Límite de resultados (máx 100)
):
    # Selecciona todos los productos aplicando el desplazamiento y límite
    products = session.exec(select(Product).offset(offset).limit(limit)).all()
    return products

# Endpoint para obtener un producto específico por su ID
@app.get("/products/{product_id}", response_model=Product)
def read_product_by_id(
    product_id: int, 
    session: Session = Depends(get_session)
):
    # Busca el producto directamente por su llave primaria
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(
            status_code=404, 
            detail="Producto no encontrado"
        )
    return product

# ==========================================
# Seccion "POST" - Creación de Datos
# ==========================================

# Endpoint para crear un nuevo producto
@app.post("/products/", response_model=Product)
def create_product(
    product: ProductCreate, 
    session: Session = Depends(get_session)
):
    # Convertimos el modelo de creación a un modelo de base de datos (Product)
    db_product = Product.from_orm(product)

    session.add(db_product) # Añade el objeto a la sesión
    session.commit()        # Guarda los cambios en la DB
    session.refresh(db_product)
    if db_product.id is None:
        raise HTTPException(
            status_code=500, 
            detail="Error al devolver el resultado, el producto posiblemente se ha creado"
        ) # Refresca el objeto con los datos de la DB (como el ID generado)
    return db_product

# ==========================================
# Seccion "PATCH" - Actualización Parcial
# ==========================================

# Endpoint para actualizar campos específicos de un producto
@app.patch("/products/{product_id}", response_model=Product)
def update_product(
    product_id: int, 
    product: Product, # Aquí se reciben los campos a actualizar
    session: Session = Depends(get_session)
):
    # Buscamos el producto existente
    existing_product = session.get(Product, product_id)
    if not existing_product:
        raise HTTPException(
            status_code=404, 
            detail="Producto no encontrado"
        )
    
    # Obtenemos solo los datos que el usuario envió (excluyendo los no definidos)
    update_data = product.dict(exclude_unset=True)

    # Actualizamos los atributos del producto existente
    for key, value in update_data.items():
        setattr(existing_product, key, value)
    
    session.add(existing_product)
    session.commit()
    session.refresh(existing_product)
    return existing_product

# ==========================================
# Seccion "PUT" - Operaciones Específicas
# ==========================================

# Endpoint para alternar el estado (activo/inactivo) de un producto
@app.put("/products/{product_id}/changeStatus", response_model=Product)
def change_status(
    product_id: int, 
    session: Session = Depends(get_session)
):
    existing_product = session.get(Product, product_id)
    if not existing_product:
        raise HTTPException(
            status_code=404, 
            detail="Producto no encontrado"
        )
    
    # Alternamos el valor booleano de 'active'
    existing_product.active = not existing_product.active
    
    session.add(existing_product)
    session.commit()
    session.refresh(existing_product)
    return existing_product