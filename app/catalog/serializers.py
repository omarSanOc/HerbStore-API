from app.catalog.models import Product
from app.core.i18n import Language


def _number(value):
    return float(value) if value is not None else None


def product_json(product: Product, language: Language, *, detail: bool = False) -> dict:
    data = {
        "id": product.id,
        "brand": product.brand,
        "name": product.name_es if language == "es" else product.name_en,
        "categoryId": product.category_id,
        "subcategoryId": product.subcategory_id,
        "price": _number(product.price),
        "currency": product.currency,
        "rating": _number(product.rating),
        "reviewCount": product.review_count,
        "soldLast30Days": product.sold_last_30_days,
        "badges": product.badges,
        "inStock": product.stock > 0 if detail else product.catalog_in_stock,
        "isOwnBrand": product.is_own_brand,
        "subscribeAndSave": product.subscribe_and_save,
        "images": product.images,
        "servingInfo": {
            "size": product.serving_size_es if language == "es" else product.serving_size_en,
            "servingsPerContainer": product.servings_per_container,
        },
        "description": product.description_es if language == "es" else product.description_en,
        "ean13": product.ean13,
    }
    if product.list_price is not None:
        data["listPrice"] = _number(product.list_price)
    coupon = product.coupon_text_es if language == "es" else product.coupon_text_en
    if coupon is not None:
        data["couponText"] = coupon
    if detail:
        data["stock"] = product.stock
    return data
