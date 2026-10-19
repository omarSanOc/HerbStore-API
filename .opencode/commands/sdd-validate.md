---
description: SDD · Valida una implementación RF por RF sin corregirla
agent: reviewer
subagent: false
---
Usa la skill `sdd`. Lee `specs/$1/spec.md`, `plan.md`, `tasks.md`, `docs/constitution.md`, `AGENTS.md` y los cambios actuales.

1. Ejecuta Ruff y Pytest.
2. Recorre cada RF e indica test/evidencia y resultado.
3. Valida status, JSON, errores, OpenAPI, campos opcionales e idiomas cuando afecte la interfaz HTTP.
4. Exige PostgreSQL desechable para concurrencia/inventario y upgrade/downgrade Alembic para cambios de esquema.
5. Comprueba criterios de finalización, privacidad, constitución y ausencia de alcance extra.

No corrijas nada. Devuelve el veredicto y hallazgos con archivo:línea y RF/principio.
