import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.main import app
from app.database import get_session
from app.models import Product

# 1. Configuración de la Base de Datos de Prueba (SQLite en memoria)
sqlite_url = "sqlite://"
engine = create_engine(
    sqlite_url,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# 2. Fixture para limpiar la base de datos en cada test
@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)

# 3. Fixture para sobreescribir la dependencia de la base de datos de FastAPI
@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

#Test para crear un producto

def test_create_product(client: TestClient):
    response = client.post(
        "/products",
        json={"name": "Teclado Mecánico", "price": 45.99, "stock": 10}
    )
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == "Teclado Mecánico"
    assert data["id"] is not None

#Test para leer productos con paginación

def test_read_products_pagination(client: TestClient, session: Session):
    # Creamos 3 productos de prueba directamente en la DB
    session.add(Product(name="P1", price=10))
    session.add(Product(name="P2", price=20))
    session.add(Product(name="P3", price=30))
    session.commit()

    # Probamos el límite de la paginación
    response = client.get("/products?limit=2")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 2  # Solo deben venir 2 por el limit

#Test para error de producto no encontrado

def test_error_product_not_found(client: TestClient):
    response = client.get("/products/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Producto no encontrado"

def test_deactivate_product(client: TestClient, session: Session):
    # Creamos un producto
    product = Product(name="Test Product", price=10.0, stock=5, active=True)
    session.add(product)
    session.commit()
    session.refresh(product)
    
    # Desactivamos
    response = client.put(f"/products/{product.id}/deactivate")
    data = response.json()
    
    assert response.status_code == 200
    assert data["active"] is False

def test_change_status_product(client: TestClient, session: Session):
    # Creamos un producto
    product = Product(name="Test Product", price=10.0, stock=5, active=True)
    session.add(product)
    session.commit()
    session.refresh(product)
    
    # Cambiamos estado (debe pasar a False)
    response = client.put(f"/products/{product.id}/changeStatus")
    assert response.json()["active"] is False
    
    # Cambiamos estado otra vez (debe pasar a True)
    response = client.put(f"/products/{product.id}/changeStatus")
    assert response.json()["active"] is True