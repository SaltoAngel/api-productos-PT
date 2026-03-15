# API de Productos

Esta es una API REST para la gestión de productos, construida con FastAPI y SQLModel

## 🚀 Instalación y Ejecución Rápida

Para facilitar la isntalacion, el proyecto se puede poner en marcha con un solo comando:

1. **Clonar el repositorio:**

   ```bash
   git clone https://github.com/SaltoAngel/api-productos-python.git
   cd api-productos-python
   ```

2. **Levantar el entorno completo:**

   ```bash
   docker compose up --build
   ```

   Este comando construye la imagen de la API y levanta la base de datos PostgreSQL automáticamente.

3. **Verificación:**
   La API estará disponible en `http://localhost:8080/docs`

---

## 🛠 Documentación de la API (Endpoints)

### 1. Desactivar producto

**PUT `/products/{id}/deactivate`**
Establece el campo `active` en `false`. Es el método obligatorio para dar de baja un producto.

### 2. Crear un producto

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
  "id": 1,
  "name": "Laptop Pro",
  "price": 1200.5,
  "stock": 10,
  "active": true,
  "createdAt": "2026-03-15T15:15:00.000Z"
}
```

### 3. Listar productos

**GET `/products`**
Permite obtener la lista de productos con soporte para paginación (`offset` y `limit`).

### 4. Obtener un producto por ID

**GET `/products/{id}`**

### 5. Cambiar estado

**PUT `/products/{id}/changeStatus`**
Alterna entre `active: true` y `active: false`.

---

## ⚠️ Manejo de Errores

Si las validaciones fallan o el recurso no se encuentra, la API devuelve:

- **400 Bad Request** o **422 Unprocessable Entity**: Si los datos enviados no cumplen con las validaciones (ej. precio negativo, nombre vacío).
- **404 Not Found**: Si se intenta acceder o modificar un producto que no existe en la base de datos.

---

## ✅ Validaciones

- `name`: No puede estar vacío (mínimo 1 carácter).
- `price`: Debe ser estrictamente superior a 0 (`gt=0`).
- `stock`: Debe ser mayor o igual a 0 (`ge=0`).
- `createdAt`: Campo generado automáticamente al crear el producto.

## ⚙️ Tecnologías

- **FastAPI** & **SQLModel** (Python)
- **PostgreSQL** (Puerto interno 5432)
- **Docker & Docker Compose** (Puerto expuesto 8080)
