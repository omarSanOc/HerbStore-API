---
description: SDD · Implementa una sola tarea aprobada (uso - /sdd-implement 001-nombre T3)
agent: implementer
subagent: false
---
Implementa únicamente la tarea `$2` de `specs/$1/tasks.md` siguiendo la skill `sdd`, `spec.md`, `plan.md`, `docs/constitution.md` y `AGENTS.md`.

1. Escribe la prueba enfocada y confirma que falla por la razón esperada.
2. Implementa solo el alcance de la tarea hasta ponerla en verde.
3. Ejecuta la prueba enfocada y la verificación completa con Ruff y Pytest.
4. Valida Alembic/PostgreSQL cuando el plan lo exija.
5. Marca solo `$2`, actualiza `MEMORY.md` y muestra RF, archivos y resultados.

Después detente; no empieces otra tarea.
