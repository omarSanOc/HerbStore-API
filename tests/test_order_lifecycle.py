from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from threading import Barrier

import pytest
from sqlalchemy import select

from app.catalog.models import Product
from app.core.database import SessionLocal, engine
from app.orders.service import order_status, submit_order

ADDRESS = {
    "fullName": "Test Customer",
    "phone": "5512345678",
    "postalCode": "03100",
    "state": "CDMX",
    "city": "Benito Juárez",
    "street": "Fictional Avenue",
    "exteriorNumber": "42",
}


def order_for(product_id: str, quantity: int) -> dict:
    return {
        "items": [{"productId": product_id, "quantity": quantity}],
        "shippingAddress": ADDRESS,
        "currency": "MXN",
    }


def stock_of(product_id: str) -> int:
    with SessionLocal() as session:
        return session.scalar(select(Product.stock).where(Product.id == product_id))


def test_pending_expiration_restores_stock_and_forgets_key():
    product_id = "product-261009-044"
    started = datetime(2026, 10, 18, 12, tzinfo=UTC)
    before = stock_of(product_id)

    with SessionLocal() as session:
        kind, _ = submit_order(
            session,
            "expiring-key",
            order_for(product_id, 2),
            processing_ms=25 * 60 * 60 * 1000,
            active_hours=24,
            now=started,
        )
        session.commit()
    assert kind == "result"
    assert stock_of(product_id) == before - 2

    with SessionLocal() as session:
        kind, _ = order_status(session, "expiring-key", now=started + timedelta(hours=24))
        session.commit()
    assert kind == "expired"
    assert stock_of(product_id) == before

    with SessionLocal() as session:
        kind, _ = order_status(session, "expiring-key", now=started + timedelta(hours=48))
        session.commit()
    assert kind == "not_created"


def test_confirmed_order_keeps_stock_after_tombstone():
    product_id = "product-261009-045"
    started = datetime(2026, 10, 18, 12, tzinfo=UTC)
    before = stock_of(product_id)

    with SessionLocal() as session:
        submit_order(
            session,
            "confirmed-lifecycle-key",
            order_for(product_id, 2),
            processing_ms=1000,
            active_hours=24,
            now=started,
        )
        session.commit()
    with SessionLocal() as session:
        kind, data = order_status(
            session, "confirmed-lifecycle-key", now=started + timedelta(seconds=1)
        )
        session.commit()
    assert kind == "result"
    assert data["response"][1]["status"] == "confirmed"

    with SessionLocal() as session:
        assert (
            order_status(session, "confirmed-lifecycle-key", now=started + timedelta(hours=24))[0]
            == "expired"
        )
        session.commit()
    assert stock_of(product_id) == before - 2


@pytest.mark.skipif(engine.dialect.name != "postgresql", reason="requires PostgreSQL row locks")
def test_concurrent_orders_cannot_oversell():
    product_id = "product-261009-046"
    with SessionLocal.begin() as session:
        product = session.scalar(select(Product).where(Product.id == product_id).with_for_update())
        product.stock = 2

    barrier = Barrier(2)

    def place_order(key: str) -> str:
        with SessionLocal() as session:
            barrier.wait()
            kind, _ = submit_order(
                session,
                key,
                order_for(product_id, 2),
                processing_ms=1000,
                active_hours=24,
            )
            session.commit()
            return kind

    with ThreadPoolExecutor(max_workers=2) as executor:
        outcomes = list(executor.map(place_order, ["concurrent-a", "concurrent-b"]))

    assert sorted(outcomes) == ["out_of_stock", "result"]
    assert stock_of(product_id) == 0
