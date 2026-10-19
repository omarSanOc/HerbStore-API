---
description: SDD · Divide un plan aprobado en tareas pequeñas y verificables
agent: planner
subagent: false
---
Usa la skill `sdd`. Lee `specs/$1/spec.md` y `specs/$1/plan.md`.

Si alguno no está aprobado, está incompleto o no cubre todos los RF, detente.

Genera `specs/$1/tasks.md`: checkboxes, orden de dependencia, 20–30 minutos por tarea, RF cubiertos y una línea `Hecho cuando:` verificable. Máximo diez tareas; si salen más, propone dividir la spec.

No escribas código. Actualiza `MEMORY.md` al cerrar la fase.
