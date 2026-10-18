import math
from datetime import UTC, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal
from typing import Any
from uuid import uuid4

from sqlalchemy import select, text
from sqlalchemy.orm import Session, selectinload

from app.catalog.models import Product
from app.core.errors import ApiError
from app.orders.contracts import ValidOrder, fingerprint, key_hash, validate_order
from app.orders.models import Order, OrderAttempt, OrderItem

MXN_PER_USD = Decimal("18")
FREE_SHIPPING_THRESHOLD_MXN = Decimal("800")
SHIPPING_MXN = Decimal("99")
CENT = Decimal("0.01")


def _aware(value: datetime) -> datetime:
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value


def _money(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def _advisory_lock(session: Session, hashed_key: str) -> None:
    if session.bind is not None and session.bind.dialect.name == "postgresql":
        unsigned = int(hashed_key[:16], 16)
        signed = unsigned if unsigned < 2**63 else unsigned - 2**64
        session.execute(text("SELECT pg_advisory_xact_lock(:value)"), {"value": signed})


def _restore_stock(session: Session, order: Order) -> None:
    product_ids = sorted(item.product_id for item in order.items)
    products = {
        item.id: item
        for item in session.scalars(
            select(Product)
            .where(Product.id.in_(product_ids))
            .order_by(Product.id)
            .with_for_update()
        )
    }
    for item in order.items:
        products[item.product_id].stock += item.quantity


def reconcile(session: Session, now: datetime) -> None:
    attempts = list(
        session.scalars(
            select(OrderAttempt)
            .options(selectinload(OrderAttempt.order).selectinload(Order.items))
            .where(OrderAttempt.forget_at <= now)
            .with_for_update()
        )
    )
    # Include attempts that only need confirmation or expiration.
    attempts += list(
        session.scalars(
            select(OrderAttempt)
            .options(selectinload(OrderAttempt.order).selectinload(Order.items))
            .where(OrderAttempt.forget_at > now)
            .where(
                (OrderAttempt.expires_at <= now)
                | ((OrderAttempt.status == "pending") & (OrderAttempt.confirm_at <= now))
            )
            .with_for_update()
        )
    )
    for attempt in attempts:
        order = attempt.order
        confirm_at = _aware(attempt.confirm_at) if attempt.confirm_at is not None else None
        expires_at = _aware(attempt.expires_at)
        forget_at = _aware(attempt.forget_at)
        if (
            attempt.status == "pending"
            and confirm_at is not None
            and confirm_at <= now
            and confirm_at < expires_at
        ):
            attempt.status = "confirmed"
        if now >= expires_at and attempt.status != "expired":
            if attempt.status == "pending" and order is not None:
                _restore_stock(session, order)
            attempt.status = "expired"
            attempt.fingerprint = None
            attempt.confirm_at = None
            attempt.order = None
            attempt.order_id = None
            if order is not None:
                session.delete(order)
        if now >= forget_at:
            session.delete(attempt)
    session.flush()


def _order_json(order: Order) -> dict[str, Any]:
    return {
        "id": order.id,
        "items": [
            {
                "productId": item.product_id,
                "quantity": item.quantity,
                "unitPrice": float(item.unit_price),
                "lineTotal": float(item.line_total),
            }
            for item in order.items
        ],
        "currency": order.currency,
        "subtotal": float(order.subtotal),
        "shipping": float(order.shipping),
        "total": float(order.total),
        "status": "confirmed",
        "createdAt": _aware(order.created_at)
        .astimezone(UTC)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z"),
    }


def _result(
    attempt: OrderAttempt, now: datetime, *, include_key: str | None = None
) -> tuple[int, dict]:
    if attempt.status == "confirmed" and attempt.order is not None:
        return 200, {"status": "confirmed", "order": _order_json(attempt.order)}
    remaining = (
        max(0, (_aware(attempt.confirm_at) - now).total_seconds()) if attempt.confirm_at else 0
    )
    body = {"status": "pending", "retryAfterSeconds": max(1, math.ceil(remaining))}
    if include_key is not None:
        body["key"] = include_key
    return 202, body


def _calculate(
    order: ValidOrder, products: dict[str, Product]
) -> tuple[list[dict], Decimal, Decimal, Decimal]:
    lines = []
    canonical_mxn = Decimal("0")
    for item in sorted(order.items, key=lambda value: value["productId"]):
        product = products[item["productId"]]
        price_mxn = product.price * MXN_PER_USD if product.currency == "USD" else product.price
        canonical_mxn += price_mxn * item["quantity"]
        unit = _money(price_mxn / MXN_PER_USD if order.currency == "USD" else price_mxn)
        lines.append(
            {
                "product_id": product.id,
                "quantity": item["quantity"],
                "unit_price": unit,
                "line_total": _money(unit * item["quantity"]),
            }
        )
    subtotal = _money(sum((line["line_total"] for line in lines), Decimal("0")))
    shipping = (
        Decimal("0")
        if canonical_mxn >= FREE_SHIPPING_THRESHOLD_MXN
        else _money(SHIPPING_MXN / MXN_PER_USD if order.currency == "USD" else SHIPPING_MXN)
    )
    return lines, subtotal, shipping, _money(subtotal + shipping)


def submit_order(
    session: Session,
    raw_key: str | None,
    raw_body: Any,
    *,
    processing_ms: int,
    active_hours: int,
    now: datetime | None = None,
) -> tuple[str, dict[str, Any]]:
    if raw_key is None or not raw_key.strip():
        return "validation", {"Idempotency-Key": "REQUIRED"}
    key = raw_key.strip()
    hashed_key = key_hash(key)
    _advisory_lock(session, hashed_key)
    current = now or datetime.now(UTC)
    reconcile(session, current)
    existing = session.scalar(
        select(OrderAttempt)
        .options(selectinload(OrderAttempt.order).selectinload(Order.items))
        .where(OrderAttempt.key_hash == hashed_key)
        .with_for_update()
    )
    if existing is not None and existing.status == "expired":
        return "expired", {}

    all_products = list(session.scalars(select(Product)))
    try:
        order_request = validate_order(raw_body, all_products)
    except ApiError as error:
        # Validation is an expected result. Commit any lazy reconciliation done above,
        # just as the in-memory mock keeps those state transitions.
        return "validation", error.fields or {}
    request_fingerprint = fingerprint(order_request)
    if existing is not None:
        if existing.fingerprint != request_fingerprint:
            return "conflict", {
                "status": existing.status,
                "links": {"status": f"/orders/status/{key}"},
            }
        return "result", {"response": _result(existing, current, include_key=key)}

    product_ids = sorted(item["productId"] for item in order_request.items)
    locked_products = {
        product.id: product
        for product in session.scalars(
            select(Product)
            .where(Product.id.in_(product_ids))
            .order_by(Product.id)
            .with_for_update()
        )
    }
    if any(
        locked_products[item["productId"]].stock < item["quantity"] for item in order_request.items
    ):
        return "out_of_stock", {}

    for item in order_request.items:
        locked_products[item["productId"]].stock -= item["quantity"]
    lines, subtotal, shipping, total = _calculate(order_request, locked_products)
    order = Order(
        id=str(uuid4()),
        currency=order_request.currency,
        subtotal=subtotal,
        shipping=shipping,
        total=total,
        created_at=current,
        items=[OrderItem(**line) for line in lines],
    )
    active = timedelta(hours=active_hours)
    attempt = OrderAttempt(
        key_hash=hashed_key,
        fingerprint=request_fingerprint,
        status="pending",
        created_at=current,
        confirm_at=current + timedelta(milliseconds=processing_ms),
        expires_at=current + active,
        forget_at=current + active * 2,
        order=order,
    )
    session.add(attempt)
    session.flush()
    return "result", {"response": _result(attempt, current, include_key=key)}


def order_status(
    session: Session, key: str, *, now: datetime | None = None
) -> tuple[str, dict[str, Any]]:
    clean_key = key.strip()
    if not clean_key:
        return "not_created", {}
    hashed_key = key_hash(clean_key)
    _advisory_lock(session, hashed_key)
    current = now or datetime.now(UTC)
    reconcile(session, current)
    attempt = session.scalar(
        select(OrderAttempt)
        .options(selectinload(OrderAttempt.order).selectinload(Order.items))
        .where(OrderAttempt.key_hash == hashed_key)
        .with_for_update()
    )
    if attempt is None:
        return "not_created", {}
    if attempt.status == "expired":
        return "expired", {}
    return "result", {"response": _result(attempt, current)}
