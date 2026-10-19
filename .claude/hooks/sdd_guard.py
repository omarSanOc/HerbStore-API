"""PreToolUse guard that mirrors the per-agent OpenCode SDD permissions.

Usage: python3 sdd_guard.py <role>. Reads the hook JSON from stdin and exits
with code 2 (blocking the tool call) when the role is not allowed to run it.
"""

import json
import os
import re
import sys
from fnmatch import fnmatch

EDIT_TOOLS = {"Edit", "Write", "NotebookEdit"}

# Paths each role may edit (allow) or must never edit (deny).
EDIT_RULES = {
    "coordinator": {"allow": ["MEMORY.md"]},
    "planner": {"allow": ["specs/*", "MEMORY.md"]},
    "implementer": {"deny": ["docs/constitution.md", "specs/*/spec.md", "specs/*/plan.md"]},
    "reviewer": {"allow": []},
}

# Command prefixes each role may run (allow) or must never run (deny).
SHELL_RULES = {
    "coordinator": {
        "allow": [
            "git status",
            "git diff",
            "uv run ruff format --check",
            "uv run ruff check",
            "uv run pytest",
        ]
    },
    "planner": {"allow": ["git status", "git diff"]},
    "implementer": {"deny": ["git push", "git reset", "git checkout", "rm -rf"]},
    "reviewer": {
        "deny": [
            "git commit",
            "git push",
            "git reset",
            "git checkout",
            "git add",
            "rm ",
            "mv ",
            "uv add",
            "uv remove",
            "uv run alembic",
        ]
    },
}

# Shell chaining, substitution or redirection lets a command escape its prefix.
UNSAFE_SHELL = re.compile(r"[;&|`>]|\$\(")


def block(reason: str) -> None:
    print(f"SDD guard: {reason}", file=sys.stderr)
    sys.exit(2)


def relative_path(path: str) -> str:
    root = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    absolute = os.path.realpath(os.path.join(root, path))
    return os.path.relpath(absolute, os.path.realpath(root))


def check_edit(role: str, path: str) -> None:
    rules = EDIT_RULES[role]
    target = relative_path(path)
    if target.startswith(".."):
        block(f"'{role}' cannot edit files outside the project ({path}).")
    if any(fnmatch(target, pattern) for pattern in rules.get("deny", [])):
        block(f"'{role}' cannot edit {target}.")
    allowed = rules.get("allow")
    if allowed is not None and not any(fnmatch(target, p) for p in allowed):
        block(f"'{role}' may only edit: {', '.join(allowed) or 'nothing'}.")


def check_shell(role: str, command: str) -> None:
    rules = SHELL_RULES[role]
    segments = [s.strip() for s in re.split(r"&&|\|\||;|\|", command) if s.strip()]
    for segment in segments:
        if any(segment.startswith(p) for p in rules.get("deny", [])):
            block(f"'{role}' cannot run: {segment}")
    allowed = rules.get("allow")
    if allowed is None:
        return
    if UNSAFE_SHELL.search(command):
        block(f"'{role}' may only run single commands without chaining.")
    if not any(command.strip().startswith(p) for p in allowed):
        block(f"'{role}' may only run: {', '.join(allowed)}.")


def main() -> None:
    role = sys.argv[1] if len(sys.argv) > 1 else ""
    if role not in EDIT_RULES:
        block(f"unknown role '{role}'.")
    payload = json.load(sys.stdin)
    tool = payload.get("tool_name", "")
    tool_input = payload.get("tool_input") or {}
    if tool in EDIT_TOOLS:
        path = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
        check_edit(role, path)
    elif tool == "Bash":
        check_shell(role, tool_input.get("command", ""))


if __name__ == "__main__":
    main()
