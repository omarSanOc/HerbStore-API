---
name: sdd-clarify
description: SDD · Revisa una spec como QA sin modificar archivos (uso - /sdd-clarify 001-nombre)
argument-hint: <NNN-nombre>
context: fork
agent: reviewer
---
Sigue `.agents/skills/sdd/SKILL.md` y revisa `specs/$ARGUMENTS/spec.md` sin modificar archivos.

Lista únicamente:
1. Ambigüedades que impiden verificar requisitos.
2. Contradicciones internas o con el comportamiento móvil existente.
3. Casos límite y errores no cubiertos.
4. Conflictos con `docs/constitution.md` o `AGENTS.md`.
5. RF sin criterio observable.

No propongas soluciones. Emite el veredicto del reviewer.
