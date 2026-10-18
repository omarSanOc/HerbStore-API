def test_health_and_home_contract(client):
    assert client.get("/health").json() == {"status": "ok"}

    response = client.get("/home")
    assert response.status_code == 200
    body = response.json()
    assert [section["id"] for section in body["sections"]] == [
        "best_sellers",
        "new",
        "offers",
    ]
    assert sum(category["productCount"] for category in body["categories"]) == 300
    assert all(section["items"] for section in body["sections"])


def test_category_and_brand_counts(client):
    categories = client.get("/categories").json()
    brands = client.get("/brands").json()
    assert sum(item["productCount"] for item in categories) == 300
    assert sum(item["productCount"] for item in brands) == 300
    for category in categories:
        assert (
            sum(item["productCount"] for item in category["subcategories"])
            == category["productCount"]
        )


def test_products_filter_sort_and_paginate(client):
    response = client.get(
        "/products?category=vitamins&minRating=4&inStock=true&sort=rating&page=1&limit=5"
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) <= 5
    assert body["page"] == 1
    assert body["total"] > 0
    assert all(item["categoryId"] == "vitamins" for item in body["items"])
    assert all(item["rating"] >= 4 for item in body["items"])
    assert all(item["inStock"] for item in body["items"])
    assert [item["rating"] for item in body["items"]] == sorted(
        [item["rating"] for item in body["items"]], reverse=True
    )


def test_unknown_facets_and_late_pages_are_valid(client):
    assert client.get("/products?brand=Unknown").json() == {
        "items": [],
        "page": 1,
        "totalPages": 0,
        "total": 0,
    }
    late = client.get("/products?page=99&limit=10").json()
    assert late["items"] == []
    assert late["totalPages"] == 30
    assert late["total"] == 300


def test_detail_and_barcode_have_live_stock(client):
    detail = client.get("/products/product-261009-043")
    assert detail.status_code == 200
    product = detail.json()
    by_barcode = client.get(f"/products/barcode/{product['ean13']}")
    assert by_barcode.json() == product
    assert product["stock"] >= 0
    assert product["inStock"] == (product["stock"] > 0)


def test_catalog_errors_are_safe(client):
    for path in [
        "/products?page=0",
        "/products?limit=51",
        "/products?brand=Known,,Unknown",
        "/products?minRating=NaN",
        "/products?inStock=1",
        "/products?sort=popular",
        "/products?fail=yes",
    ]:
        response = client.get(path)
        assert response.status_code == 400, path
        assert response.json()["error"]["code"] == "INVALID_QUERY"

    assert client.get("/products/barcode/123").json()["error"]["code"] == "INVALID_BARCODE"
    assert (
        client.get("/products/product-does-not-exist").json()["error"]["code"]
        == "PRODUCT_NOT_FOUND"
    )


def test_spanish_changes_human_text_not_shape(client):
    english = client.get("/categories", headers={"Accept-Language": "en"})
    spanish = client.get("/categories", headers={"Accept-Language": "es-MX"})
    assert english.headers["content-language"] == "en"
    assert spanish.headers["content-language"] == "es"
    assert english.json()[0]["name"] == "Vitamins"
    assert spanish.json()[0]["name"] == "Vitaminas"
    assert english.json()[0].keys() == spanish.json()[0].keys()


def test_generated_images_and_cache(client):
    response = client.get("/images/products/product-001-front.png")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert response.content.startswith(b"\x89PNG\r\n\x1a\n")
    cached = client.get(
        "/images/products/product-001-front.png",
        headers={"If-None-Match": response.headers["etag"]},
    )
    assert cached.status_code == 304
    assert client.get("/images/products/unknown.png").status_code == 404


def test_unknown_route_uses_json_envelope(client):
    response = client.get("/private-value")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"
    assert "private-value" not in response.text
