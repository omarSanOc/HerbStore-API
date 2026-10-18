from dataclasses import dataclass
from typing import Any


@dataclass
class ApiError(Exception):
    status_code: int
    code: str
    fields: dict[str, str] | None = None
    extra: dict[str, Any] | None = None
