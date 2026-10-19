---
name: sdd-tasks
description: SDD · Divide un plan aprobado en tareas pequeñas y verificables (uso - /sdd-tasks 001-nombre)
argument-hint: <NNN-nombre>
disable-model-invocation: true
context: fork
agent: planner
---
Sigue `.agents/skills/sdd/SKILL.md`. Lee `specs/$ARGUMENTS/spec.md` y `specs/$ARGUMENTS/plan.md`.

Si alguno no está aprobado, está incompleto o no cubre todos los RF, detente.

Genera `specs/$ARGUMENTS/tasks.md`: checkboxes, orden de dependencia, 20–30 minutos por tarea, RF cubiertos y una línea `Hecho cuando:` verificable. Máximo diez tareas; si salen más, propone dividir la spec.

No escribas código. Actualiza `MEMORY.md` al cerrar la fase.
