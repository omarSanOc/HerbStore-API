# CLAUDE.md — HerbStore API

Claude Code ya carga `AGENTS.md` (instrucciones del proyecto). Este archivo añade la constitución, que debe estar siempre en contexto:

@docs/constitution.md

## SDD en Claude Code

La configuración SDD de OpenCode (`.opencode/`, `.agents/skills/sdd/`) tiene su equivalente en `.claude/`:

- Metodología canónica (compartida): `.agents/skills/sdd/SKILL.md`. No la dupliques; edítala ahí.
- Subagentes: `planner`, `implementer`, `reviewer` en `.claude/agents/`. `coordinator` es de hilo principal: `claude --agent coordinator` o `/sdd <petición>`.
- Comandos: `/sdd`, `/sdd-spec`, `/sdd-clarify`, `/sdd-plan`, `/sdd-tasks`, `/sdd-implement`, `/sdd-validate`, `/sdd-change`, `/sdd-status`, `/sdd-constitution`, `/feature`.
- Los permisos por agente de OpenCode se aplican con el hook `.claude/hooks/sdd_guard.py`.
- Si cambias un agente o comando, actualiza ambas versiones (`.opencode/` y `.claude/`).
