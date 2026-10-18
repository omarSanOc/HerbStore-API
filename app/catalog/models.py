from decimal import Decimal

from sqlalchemy import JSON, Boolean, CheckConstraint, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Product(Base):
    __tablename__ = "products"
    __table_args__ = (
        CheckConstraint("price >= 0", name="ck_products_price_nonnegative"),
        CheckConstraint("rating >= 0 AND rating <= 5", name="ck_products_rating_range"),
        CheckConstraint("stock >= 0", name="ck_products_stock_nonnegative"),
    )

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    position: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    brand: Mapped[str] = mapped_column(String(100), index=True)
    name_en: Mapped[str] = mapped_column(String(160))
    name_es: Mapped[str] = mapped_column(String(160))
    category_id: Mapped[str] = mapped_column(String(50), index=True)
    subcategory_id: Mapped[str] = mapped_column(String(50), index=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    list_price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(3))
    rating: Mapped[Decimal] = mapped_column(Numeric(2, 1))
    review_count: Mapped[int] = mapped_column(Integer)
    sold_last_30_days: Mapped[int] = mapped_column(Integer)
    badges: Mapped[list[str]] = mapped_column(JSON)
    coupon_text_en: Mapped[str | None] = mapped_column(String(160), nullable=True)
    coupon_text_es: Mapped[str | None] = mapped_column(String(160), nullable=True)
    catalog_in_stock: Mapped[bool] = mapped_column(Boolean)
    stock: Mapped[int] = mapped_column(Integer)
    is_own_brand: Mapped[bool] = mapped_column(Boolean)
    subscribe_and_save: Mapped[bool] = mapped_column(Boolean)
    images: Mapped[list[str]] = mapped_column(JSON)
    serving_size_en: Mapped[str] = mapped_column(String(80))
    serving_size_es: Mapped[str] = mapped_column(String(80))
    servings_per_container: Mapped[int] = mapped_column(Integer)
    description_en: Mapped[str] = mapped_column(Text)
    description_es: Mapped[str] = mapped_column(Text)
    ean13: Mapped[str] = mapped_column(String(13), unique=True, index=True)
