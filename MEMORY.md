# MEMORY.md — Diario de Estudio

Memoria del proyecto entre sesiones. Máximo ~50 líneas: resume o elimina lo que ya no aporte.

## Estado actual

- v0.1 funcional: FastAPI sirve Home, categorías, marcas, catálogo paginado/filtrado, detalle por ID/EAN-13, imágenes ficticias y checkout idempotente.
- Catálogo canónico de 300 productos migrado desde el mock de HerbStore; seed idempotente, inventario y órdenes persistentes en PostgreSQL.
- API bilingüe (`en` fallback y `es` por `Accept-Language`), errores JSON estables y Swagger/ReDoc disponibles.
- Dockerfile, Docker Compose, migración Alembic inicial y workflow CI configurados.
- Constitución creada en `docs/constitution.md` con seis principios innegociables para futuras specs.
- Agentes, comandos y skill SDD adaptados a FastAPI/Pytest/PostgreSQL y configurados para OpenCode V2.
- SDD portado a Claude Code (2026-10-18): `CLAUDE.md` importa la constitución; `.claude/agents` (coordinator, planner, implementer, reviewer), 11 comandos en `.claude/skills`, guard `.claude/hooks/sdd_guard.py`.
- Suite local: 18 tests pasan y 1 de concurrencia se omite en SQLite; CI pasó la suite completa con PostgreSQL 17.
- Repositorio publicado en `omarSanOc/HerbStore-API`, rama `main`; incluye constitución y configuración SDD para OpenCode V2.

## Decisiones (y por qué)

- PostgreSQL en producción: órdenes, stock e idempotencia necesitan transacciones, row locks y advisory locks; SQLite queda solo para feedback local rápido.
- Monolito modular (`catalog`, `orders`, `core`): separa responsabilidades sin añadir complejidad de microservicios.
- Compatibilidad estricta con el mock móvil: se conservan rutas sin versión, status HTTP, campos camelCase y envelopes existentes.
- Dinero con `Decimal` y redondeo half-up; precios y totales siempre los calcula el servidor.
- Ciclo de órdenes perezoso: requests de orden/status/detalle reconcilian pending, confirmación, expiración a 24 h y olvido a 48 h sin workers.
- Privacidad: la dirección se valida pero no se persiste ni registra; claves y requests idempotentes se almacenan como hashes.
- Seed solo inserta IDs ausentes para no destruir stock ni operación existente al reiniciar.
- La spec aprobada define el alcance: código, migraciones y tests deben trazarse a ella sin añadir comportamiento extra.
- OpenCode carga siempre la constitución; `coordinator` aplica aprobaciones y delega en planner, implementer y reviewer.
- Claude Code: los subagentes no pueden delegar ni entrevistar al usuario, así que `coordinator` corre como hilo principal (`claude --agent coordinator` o `/sdd`) y los comandos interactivos van inline; permisos por agente vía hook PreToolUse porque el frontmatter solo admite `tools`.

## Aprendizajes y errores a evitar

- Home/listas usan `inStock` estático; el detalle usa stock vivo. Es una compatibilidad deliberada, no corregirla sin cambiar el contrato móvil.
- Definir `DATABASE_URL` y demás variables antes de importar `app`: settings, engine y sesiones quedan cacheados/globales.
- Cambiar modelos exige migración Alembic; `Base.metadata.create_all` en tests puede ocultar una migración rota.
- No reemplazar el JSON crudo de `POST /orders` por validación automática que cambie los errores `400` a `422`.
- No probar migraciones ni pytest PostgreSQL contra bases compartidas: la suite siembra y muta productos, órdenes y stock.

## Próximos pasos

- Iniciar Docker Desktop y validar el arranque completo con `docker compose up --build` y health check.
- Conectar la app móvil al backend y comprobar el flujo catálogo → detalle → carrito → checkout en Android/iOS.
- Aprobar proveedor y costes antes de desplegar; Railway con PostgreSQL administrado es la recomendación inicial.
- Hacer push a `origin/main` del commit con la configuración SDD para Claude Code cuando el usuario lo solicite.
- Abrir una sesión nueva de Claude Code y comprobar `/agents`, los comandos `/sdd-*` y el bloqueo del hook en un subagente.
