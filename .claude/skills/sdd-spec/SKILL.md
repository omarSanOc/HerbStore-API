---
name: sdd-spec
description: SDD · Entrevista y crea una spec (uso - /sdd-spec 001-nombre idea inicial)
argument-hint: <NNN-nombre> <idea inicial>
disable-model-invocation: true
---
Actúa con el rol y límites del `planner` (`.claude/agents/planner.md`): solo puedes escribir dentro de `specs/` y `MEMORY.md`. Sigue `.agents/skills/sdd/SKILL.md`. No escribas código.

Argumentos: `$ARGUMENTS` — el primer token es la carpeta (`specs/<token>/`); el resto es la idea inicial.

Lee `docs/constitution.md`, `AGENTS.md`, `MEMORY.md` y el comportamiento existente relacionado.

1. Haz preguntas de una en una para resolver ambigüedades de comportamiento, errores, casos límite y fuera de alcance; máximo cinco.
2. Con las respuestas, crea `specs/<carpeta>/spec.md` con la plantilla SDD, RF en EARS y `Estado: borrador`.
3. Mantén la spec en QUÉ y POR QUÉ; no incluyas stack, arquitectura, tablas ni archivos.
4. Actualiza `MEMORY.md` al cerrar la fase.
