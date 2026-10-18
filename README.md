# HerbStore API

Backend persistente de la aplicación móvil ficticia
[HerbStore](https://github.com/omarSanOc/HerbStore). Sustituye su servidor mock sin cambiar las
rutas ni la estructura JSON que consume la app.

## Tecnologías

- Python 3.12+, FastAPI y Pydantic 2.
- PostgreSQL, SQLAlchemy 2 y Alembic.
- Pytest y Ruff.
- Docker Compose para desarrollo local.

La arquitectura es un **monolito modular**: `catalog` contiene las lecturas del catálogo y
`orders` concentra checkout, inventario e idempotencia. Se evita añadir capas sin una
responsabilidad real.

## Arranque recomendado con Docker

Requiere Docker Desktop (macOS/Windows) o Docker Engine (Linux) en ejecución.

```bash
cp .env.example .env
docker compose up --build
```

El contenedor aplica las migraciones, carga de forma idempotente los 300 productos y escucha en
`http://localhost:3001`.

- Swagger UI: <http://localhost:3001/docs>
- ReDoc: <http://localhost:3001/redoc>
- OpenAPI: <http://localhost:3001/openapi.json>
- Health check: <http://localhost:3001/health>

Para detenerlo sin borrar PostgreSQL:

```bash
docker compose down
```

## Desarrollo sin contenerizar la API

Primero levanta PostgreSQL con `docker compose up -d database`. Después:

```bash
uv sync
cp .env.example .env
uv run alembic upgrade head
uv run python -m scripts.seed
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 3001
```

El seed puede repetirse: solo inserta los productos que aún no existen y nunca restablece el stock
de una tienda que ya está funcionando.

## Direcciones para la aplicación móvil

| Entorno | Origen de la API |
|---|---|
| Android Emulator | `http://10.0.2.2:3001` |
| iOS Simulator | `http://localhost:3001` |
| Dispositivo físico por LAN | `http://<IP-LAN-DEL-EQUIPO>:3001` |
| Android físico por USB | `http://localhost:3001` después de `adb reverse tcp:3001 tcp:3001` |

En un dispositivo físico, el firewall debe permitir el puerto 3001. En la app original se puede
definir `EXPO_PUBLIC_API_ORIGIN` con uno de estos orígenes.

## Contratos disponibles

| Método | Ruta | Propósito |
|---|---|---|
| GET | `/health` | Estado del servidor |
| GET | `/home` | Banners, categorías y secciones de Home |
| GET | `/categories` | Árbol de categorías y subcategorías |
| GET | `/brands` | Marcas y conteos |
| GET | `/products` | Búsqueda, filtros, ordenación y paginación |
| GET | `/products/{id}` | Detalle y stock vivo |
| GET | `/products/barcode/{code}` | Detalle por EAN-13 |
| GET | `/images/{kind}/{name}` | PNG ficticio y determinista |
| POST | `/orders` | Crea o reintenta un pedido idempotente |
| GET | `/orders/status/{key}` | Consulta el intento de pedido |

`GET /products` acepta `page`, `limit`, `category`, `brand`, `subcategory`, `minRating`,
`inStock`, `ownBrand`, `subscribeAndSave`, `q` y `sort`. Los valores de `sort` son `featured`,
`price_asc`, `price_desc`, `rating` y `best_selling`.

Las listas conservan el indicador estático `inStock` del catálogo para ser compatibles con el
mock. Los dos endpoints de detalle añaden `stock` vivo y calculan `inStock` a partir de él.

## Idiomas

Los textos destinados a personas se seleccionan con el encabezado `Accept-Language`:

```bash
curl -H 'Accept-Language: es' http://localhost:3001/categories
curl -H 'Accept-Language: en' http://localhost:3001/categories
```

Se admite `es` y `en`; inglés es el fallback. Los campos, enums y códigos de error no cambian con
el idioma. La respuesta indica el idioma efectivo mediante `Content-Language`.

## Crear una orden

```bash
curl -i http://localhost:3001/orders \
  -X POST \
  -H 'Content-Type: application/json' \
  -H 'Idempotency-Key: 8ee881d1-0cf8-4ae4-a85c-d212d3b55d7a' \
  -d '{
    "items": [{"productId": "product-261009-043", "quantity": 1}],
    "shippingAddress": {
      "fullName": "Test Customer",
      "phone": "5512345678",
      "postalCode": "03100",
      "state": "CDMX",
      "city": "Benito Juárez",
      "street": "Fictional Avenue",
      "exteriorNumber": "42"
    },
    "currency": "MXN"
  }'
```

El cliente debe conservar la misma clave durante todos los reintentos del mismo checkout. El
servidor calcula precios, reserva stock dentro de una transacción y no persiste la dirección. Solo
guarda hashes SHA-256 de la clave y del request normalizado.

Una orden comienza como `pending`, normalmente pasa a `confirmed` después de un segundo y puede
consultarse con `/orders/status/{key}`. La asociación permanece activa 24 horas, conserva un
tombstone sin datos del pedido hasta las 48 horas y después se elimina.

## Errores JSON

```json
{
  "error": {
    "code": "PRODUCT_NOT_FOUND",
    "message": "The product was not found."
  }
}
```

Los errores de validación agregan `fields`, con rutas y códigos estables, pero nunca repiten los
valores privados recibidos.

## Calidad

```bash
uv run ruff format --check .
uv run ruff check .
uv run pytest
```

Las pruebas locales usan una base SQLite efímera para ser rápidas. El workflow
`.github/workflows/ci.yml` ejecuta las mismas pruebas sobre PostgreSQL 17, donde también se validan
los bloqueos de filas y el advisory lock de cada clave idempotente.

## Despliegue

El `Dockerfile` sirve para Railway, Render, Fly.io o un VPS. Para una primera demo se recomienda
Railway con PostgreSQL administrado. Antes de publicar:

1. Configura `DATABASE_URL` como secreto del proveedor.
2. Ejecuta `alembic upgrade head` y `python -m scripts.seed` como comando previo al arranque.
3. Publica únicamente mediante HTTPS.
4. Configura copias de seguridad y monitorización de PostgreSQL.
5. No incrustes credenciales de servidor en la aplicación móvil.

Los precios y planes de los proveedores cambian; revísalos antes de aprobar el despliegue. Este
repositorio no realiza ningún despliegue automáticamente.

## Límites intencionados

- No hay cuentas, autenticación ni panel web.
- No hay pagos reales ni datos comerciales reales.
- No se almacenan direcciones de envío.
- Las imágenes se generan como placeholders sin marcas.
