---
name: sdd-plan
description: SDD · Genera el plan técnico de una spec aprobada (uso - /sdd-plan 001-nombre)
argument-hint: <NNN-nombre>
disable-model-invocation: true
context: fork
agent: planner
---
Sigue `.agents/skills/sdd/SKILL.md`. Lee `docs/constitution.md`, `AGENTS.md`, `MEMORY.md` y `specs/$ARGUMENTS/spec.md`.

Si la spec no está aprobada o conserva dudas abiertas, detente.

Genera `specs/$ARGUMENTS/plan.md` con trazabilidad RF y solo la complejidad necesaria: archivos/responsabilidades, flujo HTTP y de datos, lógica aislable, contratos JSON/OpenAPI, persistencia y Alembic, transacciones/concurrencia, errores, privacidad, i18n, pseudocódigo, decisiones/alternativas y estrategia Pytest/Ruff/PostgreSQL.

No escribas código. Actualiza `MEMORY.md` al cerrar la fase.
