import hashlib
import json

import pytest

from app.catalog.png import placeholder_png


def test_catalog_file_replaces_placeholder_and_revalidates(client, monkeypatch, tmp_path):
    from app.catalog import routes

    monkeypatch.setattr(routes, "ASSET_ROOT", tmp_path)
    product_directory = tmp_path / "products"
    product_directory.mkdir()
    asset = product_directory / "product-226-front.png"
    first = placeholder_png(3, 3, "first-test-image")
    asset.write_bytes(first)
    url = "/images/products/product-226-front.png"

    response = client.get(url)
    assert response.status_code == 200
    assert response.content == first
    assert response.headers["content-type"] == "image/png"
    assert response.headers["cache-control"] == "public, max-age=86400"
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["etag"] == f'"{hashlib.sha1(first).hexdigest()}"'
    cached = client.get(url, headers={"If-None-Match": response.headers["etag"]})
    assert cached.status_code == 304
    assert cached.content == b""

    second = placeholder_png(3, 3, "second-test-image")
    asset.write_bytes(second)
    changed = client.get(url, headers={"If-None-Match": response.headers["etag"]})
    assert changed.status_code == 200
    assert changed.content == second
    assert changed.headers["etag"] != response.headers["etag"]


def test_missing_asset_keeps_existing_placeholder(client, monkeypatch, tmp_path):
    from app.catalog import routes

    monkeypatch.setattr(routes, "ASSET_ROOT", tmp_path)
    response = client.get("/images/products/product-300-detail.png")
    assert response.status_code == 200
    assert response.content == placeholder_png(256, 256, "products/product-300-detail.png")


def test_files_cannot_bypass_image_name_validation(client, monkeypatch, tmp_path):
    from app.catalog import routes

    monkeypatch.setattr(routes, "ASSET_ROOT", tmp_path)
    (tmp_path / "products").mkdir()
    (tmp_path / "products" / "unknown.png").write_bytes(b"not-a-public-image")
    for url in (
        "/images/products/unknown.png",
        "/images/products/product-301-front.png",
        "/images/private/product-226-front.png",
        "/images/categories/unknown.png",
        "/images/banners/unknown.png",
    ):
        response = client.get(url)
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "NOT_FOUND"


def test_categories_and_banners_use_packaged_files(client, monkeypatch, tmp_path):
    from app.catalog import routes

    monkeypatch.setattr(routes, "ASSET_ROOT", tmp_path)
    for kind, name in (("categories", "vitamins.png"), ("banners", "plant-powered.png")):
        (tmp_path / kind).mkdir()
        content = placeholder_png(3, 3, kind)
        (tmp_path / kind / name).write_bytes(content)
        assert client.get(f"/images/{kind}/{name}").content == content


def test_artwork_inventory_matches_seeded_home(client, monkeypatch):
    from scripts import verify_catalog_photography as verify

    def local_get(origin, path, headers=None):
        response = client.get(path, headers=headers or {})
        return response.status_code, response.headers, response.content

    monkeypatch.setattr(verify, "get", local_get)
    assets = json.loads(verify.MANIFEST.read_text())["assets"]
    verify.verify_inventory("http://testserver", assets)


def test_artwork_inventory_detects_changed_product_before_generation(client, monkeypatch):
    from scripts import verify_catalog_photography as verify

    def local_get(origin, path, headers=None):
        response = client.get(path, headers=headers or {})
        body = response.json()
        if path == "/home":
            body["sections"][0]["items"][0]["name"] = "Changed product"
        return response.status_code, response.headers, json.dumps(body).encode()

    monkeypatch.setattr(verify, "get", local_get)
    assets = json.loads(verify.MANIFEST.read_text())["assets"]
    with pytest.raises(AssertionError, match="name differs"):
        verify.verify_inventory("http://testserver", assets)


def test_full_inventory_has_one_pair_per_product():
    from scripts import verify_catalog_photography as verify

    manifest = json.loads(verify.MANIFEST.read_text())
    verify.validate_manifest(manifest)
    assert manifest["productCount"] == 300
    assert manifest["assetCount"] == 607
    manifest["assets"][-1]["view"] = "front"
    with pytest.raises(AssertionError, match="Missing image pair"):
        verify.validate_manifest(manifest)


def test_partial_asset_selection_does_not_include_pending_files():
    from scripts import verify_catalog_photography as verify

    reviewed = {"categoryId": "vitamins", "status": "reviewed"}
    pending = {"categoryId": "vitamins", "status": "pending"}
    other = {"categoryId": "minerals", "status": "reviewed"}
    assert verify.select_assets([reviewed, pending, other], "vitamins", True) == [reviewed]
    assert verify.select_assets([reviewed, pending, other], "vitamins", False) == [
        reviewed,
        pending,
    ]
    with pytest.raises(AssertionError, match="No assets selected"):
        verify.select_assets([pending], None, True)
