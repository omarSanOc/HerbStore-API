import hashlib
import json
from dataclasses import dataclass
from typing import Any

from app.catalog.models import Product
from app.core.errors import ApiError

ROOT_FIELDS = {"items", "shippingAddress", "currency"}
ITEM_FIELDS = {"productId", "quantity"}
ADDRESS_FIELDS = {
    "fullName",
    "phone",
    "postalCode",
    "state",
    "city",
    "street",
    "exteriorNumber",
    "interiorNumber",
}
REQUIRED_ADDRESS_FIELDS = [
    "fullName",
    "phone",
    "postalCode",
    "state",
    "city",
    "street",
    "exteriorNumber",
]
MINIMUM_LENGTHS = {"fullName": 3, "state": 2, "city": 2, "street": 3}


@dataclass(frozen=True)
class ValidOrder:
    items: list[dict[str, Any]]
    shipping_address: dict[str, str]
    currency: str

    def canonical(self) -> dict[str, Any]:
        return {
            "items": sorted(self.items, key=lambda item: item["productId"]),
            "shippingAddress": self.shipping_address,
            "currency": self.currency,
        }


def _is_object(value: Any) -> bool:
    return isinstance(value, dict)


def validate_order(raw: Any, products: list[Product]) -> ValidOrder:
    if not _is_object(raw):
        raise ApiError(400, "VALIDATION_ERROR", {"root": "INVALID_TYPE"})

    fields: dict[str, str] = {}
    for key in raw:
        if key not in ROOT_FIELDS:
            fields[key] = "ADDITIONAL_PROPERTY"

    product_ids = {product.id for product in products}
    normalized_items: list[dict[str, Any]] = []
    raw_items = raw.get("items")
    if raw_items is None:
        fields["items"] = "REQUIRED"
    elif not isinstance(raw_items, list):
        fields["items"] = "INVALID_TYPE"
    elif not raw_items:
        fields["items"] = "OUT_OF_RANGE"
    else:
        seen: set[str] = set()
        for index, item in enumerate(raw_items):
            prefix = f"items[{index}]"
            if not _is_object(item):
                fields[prefix] = "INVALID_TYPE"
                continue
            for key in item:
                if key not in ITEM_FIELDS:
                    fields[f"{prefix}.{key}"] = "ADDITIONAL_PROPERTY"
            product_id: str | None = None
            raw_id = item.get("productId")
            if raw_id is None:
                fields[f"{prefix}.productId"] = "REQUIRED"
            elif not isinstance(raw_id, str):
                fields[f"{prefix}.productId"] = "INVALID_TYPE"
            else:
                product_id = raw_id.strip()
                if not product_id:
                    fields[f"{prefix}.productId"] = "REQUIRED"
                elif product_id in seen:
                    fields[f"{prefix}.productId"] = "DUPLICATE"
                elif product_id not in product_ids:
                    fields[f"{prefix}.productId"] = "UNKNOWN_PRODUCT"
                seen.add(product_id)
            quantity: int | None = None
            raw_quantity = item.get("quantity")
            if raw_quantity is None:
                fields[f"{prefix}.quantity"] = "REQUIRED"
            elif isinstance(raw_quantity, bool) or not isinstance(raw_quantity, int):
                fields[f"{prefix}.quantity"] = "INVALID_TYPE"
            else:
                quantity = raw_quantity
                if not 1 <= quantity <= 99:
                    fields[f"{prefix}.quantity"] = "OUT_OF_RANGE"
            if product_id is not None and quantity is not None:
                normalized_items.append({"productId": product_id, "quantity": quantity})

    address: dict[str, str] = {}
    raw_address = raw.get("shippingAddress")
    if raw_address is None:
        fields["shippingAddress"] = "REQUIRED"
    elif not _is_object(raw_address):
        fields["shippingAddress"] = "INVALID_TYPE"
    else:
        for key in raw_address:
            if key not in ADDRESS_FIELDS:
                fields[f"shippingAddress.{key}"] = "ADDITIONAL_PROPERTY"
        for field in REQUIRED_ADDRESS_FIELDS:
            path = f"shippingAddress.{field}"
            value = raw_address.get(field)
            if value is None:
                fields[path] = "REQUIRED"
            elif not isinstance(value, str):
                fields[path] = "INVALID_TYPE"
            else:
                text = value.strip()
                address[field] = text
                if not text:
                    fields[path] = "REQUIRED"
                elif field in MINIMUM_LENGTHS and len(text) < MINIMUM_LENGTHS[field]:
                    fields[path] = "TOO_SHORT"
                elif (field == "phone" and (len(text) != 10 or not text.isdigit())) or (
                    field == "postalCode" and (len(text) != 5 or not text.isdigit())
                ):
                    fields[path] = "INVALID_FORMAT"
        interior = raw_address.get("interiorNumber")
        if interior is not None:
            if not isinstance(interior, str):
                fields["shippingAddress.interiorNumber"] = "INVALID_TYPE"
            elif interior.strip():
                address["interiorNumber"] = interior.strip()

    raw_currency = raw.get("currency")
    currency = ""
    if raw_currency is None:
        fields["currency"] = "REQUIRED"
    elif not isinstance(raw_currency, str):
        fields["currency"] = "INVALID_TYPE"
    else:
        currency = raw_currency.strip()
        if currency not in {"MXN", "USD"}:
            fields["currency"] = "INVALID_VALUE"

    if fields:
        raise ApiError(400, "VALIDATION_ERROR", fields)
    return ValidOrder(normalized_items, address, currency)


def fingerprint(order: ValidOrder) -> str:
    serialized = json.dumps(
        order.canonical(), sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )
    return hashlib.sha256(serialized.encode()).hexdigest()


def key_hash(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()
