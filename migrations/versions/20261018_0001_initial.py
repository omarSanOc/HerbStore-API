"""Initial HerbStore schema."""

import sqlalchemy as sa
from alembic import op

revision = "20261018_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "products",
        sa.Column("id", sa.String(length=40), primary_key=True),
        sa.Column("position", sa.Integer(), nullable=False, unique=True),
        sa.Column("brand", sa.String(length=100), nullable=False),
        sa.Column("name_en", sa.String(length=160), nullable=False),
        sa.Column("name_es", sa.String(length=160), nullable=False),
        sa.Column("category_id", sa.String(length=50), nullable=False),
        sa.Column("subcategory_id", sa.String(length=50), nullable=False),
        sa.Column("price", sa.Numeric(10, 2), nullable=False),
        sa.Column("list_price", sa.Numeric(10, 2), nullable=True),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("rating", sa.Numeric(2, 1), nullable=False),
        sa.Column("review_count", sa.Integer(), nullable=False),
        sa.Column("sold_last_30_days", sa.Integer(), nullable=False),
        sa.Column("badges", sa.JSON(), nullable=False),
        sa.Column("coupon_text_en", sa.String(length=160), nullable=True),
        sa.Column("coupon_text_es", sa.String(length=160), nullable=True),
        sa.Column("catalog_in_stock", sa.Boolean(), nullable=False),
        sa.Column("stock", sa.Integer(), nullable=False),
        sa.Column("is_own_brand", sa.Boolean(), nullable=False),
        sa.Column("subscribe_and_save", sa.Boolean(), nullable=False),
        sa.Column("images", sa.JSON(), nullable=False),
        sa.Column("serving_size_en", sa.String(length=80), nullable=False),
        sa.Column("serving_size_es", sa.String(length=80), nullable=False),
        sa.Column("servings_per_container", sa.Integer(), nullable=False),
        sa.Column("description_en", sa.Text(), nullable=False),
        sa.Column("description_es", sa.Text(), nullable=False),
        sa.Column("ean13", sa.String(length=13), nullable=False, unique=True),
        sa.CheckConstraint("price >= 0", name="ck_products_price_nonnegative"),
        sa.CheckConstraint("rating >= 0 AND rating <= 5", name="ck_products_rating_range"),
        sa.CheckConstraint("stock >= 0", name="ck_products_stock_nonnegative"),
    )
    op.create_index("ix_products_brand", "products", ["brand"])
    op.create_index("ix_products_category_id", "products", ["category_id"])
    op.create_index("ix_products_subcategory_id", "products", ["subcategory_id"])
    op.create_index("ix_products_ean13", "products", ["ean13"], unique=True)

    op.create_table(
        "orders",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("subtotal", sa.Numeric(10, 2), nullable=False),
        sa.Column("shipping", sa.Numeric(10, 2), nullable=False),
        sa.Column("total", sa.Numeric(10, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("subtotal >= 0", name="ck_orders_subtotal_nonnegative"),
        sa.CheckConstraint("shipping >= 0", name="ck_orders_shipping_nonnegative"),
        sa.CheckConstraint("total >= 0", name="ck_orders_total_nonnegative"),
    )
    op.create_table(
        "order_items",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "order_id",
            sa.String(length=36),
            sa.ForeignKey("orders.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("product_id", sa.String(length=40), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("unit_price", sa.Numeric(10, 2), nullable=False),
        sa.Column("line_total", sa.Numeric(10, 2), nullable=False),
        sa.CheckConstraint(
            "quantity >= 1 AND quantity <= 99", name="ck_order_items_quantity_range"
        ),
    )
    op.create_index("ix_order_items_order_id", "order_items", ["order_id"])
    op.create_table(
        "order_attempts",
        sa.Column("key_hash", sa.String(length=64), primary_key=True),
        sa.Column("fingerprint", sa.String(length=64), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("confirm_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("forget_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "order_id",
            sa.String(length=36),
            sa.ForeignKey("orders.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'confirmed', 'expired')",
            name="ck_order_attempts_status_value",
        ),
    )
    op.create_index("ix_order_attempts_status", "order_attempts", ["status"])
    op.create_index("ix_order_attempts_expires_at", "order_attempts", ["expires_at"])
    op.create_index("ix_order_attempts_forget_at", "order_attempts", ["forget_at"])


def downgrade() -> None:
    op.drop_table("order_attempts")
    op.drop_table("order_items")
    op.drop_table("orders")
    op.drop_table("products")
