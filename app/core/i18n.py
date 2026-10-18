from typing import Literal

from fastapi import Request

Language = Literal["en", "es"]

MESSAGES: dict[str, dict[Language, str]] = {
    "PRODUCT_NOT_FOUND": {
        "en": "The product was not found.",
        "es": "No se encontró el producto.",
    },
    "INVALID_BARCODE": {
        "en": "The barcode must be a valid EAN-13 value.",
        "es": "El código de barras debe ser un EAN-13 válido.",
    },
    "INVALID_QUERY": {
        "en": "The catalog query is invalid.",
        "es": "La consulta del catálogo no es válida.",
    },
    "SIMULATED_FAILURE": {
        "en": "A simulated catalog failure occurred.",
        "es": "Ocurrió un fallo simulado del catálogo.",
    },
    "VALIDATION_ERROR": {
        "en": "Order request validation failed",
        "es": "La validación de la solicitud de pedido falló",
    },
    "IDEMPOTENCY_KEY_REUSED": {
        "en": "The idempotency key is already associated with another request",
        "es": "La clave de idempotencia ya está asociada con otra solicitud",
    },
    "OUT_OF_STOCK": {
        "en": "One or more products do not have enough stock",
        "es": "Uno o más productos no tienen existencias suficientes",
    },
    "ORDER_NOT_CREATED": {
        "en": "No order attempt exists for this key",
        "es": "No existe un intento de pedido para esta clave",
    },
    "IDEMPOTENCY_KEY_EXPIRED": {
        "en": "The idempotency key has expired",
        "es": "La clave de idempotencia ha caducado",
    },
    "NOT_FOUND": {
        "en": "The requested route was not found.",
        "es": "No se encontró la ruta solicitada.",
    },
    "PAYLOAD_TOO_LARGE": {
        "en": "The request body is too large.",
        "es": "El cuerpo de la solicitud es demasiado grande.",
    },
    "INTERNAL_ERROR": {
        "en": "An unexpected server error occurred.",
        "es": "Ocurrió un error inesperado en el servidor.",
    },
}


def language_from_request(request: Request) -> Language:
    value = request.headers.get("accept-language", "en").lower()
    return "es" if value.startswith("es") else "en"


def message(code: str, language: Language) -> str:
    return MESSAGES[code][language]
