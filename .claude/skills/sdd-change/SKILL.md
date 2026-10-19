---
name: sdd-change
description: SDD · Registra un requisito nuevo antes de cambiar código (uso - /sdd-change 001-nombre requisito)
argument-hint: <NNN-nombre> <nuevo requisito>
disable-model-invocation: true
---
Actúa con el rol y límites del `planner` (`.claude/agents/planner.md`): solo puedes escribir dentro de `specs/` y `MEMORY.md`. Sigue `.agents/skills/sdd/SKILL.md`. No modifiques código.

Argumentos: `$ARGUMENTS` — el primer token es la carpeta (`specs/<token>/`); el resto es el nuevo requisito.

1. Actualiza primero `specs/<carpeta>/spec.md`: RF nuevo o modificado en EARS, casos límite y fuera de alcance.
2. Indica qué partes de `plan.md` y `tasks.md` quedarán obsoletas, pero no las cambies todavía.
3. Muestra el diff de la spec, actualiza `MEMORY.md` y espera aprobación explícita.
