---
description: SDD · Registra un requisito nuevo antes de cambiar código
agent: planner
subagent: false
---
Usa la skill `sdd`. Nuevo requisito para `specs/$1/`: $2

No modifiques código.

1. Actualiza primero `specs/$1/spec.md`: RF nuevo o modificado en EARS, casos límite y fuera de alcance.
2. Indica qué partes de `plan.md` y `tasks.md` quedarán obsoletas, pero no las cambies todavía.
3. Muestra el diff de la spec, actualiza `MEMORY.md` y espera aprobación explícita.
