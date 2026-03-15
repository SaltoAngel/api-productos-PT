from fastapi import FastAPI, Depends, HTTPException, Query
from app.database import create_db_and_tables, get_session
from sqlmodel import Session, select
from app.models import Product
from app.schema import ProductCreate # Se añade ProductCreate para el POST
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        # Si el log tiene datos extra, los incluimos
        if hasattr(record, "extra_info"):
            log_record["metadata"] = record.extra_info
            
        return json.dumps(log_record)

# Configurar el manejador de logs para la consola
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())

logger = logging.getLogger("api-productos")
logger.addHandler(handler)
logger.setLevel(logging.INFO)
# Evitar que los logs se dupliquen si FastAPI tiene su propia config
logger.propagate = False

# Inicialización de la aplicación FastAPI
app = FastAPI(title="API de Productos")

if not app:
    logger.error(
        "Error al inicializar la aplicación", 
        extra={"extra_info": {"app": app}}
    )
    raise HTTPException(
        status_code=500, 
        detail="Error al inicializar la aplicación"
    )
else:
    logger.info(
        "Aplicación inicializada correctamente", 
        extra={"extra_info": {"app": app}}
    )

# Evento que se ejecuta al iniciar la aplicación
@app.on_event("startup")
def on_startup():
    # Crea la base de datos y las tablas si no existen
    create_db_and_tables()
if create_db_and_tables:
    logger.info(
        "Base de datos creada correctamente", 
        extra={"extra_info": {"create_db_and_tables": create_db_and_tables}}
    )
else:
    logger.error(
        "Error al crear la base de datos",  
        extra={"extra_info": {"create_db_and_tables": create_db_and_tables}}
    )
    raise HTTPException(
        status_code=500, 
        detail="Error al crear la base de datos"
    )

# ==========================================
# Seccion "GET" - Lectura de Datos
# ==========================================

# Endpoint para listar productos con paginación
@app.get("/products", response_model=list[Product])
def read_products(
    session: Session = Depends(get_session),
    offset: int = 0, # Desplazamiento (desde qué registro empezar)
    limit: int = Query(default=10, le=100) # Límite de resultados (máx 100)
):
    # Selecciona todos los productos aplicando el desplazamiento y límite
    products = session.exec(select(Product).offset(offset).limit(limit)).all()
    if not products:
        logger.warning(
            "Intento de obtener productos fallido", 
            extra={"extra_info": {"products": products, "reason": "not_found"}}
        )
        raise HTTPException(
            status_code=404, 
            detail="Productos no encontrados"
        )
    logger.info(
        "Productos obtenidos correctamente", 
        extra={"extra_info": {"products": products}}
    )
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
        logger.warning(
            "Intento de obtener producto fallido", 
            extra={"extra_info": {"product_id": product_id, "reason": "not_found"}}
        )
        raise HTTPException(
            status_code=404, 
            detail="Producto no encontrado"
        )
    return product

# ==========================================
# Seccion "POST" - Creación de Datos
# ==========================================

# Endpoint para crear un nuevo producto
@app.post("/products", response_model=Product)
def create_product(
    product: ProductCreate, 
    session: Session = Depends(get_session)
):
    # Convertimos el modelo de creación a un modelo de base de datos (Product)
    db_product = Product.model_validate(product)

    session.add(db_product) # Añade el objeto a la sesión
    session.commit()        # Guarda los cambios en la DB
    logger.info(
        "Producto creado correctamente", 
        extra={"extra_info": {"product_id": db_product.id, "new_data": db_product}}
    )
    session.refresh(db_product)
    if db_product.id is None:
        logger.error(
            "Error al devolver el resultado, el producto posiblemente se ha creado", 
            extra={"extra_info": {"product_id": db_product.id, "new_data": db_product}}
        )
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
        logger.warning(
            "Intento de actualización fallido", 
            extra={"extra_info": {"product_id": product_id, "reason": "not_found"}}
        )
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
    logger.info(
        "Producto actualizado correctamente", 
        extra={"extra_info": {"product_id": product_id, "new_data": existing_product}}
    )
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
        logger.warning(
            "Intento de cambio de estado fallido", 
            extra={"extra_info": {"product_id": product_id, "reason": "not_found"}}
        )
        raise HTTPException(
            status_code=404, 
            detail="Producto no encontrado"
        )
    
    # Alternamos el valor booleano de 'active'
    existing_product.active = not existing_product.active
    
    session.add(existing_product)
    session.commit()
    session.refresh(existing_product)
    # Log de éxito
    logger.info(
        "Estado del producto cambiado correctamente", 
        extra={"extra_info": {"product_id": product_id, "new_status": existing_product.active}}
    )
    return existing_product

# Endpoint para desactivar específicamente un producto (active = False)
@app.put("/products/{product_id}/deactivate", response_model=Product)
def deactivate_product(
    product_id: int, 
    session: Session = Depends(get_session)
):
    existing_product = session.get(Product, product_id)
    if not existing_product:
        logger.warning(
            "Intento de desactivación fallido", 
            extra={"extra_info": {"product_id": product_id, "reason": "not_found"}}
        )
        raise HTTPException(
            status_code=404, 
            detail="Producto no encontrado"
        )
    
    # Desactivamos el producto
    existing_product.active = False
    
    session.add(existing_product)
    session.commit()
    session.refresh(existing_product)
    # Log de éxito
    logger.info(
        "Producto desactivado correctamente", 
        extra={"extra_info": {"product_id": product_id}}
    )
    return existing_product