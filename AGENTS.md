# AGENTS.md — HerbStore API

Backend persistente y didáctico para la aplicación móvil HerbStore. Sustituye su servidor mock de Node sin romper las rutas, respuestas JSON ni reglas de checkout que ya consume la app.

## Stack y estructura

- Python 3.12+, FastAPI, Pydantic 2, SQLAlchemy 2, PostgreSQL 17, Alembic, uv, Pytest, Ruff y Docker Compose.
- `app/main.py` compone middleware, routers y el envelope global de errores; `app/catalog/routes.py` y `app/orders/routes.py` son las entradas HTTP.
- `app/catalog/query.py` define el parseo y normalización de filtros; `serializers.py` define el contrato móvil. No dupliques esas reglas en las rutas.
- `app/orders/contracts.py` define validación estricta y fingerprint; `service.py` concentra totales, inventario, locks, idempotencia y ciclo de vida.
- `app/catalog/data/products.json` es el fixture canónico de 300 productos. `scripts/seed.py` solo inserta IDs ausentes: no actualiza filas existentes ni restablece stock.
- Los modelos SQLAlchemy y `migrations/` deben cambiar juntos. Los tests crean tablas con `Base.metadata.create_all`, por lo que no validan por sí solos una migración Alembic.

## Comandos

```bash
uv sync --frozen
docker compose up --build
```

Desarrollo con la API fuera de Docker:

```bash
docker compose up -d database
uv run alembic upgrade head
uv run python -m scripts.seed
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 3001
```

```bash
uv run ruff format --check .
uv run ruff check .
uv run pytest
uv run pytest tests/test_orders.py::test_idempotent_order_flow_and_stock
docker compose build
```

## Convenciones

- Código, identificadores, nombres de archivos y comentarios técnicos en inglés; documentación y explicaciones para el equipo en español. Los textos de API para personas admiten `en` y `es` mediante `Accept-Language`.
- Conserva rutas sin versión, campos JSON en `camelCase`, códigos de error estables y omisión de campos opcionales. Las imágenes son las únicas respuestas no JSON.
- Inglés es el fallback. Cambiar idioma nunca modifica campos, enums, códigos de error ni la forma de la respuesta.
- Usa `Decimal` y redondeo half-up para dinero; `app/orders/service.py` es la referencia.
- `POST /orders` lee JSON crudo deliberadamente para devolver el `400` establecido en vez del `422` predeterminado de FastAPI.

## Reglas de dominio / trampas conocidas

- Home y las listas exponen el `inStock` estático del catálogo; solo el detalle añade `stock` vivo y deriva `inStock`. Esta diferencia es compatibilidad, no un bug.
- Precios y totales son autoritativos del servidor. Nunca aceptes totales enviados por el cliente.
- Conserva el advisory lock por hash de `Idempotency-Key` y los `SELECT ... FOR UPDATE` de productos ordenados; evitan duplicados, deadlocks y sobreventa.
- Las transiciones de orden son perezosas: no hay worker ni timer. Crear/reintentar una orden, consultar su estado y consultar detalle de producto ejecutan reconciliación y deben confirmarla con `commit`.
- Una orden reserva stock mientras está `pending`; confirma tras `ORDER_PROCESSING_MS`. A las 24 h queda un tombstone sin datos —y un pending devuelve stock—; a las 48 h se olvida la clave.
- La dirección se valida y participa en el fingerprint, pero nunca se persiste ni se registra. Solo se guarda el hash de la clave idempotente y del request normalizado.
- `get_settings()` está cacheado y el engine/session factory se crea al importar `app.core.database`: define variables de entorno antes de importar `app`.
- Los tests locales usan `pytest.db`; la prueba de sobreventa se omite salvo que `DATABASE_URL` apunte a PostgreSQL.

## Forma de trabajar

- Planifica antes de cambiar contrato HTTP, esquema de base de datos, concurrencia/idempotencia, fixture canónico o dependencias.
- Haz cambios pequeños y acompaña cada regla de negocio con una prueba enfocada. Si cambia un modelo, incluye y verifica su migración.
- Al terminar, resume comportamiento y archivos modificados, comandos ejecutados y cualquier validación PostgreSQL o móvil pendiente.

## Límites

- ✅ Siempre: preservar compatibilidad con la app móvil, actualizar pruebas y Swagger al cambiar contratos, y mantener modelos/migraciones sincronizados.
- ✅ Siempre: usar una base desechable para pruebas PostgreSQL; los tests siembran y mutan datos, y no limpian una base remota o compartida.
- ⚠️ Pregunta antes: añadir dependencias, crear nuevos módulos de primer nivel, cambiar rutas/status/formato JSON, modificar los 300 productos o ampliar autenticación, pagos o administración.
- ⚠️ Pregunta antes: desplegar, cambiar proveedor/infraestructura o ejecutar migraciones destructivas fuera de una base desechable.
- 🚫 Nunca: guardar o imprimir direcciones, claves idempotentes sin hash, secretos o valores privados recibidos.
- 🚫 Nunca: usar `float` para cálculos monetarios, restablecer stock al repetir el seed, editar una migración ya aplicada en producción ni confirmar `.env`, bases locales, `.venv` o cachés.
- ✅ Siempre: actualizar `MEMORY.md` al terminar cada tarea.

## Verificación

- Ejecuta, en orden: `uv run ruff format --check .`, `uv run ruff check .` y `uv run pytest`.
- Para órdenes, inventario o locks, ejecuta también la suite con `DATABASE_URL` apuntando a una PostgreSQL desechable y migrada; CI hace esto con PostgreSQL 17.
- Para cambios de esquema, prueba upgrade y downgrade Alembic en una base desechable y después ejecuta el seed; no uses el volumen local con datos útiles.
- Si cambia el contrato móvil, compara status, envelope y payload con el comportamiento existente, incluyendo inglés/español, errores y campos opcionales.

## Memoria
- Al empezar, lee `MEMORY.md` para conocer el estado del proyecto y las decisiones tomadas.
- Al terminar una tarea, actualízalo: estado actual, decisiones importantes (con su porqué) y errores a evitar.
- Mantenlo breve (máximo ~50 líneas): resume o elimina lo que ya no aporte.
- Si algo se convierte en una regla permanente, propón moverlo a `AGENTS.md` en lugar de dejarlo en la memoria.
- No guardes nunca datos sensibles (claves, tokens, datos personales).

## Reglas
- Lee `docs/constitution.md` y la spec activa (`specs/NNN-*/`) antes de tocar código.

## Flujo SDD
- Todo cambio observable sigue: spec → clarificación → aprobación → plan/tareas → aprobación → implementación por tarea → validación RF por RF.
- Usa `coordinator` para el flujo completo; `planner` solo escribe specs/planes/tareas, `implementer` ejecuta una tarea con tests primero y `reviewer` nunca modifica archivos.
- Los comandos `/sdd`, `/sdd-spec`, `/sdd-plan`, `/sdd-tasks`, `/sdd-implement`, `/sdd-validate`, `/sdd-change` y `/sdd-status` aplican esas puertas de aprobación.
- `/feature` queda reservado a documentación, configuración o refactors sin cambios de comportamiento, contrato o datos.
- OpenCode usa `.opencode/`; Claude Code usa el equivalente en `.claude/` (ver `CLAUDE.md`). Ambos comparten la metodología `.agents/skills/sdd/SKILL.md`; al cambiar un agente o comando, actualiza las dos versiones.
