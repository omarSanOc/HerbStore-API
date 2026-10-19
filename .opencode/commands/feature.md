---
description: Planifica mantenimiento sin cambio observable antes de tocar archivos
agent: plan
subagent: false
---
Quiero realizar este mantenimiento: $ARGUMENTS

Lee `docs/constitution.md`, `AGENTS.md` y `MEMORY.md`. No modifiques archivos.

Este comando solo sirve para documentación, configuración o refactors que no cambian comportamiento, contratos HTTP, datos ni reglas de dominio. Si la petición sí cambia algo observable, detente y recomienda `/sdd` o `/sdd-spec`.

Prepara un plan breve con archivos, cambios, riesgos y verificaciones. Señala cualquier decisión que requiera aprobación.
