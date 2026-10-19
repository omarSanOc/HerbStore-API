---
name: sdd
description: Úsala siempre al crear, revisar, planificar, implementar, validar o cambiar docs/constitution.md o cualquier spec de HerbStore API. Con argumentos (`/sdd <petición>`) inicia y coordina el flujo SDD completo.
argument-hint: <petición de funcionalidad>
---
# SDD — HerbStore API

Lee primero la metodología canónica `.agents/skills/sdd/SKILL.md` (compartida con OpenCode) y síguela: puertas de aprobación, plantillas de spec/plan/tareas, implementación y validación.

## Si se invoca con una petición

Petición: $ARGUMENTS

Actúa como el agente `coordinator`: lee `.claude/agents/coordinator.md` y sigue su flujo obligatorio y sus límites (no escribes código ni specs; solo actualizas `MEMORY.md`). Empieza en la fase correcta, delega con la herramienta Agent en `planner`, `reviewer` e `implementer`, y respeta las aprobaciones de spec y plan/tareas. Las preguntas del planner se las haces tú al usuario. No avances ni implementes nada que el usuario no haya aprobado explícitamente.

Si no hay petición, limita tu uso a aplicar la metodología a la tarea en curso.
