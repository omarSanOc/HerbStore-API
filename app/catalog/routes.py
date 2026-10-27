import asyncio
import hashlib
import math
import re
from datetime import UTC, datetime
from pathlib import Path

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.catalog.image_files import image_content
from app.catalog.models import Product
from app.catalog.query import (
    is_valid_ean13,
    normalize_text,
    parse_fail,
    parse_product_query,
)
from app.catalog.serializers import product_json
from app.catalog.translations import CATEGORY_NAMES, SUBCATEGORY_NAMES
from app.core.config import get_settings
from app.core.database import get_session
from app.core.errors import ApiError
from app.core.i18n import Language, language_from_request
from app.core.schemas import (
    BrandSchema,
    CategorySchema,
    HealthSchema,
    HomeSchema,
    ProductDetailSchema,
    ProductPageSchema,
)

router = APIRouter()

BANNERS = [
    {
        "id": "daily-wellness",
        "title_en": "Daily wellness essentials",
        "title_es": "Esenciales para el bienestar diario",
        "subtitle_en": "Explore fictional products for everyday routines.",
        "subtitle_es": "Explora productos ficticios para las rutinas diarias.",
        "imageUrl": "/images/banners/daily-wellness.png",
        "categoryId": "vitamins",
    },
    {
        "id": "plant-powered",
        "title_en": "Plant-powered collection",
        "title_es": "Colección de origen vegetal",
        "subtitle_en": "Discover botanical and plant protein formulas.",
        "subtitle_es": "Descubre fórmulas botánicas y proteínas vegetales.",
        "imageUrl": "/images/banners/plant-powered.png",
        "categoryId": "botanicals",
    },
]


async def _catalog_delay_and_failure(request: Request) -> None:
    settings = get_settings()
    if settings.catalog_latency_ms:
        await asyncio.sleep(settings.catalog_latency_ms / 1000)
    if parse_fail(request.query_params):
        raise ApiError(500, "SIMULATED_FAILURE")


def _language(request: Request, response: Response) -> Language:
    language = language_from_request(request)
    response.headers["Content-Language"] = language
    return language


def _all_products(session: Session) -> list[Product]:
    return list(session.scalars(select(Product).order_by(Product.position)))


@router.get("/health", response_model=HealthSchema, summary="Health check / Comprobación de estado")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get(
    "/home",
    response_model=HomeSchema,
    response_model_exclude_none=True,
    summary="Mobile home / Inicio móvil",
)
async def home(
    request: Request, response: Response, session: Session = Depends(get_session)
) -> dict:
    await _catalog_delay_and_failure(request)
    language = _language(request, response)
    products = _all_products(session)
    categories = _category_data(products, language, include_subcategories=False)
    banners = [
        {
            "id": item["id"],
            "title": item[f"title_{language}"],
            "subtitle": item[f"subtitle_{language}"],
            "imageUrl": item["imageUrl"],
            "categoryId": item["categoryId"],
        }
        for item in BANNERS
    ]
    section_titles = {
        "best_sellers": "Más vendidos" if language == "es" else "Best sellers",
        "new": "Nuevos" if language == "es" else "New",
        "offers": "Ofertas" if language == "es" else "Offers",
    }
    sections = [
        (
            "best_sellers",
            sorted(products, key=lambda item: item.sold_last_30_days, reverse=True)[:10],
        ),
        ("new", [item for item in products if "NEW" in item.badges][:10]),
        (
            "offers",
            [item for item in products if item.coupon_text_en or item.list_price is not None][:10],
        ),
    ]
    return {
        "banners": banners,
        "categories": categories,
        "sections": [
            {
                "id": section_id,
                "title": section_titles[section_id],
                "items": [product_json(item, language) for item in items],
            }
            for section_id, items in sections
        ],
    }


def _category_data(
    products: list[Product], language: Language, *, include_subcategories: bool
) -> list[dict]:
    result = []
    for category_id in CATEGORY_NAMES:
        category_products = [item for item in products if item.category_id == category_id]
        category = {
            "id": category_id,
            "name": CATEGORY_NAMES[category_id][1 if language == "es" else 0],
            "productCount": len(category_products),
        }
        if include_subcategories:
            subcategory_ids = list(dict.fromkeys(item.subcategory_id for item in category_products))
            category["subcategories"] = [
                {
                    "id": subcategory_id,
                    "name": SUBCATEGORY_NAMES[subcategory_id][1 if language == "es" else 0],
                    "productCount": sum(
                        item.subcategory_id == subcategory_id for item in category_products
                    ),
                }
                for subcategory_id in subcategory_ids
            ]
        else:
            category["imageUrl"] = f"/images/categories/{category_id}.png"
        result.append(category)
    return result


@router.get("/categories", response_model=list[CategorySchema], summary="Categories / Categorías")
async def categories(
    request: Request, response: Response, session: Session = Depends(get_session)
) -> list[dict]:
    await _catalog_delay_and_failure(request)
    return _category_data(
        _all_products(session), _language(request, response), include_subcategories=True
    )


@router.get("/brands", response_model=list[BrandSchema], summary="Brands / Marcas")
async def brands(
    request: Request, response: Response, session: Session = Depends(get_session)
) -> list[dict]:
    await _catalog_delay_and_failure(request)
    _language(request, response)
    products = _all_products(session)
    names = sorted({item.brand for item in products})
    return [
        {"name": name, "productCount": sum(item.brand == name for item in products)}
        for name in names
    ]


@router.get(
    "/products",
    response_model=ProductPageSchema,
    response_model_exclude_none=True,
    summary="Product list / Lista de productos",
)
async def products(
    request: Request, response: Response, session: Session = Depends(get_session)
) -> dict:
    await _catalog_delay_and_failure(request)
    query = parse_product_query(request.query_params)
    language = _language(request, response)
    selected = _all_products(session)

    def matches(product: Product) -> bool:
        if query.category is not None and normalize_text(product.category_id) != query.category:
            return False
        if query.brands is not None and normalize_text(product.brand) not in query.brands:
            return False
        if (
            query.subcategories is not None
            and normalize_text(product.subcategory_id) not in query.subcategories
        ):
            return False
        if query.min_rating is not None and float(product.rating) < query.min_rating:
            return False
        if query.in_stock is not None and product.catalog_in_stock != query.in_stock:
            return False
        if query.own_brand is not None and product.is_own_brand != query.own_brand:
            return False
        if (
            query.subscribe_and_save is not None
            and product.subscribe_and_save != query.subscribe_and_save
        ):
            return False
        if query.text is not None:
            searchable = normalize_text(
                f"{product.brand} {product.name_en} {product.name_es} "
                f"{product.description_en} {product.description_es}"
            )
            if query.text not in searchable:
                return False
        return True

    selected = [item for item in selected if matches(item)]
    if query.sort == "price_asc":
        selected.sort(key=lambda item: item.price)
    elif query.sort == "price_desc":
        selected.sort(key=lambda item: item.price, reverse=True)
    elif query.sort == "rating":
        selected.sort(key=lambda item: item.rating, reverse=True)
    elif query.sort == "best_selling":
        selected.sort(key=lambda item: item.sold_last_30_days, reverse=True)

    total = len(selected)
    total_pages = math.ceil(total / query.limit) if total else 0
    start = (query.page - 1) * query.limit
    return {
        "items": [product_json(item, language) for item in selected[start : start + query.limit]],
        "page": query.page,
        "totalPages": total_pages,
        "total": total,
    }


async def _product_detail(
    request: Request,
    response: Response,
    session: Session,
    *,
    product_id: str | None = None,
    ean13: str | None = None,
) -> dict:
    await _catalog_delay_and_failure(request)
    # Detail stock is live: observing it also settles due attempts, like the original mock.
    from app.orders.service import reconcile

    reconcile(session, datetime.now(UTC))
    session.commit()
    statement = select(Product)
    statement = (
        statement.where(Product.id == product_id)
        if product_id
        else statement.where(Product.ean13 == ean13)
    )
    product = session.scalar(statement)
    if product is None:
        raise ApiError(404, "PRODUCT_NOT_FOUND")
    return product_json(product, _language(request, response), detail=True)


@router.get(
    "/products/barcode/{code}",
    response_model=ProductDetailSchema,
    response_model_exclude_none=True,
    summary="Product by EAN-13 / Producto por EAN-13",
)
async def product_by_barcode(
    code: str, request: Request, response: Response, session: Session = Depends(get_session)
) -> dict:
    if not is_valid_ean13(code):
        raise ApiError(400, "INVALID_BARCODE")
    return await _product_detail(request, response, session, ean13=code)


@router.get(
    "/products/{product_id}",
    response_model=ProductDetailSchema,
    response_model_exclude_none=True,
    summary="Product detail / Detalle del producto",
)
async def product_detail(
    product_id: str,
    request: Request,
    response: Response,
    session: Session = Depends(get_session),
) -> dict:
    return await _product_detail(request, response, session, product_id=product_id)


IMAGE_SIZES = {"banners": (640, 360), "categories": (128, 128), "products": (256, 256)}
ASSET_ROOT = Path(__file__).parent / "assets"


@router.get("/images/{kind}/{name}", summary="Fictional image / Imagen ficticia")
def image(kind: str, name: str, request: Request) -> Response:
    valid = False
    if kind == "banners":
        valid = name in {f"{item['id']}.png" for item in BANNERS}
    elif kind == "categories":
        valid = name in {f"{item}.png" for item in CATEGORY_NAMES}
    elif kind == "products":
        match = re.fullmatch(r"product-(\d{3})-(front|detail)\.png", name)
        valid = match is not None and 1 <= int(match.group(1)) <= 300
    if kind not in IMAGE_SIZES or not valid:
        raise ApiError(404, "NOT_FOUND")
    content = image_content(ASSET_ROOT / kind / name, IMAGE_SIZES[kind], f"{kind}/{name}")
    etag = f'"{hashlib.sha1(content).hexdigest()}"'
    headers = {
        "Cache-Control": "public, max-age=86400",
        "X-Content-Type-Options": "nosniff",
        "ETag": etag,
    }
    if request.headers.get("if-none-match") == etag:
        return Response(status_code=304, headers=headers)
    return Response(content, media_type="image/png", headers=headers)
