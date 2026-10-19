---
name: sdd-implement
description: SDD · Implementa una sola tarea aprobada (uso - /sdd-implement 001-nombre T3)
argument-hint: <NNN-nombre> <Tn>
disable-model-invocation: true
context: fork
agent: implementer
---
Argumentos: `$ARGUMENTS` — el primer token es la carpeta de la spec y el segundo el ID de la tarea.

Implementa únicamente esa tarea de `specs/<carpeta>/tasks.md` siguiendo `.agents/skills/sdd/SKILL.md`, `spec.md`, `plan.md`, `docs/constitution.md` y `AGENTS.md`.

1. Escribe la prueba enfocada y confirma que falla por la razón esperada.
2. Implementa solo el alcance de la tarea hasta ponerla en verde.
3. Ejecuta la prueba enfocada y la verificación completa con Ruff y Pytest.
4. Valida Alembic/PostgreSQL cuando el plan lo exija.
5. Marca solo esa tarea, actualiza `MEMORY.md` y muestra RF, archivos y resultados.

Después detente; no empieces otra tarea.
