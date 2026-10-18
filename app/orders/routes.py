import json

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_session
from app.core.errors import ApiError
from app.core.i18n import language_from_request, message
from app.orders.service import order_status, submit_order

router = APIRouter(prefix="/orders")

ORDER_REQUEST_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["items", "shippingAddress", "currency"],
    "properties": {
        "items": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["productId", "quantity"],
                "properties": {
                    "productId": {"type": "string", "example": "product-261009-043"},
                    "quantity": {"type": "integer", "minimum": 1, "maximum": 99},
                },
            },
        },
        "shippingAddress": {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "fullName",
                "phone",
                "postalCode",
                "state",
                "city",
                "street",
                "exteriorNumber",
            ],
            "properties": {
                "fullName": {"type": "string"},
                "phone": {"type": "string", "pattern": "^[0-9]{10}$"},
                "postalCode": {"type": "string", "pattern": "^[0-9]{5}$"},
                "state": {"type": "string"},
                "city": {"type": "string"},
                "street": {"type": "string"},
                "exteriorNumber": {"type": "string"},
                "interiorNumber": {"type": "string"},
            },
        },
        "currency": {"type": "string", "enum": ["MXN", "USD"]},
    },
}

ORDER_RESPONSES = {
    200: {"description": "Order confirmed / Pedido confirmado"},
    202: {"description": "Order pending / Pedido pendiente"},
    400: {"description": "Strict validation error / Error de validación estricta"},
    409: {"description": "Stock or idempotency conflict / Conflicto de stock o idempotencia"},
    410: {"description": "Idempotency key expired / Clave de idempotencia caducada"},
}


def _error(request: Request, http_status: int, code: str, **extra) -> JSONResponse:
    language = language_from_request(request)
    body = {**extra, "error": {"code": code, "message": message(code, language)}}
    return JSONResponse(body, status_code=http_status, headers={"Content-Language": language})


def _adapt(request: Request, kind: str, data: dict) -> JSONResponse:
    language = language_from_request(request)
    headers = {"Content-Language": language}
    if kind == "result":
        status, body = data["response"]
        return JSONResponse(body, status_code=status, headers=headers)
    if kind == "validation":
        return _error(request, 400, "VALIDATION_ERROR", fields=data)
    if kind == "conflict":
        return _error(request, 409, "IDEMPOTENCY_KEY_REUSED", **data)
    if kind == "out_of_stock":
        return _error(request, 409, "OUT_OF_STOCK")
    if kind == "not_created":
        return _error(request, 404, "ORDER_NOT_CREATED", status="not_created")
    if kind == "expired":
        return _error(request, 410, "IDEMPOTENCY_KEY_EXPIRED", status="expired")
    raise RuntimeError("Unknown order result")


@router.post(
    "",
    summary="Create order / Crear pedido",
    description=(
        "Requires `Idempotency-Key`. Prices and totals are always calculated by the server. / "
        "Requiere `Idempotency-Key`. El servidor siempre calcula precios y totales."
    ),
    responses=ORDER_RESPONSES,
    openapi_extra={
        "requestBody": {
            "required": True,
            "content": {"application/json": {"schema": ORDER_REQUEST_SCHEMA}},
        }
    },
)
async def create_order(request: Request, session: Session = Depends(get_session)) -> JSONResponse:
    try:
        body = await request.json()
    except (json.JSONDecodeError, UnicodeDecodeError):
        return _error(request, 400, "VALIDATION_ERROR", fields={"root": "INVALID_FORMAT"})
    settings = get_settings()
    try:
        kind, data = submit_order(
            session,
            request.headers.get("Idempotency-Key"),
            body,
            processing_ms=settings.order_processing_ms,
            active_hours=settings.order_active_hours,
        )
        session.commit()
    except ApiError:
        session.rollback()
        raise
    except Exception:
        session.rollback()
        raise
    return _adapt(request, kind, data)


@router.get(
    "/status/{key}",
    summary="Order status / Estado del pedido",
    responses=ORDER_RESPONSES,
)
def get_order_status(
    key: str, request: Request, session: Session = Depends(get_session)
) -> JSONResponse:
    try:
        kind, data = order_status(session, key)
        session.commit()
    except Exception:
        session.rollback()
        raise
    return _adapt(request, kind, data)
