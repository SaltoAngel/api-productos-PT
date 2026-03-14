from fastapi import FastAPI, Depends, HTTPException
from database import create_db_and_tables, get_session
from sqlmodel import Session,select
from models import Product

app = FastAPI(title="API de Productos")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

#Seccion "GET"

@app.get("/products/", response_model=list[Product])
def read_products(
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=10, le=100)
):
    products = session.exec(select(Product).offset(offset).limit(limit)).all()
    return products

@app.get("/products/{product_id}", response_model=Product)
def read_product_by_id(product_id: int, session: Session = Depends(get_session)):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product

#Seccion "POST"

@app.post("/products/", response_model=Product)
def create_product(product: Product, session: Session = Depends(get_session)):
    session.add(product)
    session.commit()
    session.refresh(product)
    return product

#Seccion "PATCH"

@app.patch("/products/{product_id}", response_model=Product)
def update_product(product_id: int, product: Product, session: Session = Depends(get_session)):
    existing_product = session.get(Product, product_id)
    if not existing_product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    update_data = product.dict(exclude_unset=True)

    for key, value in update_data.items():
        setattr(existing_product, key, value)
    
    session.add(existing_product)
    session.commit()
    session.refresh(existing_product)

#Seccion "PUT"

@app.put("/products/{product_id}/changeStatus", response_model=Product)
def change_status(product_id: int, session: Session = Depends(get_session)):
    existing_product = session.get(Product, product_id)
    if not existing_product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    if existing_product.active:
        existing_product.active = False
    else:
        existing_product.active = True
    session.add(existing_product)
    session.commit()
    session.refresh(existing_product)
    return existing_product
    