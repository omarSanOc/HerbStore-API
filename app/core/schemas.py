from typing import Literal

from pydantic import BaseModel, Field


class HealthSchema(BaseModel):
    status: Literal["ok"]


class ServingInfoSchema(BaseModel):
    size: str
    servingsPerContainer: int


class ProductSchema(BaseModel):
    id: str
    brand: str
    name: str
    categoryId: str
    subcategoryId: str
    price: float
    listPrice: float | None = None
    currency: Literal["MXN", "USD"]
    rating: float
    reviewCount: int
    soldLast30Days: int
    badges: list[str]
    couponText: str | None = None
    inStock: bool
    isOwnBrand: bool
    subscribeAndSave: bool
    images: list[str]
    servingInfo: ServingInfoSchema
    description: str
    ean13: str


class ProductDetailSchema(ProductSchema):
    stock: int = Field(ge=0)


class ProductPageSchema(BaseModel):
    items: list[ProductSchema]
    page: int
    totalPages: int
    total: int


class SubcategorySchema(BaseModel):
    id: str
    name: str
    productCount: int


class CategorySchema(BaseModel):
    id: str
    name: str
    productCount: int
    subcategories: list[SubcategorySchema]


class BrandSchema(BaseModel):
    name: str
    productCount: int


class HomeBannerSchema(BaseModel):
    id: str
    title: str
    subtitle: str
    imageUrl: str
    categoryId: str


class HomeCategorySchema(BaseModel):
    id: str
    name: str
    productCount: int
    imageUrl: str


class HomeSectionSchema(BaseModel):
    id: Literal["best_sellers", "new", "offers"]
    title: str
    items: list[ProductSchema]


class HomeSchema(BaseModel):
    banners: list[HomeBannerSchema]
    categories: list[HomeCategorySchema]
    sections: list[HomeSectionSchema]
