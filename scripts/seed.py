import json
from importlib.resources import files

from sqlalchemy import select

from app.catalog.models import Product
from app.catalog.translations import (
    SERVING_TRANSLATIONS,
    product_description_es,
    product_name_es,
)
from app.core.database import SessionLocal


def seed() -> int:
    payload = json.loads(
        files("app.catalog.data").joinpath("products.json").read_text(encoding="utf-8")
    )
    created = 0
    with SessionLocal.begin() as session:
        existing = set(session.scalars(select(Product.id)))
        for position, item in enumerate(payload, start=1):
            if item["id"] in existing:
                continue
            serving_size = item["servingInfo"]["size"]
            session.add(
                Product(
                    id=item["id"],
                    position=position,
                    brand=item["brand"],
                    name_en=item["name"],
                    name_es=product_name_es(item["name"]),
                    category_id=item["categoryId"],
                    subcategory_id=item["subcategoryId"],
                    price=item["price"],
                    list_price=item.get("listPrice"),
                    currency=item["currency"],
                    rating=item["rating"],
                    review_count=item["reviewCount"],
                    sold_last_30_days=item["soldLast30Days"],
                    badges=item["badges"],
                    coupon_text_en=item.get("couponText"),
                    coupon_text_es=(
                        "Ahorra un 10 % al finalizar la compra" if item.get("couponText") else None
                    ),
                    catalog_in_stock=item["inStock"],
                    stock=99 if item["inStock"] else 0,
                    is_own_brand=item["isOwnBrand"],
                    subscribe_and_save=item["subscribeAndSave"],
                    images=item["images"],
                    serving_size_en=serving_size,
                    serving_size_es=SERVING_TRANSLATIONS.get(serving_size, serving_size),
                    servings_per_container=item["servingInfo"]["servingsPerContainer"],
                    description_en=item["description"],
                    description_es=product_description_es(item["name"]),
                    ean13=item["ean13"],
                )
            )
            created += 1
    return created


if __name__ == "__main__":
    print(f"Seed complete: {seed()} products created")
