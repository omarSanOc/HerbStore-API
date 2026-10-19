---
description: SDD · Entrevista y crea una spec (uso - /sdd-spec 001-nombre idea inicial)
agent: planner
subagent: false
---
Usa la skill `sdd`. No escribas código.

Carpeta: `specs/$1/`
Idea inicial: $2

Lee `docs/constitution.md`, `AGENTS.md`, `MEMORY.md` y el comportamiento existente relacionado.

1. Haz preguntas de una en una para resolver ambigüedades de comportamiento, errores, casos límite y fuera de alcance; máximo cinco.
2. Con las respuestas, crea `specs/$1/spec.md` con la plantilla SDD, RF en EARS y `Estado: borrador`.
3. Mantén la spec en QUÉ y POR QUÉ; no incluyas stack, arquitectura, tablas ni archivos.
4. Actualiza `MEMORY.md` al cerrar la fase.
