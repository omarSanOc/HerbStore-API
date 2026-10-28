# MEMORY.md — Diario de Estudio

## Estado actual

- HerbStore API v0.1: FastAPI, PostgreSQL/Alembic, catálogo persistente de 300 productos, checkout idempotente y API bilingüe compatible con la app móvil.
- Spec 001 — fotografía del catálogo: aprobada e implementada. Entrega completa: 607 PNG revisados (600 de productos, 5 categorías, 2 banners), con manifest, prompts, referencias y hashes.
- Se conservan las URLs y contratos existentes. Los assets se sirven desde `app/catalog/assets/`; los faltantes mantienen placeholder, los nombres inválidos devuelven 404 y ETag/304 funciona por contenido.
- Validación móvil Android/iOS realizada externamente durante la generación: listas, detalle, carrito, caché fría, reinicio/offline, modo oscuro y texto ampliado, con límites documentados.
- Evidencia final: `docs/catalog-photography/validation-full-catalog.md`; estado: `docs/catalog-photography/progress.md`.
- Tareas T1–T8 completas. Reviewer final: APROBADO para RF-1 a RF-6; cierre documental coherente y sin alcance adicional.
- Verificaciones: Ruff format/check PASS; `uv run python -m pytest` 26 passed/1 skipped; verificador local 607/607 PASS.
- Incidencias históricas: `uv run pytest` falló por el entorno y una repetición terminó con código 137; se conserva como evidencia válida `uv run python -m pytest` con 26 passed/1 skipped. Lint y typecheck móviles finalizaron correctamente según confirmación externa del usuario.

## Decisiones permanentes

- La spec aprobada define el alcance; cambios de API, datos, dominio, concurrencia o dependencias vuelven a spec.
- Se mantienen rutas sin versión, campos camelCase, envelopes, status, i18n `en`/`es` y comportamiento histórico de stock.
- Dinero con `Decimal` half-up; precios/totales autoritativos del servidor; dirección no persistida ni registrada; claves idempotentes con hash.
- PostgreSQL es obligatorio para órdenes, stock, locks e idempotencia; SQLite solo ofrece feedback local.
- Seed solo inserta IDs ausentes. Modelos y migraciones Alembic deben cambiar juntos.

## Aprendizajes y próximos pasos

- Definir `DATABASE_URL` antes de importar `app`; settings, engine y sesiones quedan cacheados.
- No sustituir el JSON crudo de `POST /orders`: el contrato requiere `400` en los errores establecidos.
- No probar migraciones ni concurrencia contra bases compartidas.
- Crear el commit de esta entrega y hacer push solo cuando el usuario lo solicite.
