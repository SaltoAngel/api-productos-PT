# API de Productos

Esta es una API REST para la gestión de productos, construida con FastAPI y SQLModel.

## Requisitos

- Docker
- Docker Compose

## Instrucciones de Construcción y Ejecución

### 1. Construir la imagen

```bash
docker build -t api-productos .
```

### 2. Levantar la aplicación con Docker Compose

```bash
docker-compose up -d
```

La API estará disponible en `http://localhost:8080`.

## Documentación de la API (Endpoints)

### 1. Crear un producto

**POST `/products`**

**Request Body:**

```json
{
  "name": "Laptop Pro",
  "price": 1200.5,
  "stock": 10,
  "active": true
}
```

**Response (200 OK):**

```json
{
  "name": "Laptop Pro",
  "price": 1200.5,
  "stock": 10,
  "active": true,
  "id": 1,
  "createdAt": "2026-03-15T15:15:00.000Z"
}
```

### 2. Listar productos

**GET `/products`**

**Response (200 OK):**

```json
[
  {
    "id": 1,
    "name": "Laptop Pro",
    "price": 1200.5,
    "stock": 10,
    "active": true,
    "createdAt": "2026-03-15T15:15:00.000Z"
  }
]
```

### 3. Obtener un producto por ID

**GET `/products/{id}`**

### 4. Cambiar estado (Toggle)

**PUT `/products/{id}/changeStatus`**

### 5. Desactivar producto

**PUT `/products/{id}/deactivate`**
Establece el campo `active` en `false`.

## Validaciones

- `price > 0`: No se permiten precios menores o iguales a cero.
- `stock >= 0`: No se permite stock negativo.
- `name`: No puede estar vacío.

## Tecnologías utilizadas

- **FastAPI**: Framwork web moderno y rápido.
- **SQLModel**: Para interactuar con la base de datos PostgreSQL.
- **PostgreSQL**: Base de datos relacional.
- **Docker**: Containerización.
- **GitHub Actions/GHCR**: Para el despliegue automático de la imagen.
