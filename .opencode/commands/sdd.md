---
description: SDD · Inicia y coordina el flujo completo de una funcionalidad
agent: coordinator
subagent: false
---
Coordina con la skill `sdd` esta petición para HerbStore API: $ARGUMENTS

Empieza en la fase correcta, delega en `planner`, `reviewer` e `implementer`, y respeta las aprobaciones de spec y plan/tareas. No avances ni implementes nada que el usuario no haya aprobado explícitamente.
