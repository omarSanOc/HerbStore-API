import re
import unicodedata
from dataclasses import dataclass
from typing import Literal

from starlette.datastructures import QueryParams

from app.core.errors import ApiError

ProductSort = Literal["featured", "price_asc", "price_desc", "rating", "best_selling"]
SORTS = {"featured", "price_asc", "price_desc", "rating", "best_selling"}


def normalize_text(value: str) -> str:
    decomposed = unicodedata.normalize("NFD", value)
    without_marks = "".join(char for char in decomposed if unicodedata.category(char) != "Mn")
    return " ".join(without_marks.lower().strip().split())


def _single(params: QueryParams, field: str) -> str | None:
    values = params.getlist(field)
    if not values:
        return None
    if len(values) != 1:
        raise ApiError(400, "INVALID_QUERY")
    return values[0]


def _text(params: QueryParams, field: str) -> str | None:
    value = _single(params, field)
    if value is None:
        return None
    if not value.strip():
        raise ApiError(400, "INVALID_QUERY")
    return normalize_text(value)


def _csv(params: QueryParams, field: str) -> set[str] | None:
    value = _single(params, field)
    if value is None:
        return None
    entries = [entry.strip() for entry in value.split(",")]
    if any(not entry for entry in entries):
        raise ApiError(400, "INVALID_QUERY")
    return {normalize_text(entry) for entry in entries}


def _integer(params: QueryParams, field: str, default: int, minimum: int, maximum: int) -> int:
    value = _single(params, field)
    if value is None:
        return default
    if not re.fullmatch(r"\d+", value):
        raise ApiError(400, "INVALID_QUERY")
    parsed = int(value)
    if parsed < minimum or parsed > maximum:
        raise ApiError(400, "INVALID_QUERY")
    return parsed


def _boolean(params: QueryParams, field: str) -> bool | None:
    value = _single(params, field)
    if value is None:
        return None
    if value not in {"true", "false"}:
        raise ApiError(400, "INVALID_QUERY")
    return value == "true"


@dataclass(frozen=True)
class ProductQuery:
    page: int
    limit: int
    category: str | None
    brands: set[str] | None
    subcategories: set[str] | None
    min_rating: float | None
    in_stock: bool | None
    own_brand: bool | None
    subscribe_and_save: bool | None
    text: str | None
    sort: ProductSort
    fail: bool


def parse_product_query(params: QueryParams) -> ProductQuery:
    rating_value = _single(params, "minRating")
    rating: float | None = None
    if rating_value is not None:
        if not re.fullmatch(r"(?:\d+(?:\.\d+)?|\.\d+)", rating_value):
            raise ApiError(400, "INVALID_QUERY")
        rating = float(rating_value)
        if not 0 <= rating <= 5:
            raise ApiError(400, "INVALID_QUERY")

    sort = _single(params, "sort") or "featured"
    if sort not in SORTS:
        raise ApiError(400, "INVALID_QUERY")

    return ProductQuery(
        page=_integer(params, "page", 1, 1, 2**53 - 1),
        limit=_integer(params, "limit", 20, 1, 50),
        category=_text(params, "category"),
        brands=_csv(params, "brand"),
        subcategories=_csv(params, "subcategory"),
        min_rating=rating,
        in_stock=_boolean(params, "inStock"),
        own_brand=_boolean(params, "ownBrand"),
        subscribe_and_save=_boolean(params, "subscribeAndSave"),
        text=_text(params, "q"),
        sort=sort,  # type: ignore[arg-type]
        fail=_boolean(params, "fail") or False,
    )


def parse_fail(params: QueryParams) -> bool:
    return _boolean(params, "fail") or False


def is_valid_ean13(value: str) -> bool:
    if not re.fullmatch(r"\d{13}", value):
        return False
    total = sum(int(digit) * (1 if index % 2 == 0 else 3) for index, digit in enumerate(value[:12]))
    return int(value[-1]) == (10 - total % 10) % 10
