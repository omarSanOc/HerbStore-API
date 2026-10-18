import time

from sqlalchemy import select

from app.catalog.models import Product
from app.core.database import SessionLocal


def test_order_requires_key_and_strict_body(client, valid_order):
    missing_key = client.post("/orders", json=valid_order)
    assert missing_key.status_code == 400
    assert missing_key.json()["fields"] == {"Idempotency-Key": "REQUIRED"}

    invalid = {
        **valid_order,
        "extra": "private-value",
        "shippingAddress": {**valid_order["shippingAddress"], "phone": "private-phone"},
    }
    response = client.post("/orders", headers={"Idempotency-Key": "invalid"}, json=invalid)
    assert response.status_code == 400
    assert response.json()["fields"] == {
        "extra": "ADDITIONAL_PROPERTY",
        "shippingAddress.phone": "INVALID_FORMAT",
    }
    assert "private" not in response.text
    assert client.get("/orders/status/invalid").status_code == 404


def test_idempotent_order_flow_and_stock(client, valid_order):
    before = client.get("/products/product-261009-043").json()["stock"]
    headers = {"Idempotency-Key": "flow-key"}
    first = client.post("/orders", headers=headers, json=valid_order)
    retry = client.post("/orders", headers=headers, json=valid_order)
    assert first.status_code == 202
    assert retry.json()["status"] in {"pending", "confirmed"}
    assert client.get("/products/product-261009-043").json()["stock"] == before - 2

    time.sleep(0.06)
    confirmed = client.get("/orders/status/flow-key")
    assert confirmed.status_code == 200
    assert confirmed.json()["status"] == "confirmed"
    order = confirmed.json()["order"]
    assert order["items"][0]["quantity"] == 2
    assert order["total"] == order["subtotal"] + order["shipping"]
    assert "shippingAddress" not in confirmed.text
    assert "Test Customer" not in confirmed.text


def test_key_reuse_with_different_body_conflicts(client, valid_order):
    headers = {"Idempotency-Key": "conflict-key"}
    assert client.post("/orders", headers=headers, json=valid_order).status_code == 202
    changed = {**valid_order, "currency": "USD"}
    conflict = client.post("/orders", headers=headers, json=changed)
    assert conflict.status_code == 409
    assert conflict.json()["error"]["code"] == "IDEMPOTENCY_KEY_REUSED"
    assert conflict.json()["links"]["status"] == "/orders/status/conflict-key"


def test_out_of_stock_does_not_activate_key(client, valid_order):
    unavailable = {**valid_order, "items": [{"productId": "product-261009-001", "quantity": 1}]}
    response = client.post("/orders", headers={"Idempotency-Key": "stock-key"}, json=unavailable)
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "OUT_OF_STOCK"
    assert client.get("/orders/status/stock-key").status_code == 404


def test_lists_keep_static_stock_after_order(client):
    with SessionLocal() as session:
        product = session.scalar(select(Product).where(Product.id == "product-261009-043"))
        product.stock = 0
        session.commit()
    detail = client.get("/products/product-261009-043").json()
    listed = client.get("/products?limit=50").json()["items"]
    listed_product = next(item for item in listed if item["id"] == "product-261009-043")
    assert detail["stock"] == 0
    assert detail["inStock"] is False
    assert listed_product["inStock"] is True


def test_large_and_malformed_bodies(client):
    large = client.post(
        "/orders",
        headers={"Idempotency-Key": "large", "Content-Type": "application/json"},
        content='{"padding":"' + "x" * (200 * 1024) + '"}',
    )
    assert large.status_code == 413
    assert large.json()["error"]["code"] == "PAYLOAD_TOO_LARGE"

    malformed = client.post(
        "/orders",
        headers={"Idempotency-Key": "bad", "Content-Type": "application/json"},
        content='{"items": [',
    )
    assert malformed.status_code == 400
    assert malformed.json()["fields"] == {"root": "INVALID_FORMAT"}


def test_openapi_and_docs_exist(client):
    schema = client.get("/openapi.json")
    assert schema.status_code == 200
    assert "/products" in schema.json()["paths"]
    assert "/orders" in schema.json()["paths"]
    assert client.get("/docs").status_code == 200
    assert client.get("/redoc").status_code == 200
