"""Read-only checks for the approved artwork inventory and its existing HTTP URLs."""

import argparse
import hashlib
import json
import struct
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs/catalog-photography/manifest.json"
ASSETS = ROOT / "app/catalog/assets"


def get(origin: str, path: str, headers: dict | None = None):
    request = Request(origin.rstrip("/") + path, headers=headers or {}, method="GET")
    try:
        with urlopen(request, timeout=15) as response:
            return response.status, response.headers, response.read()
    except HTTPError as error:
        return error.code, error.headers, error.read()


def get_json(origin: str, path: str):
    status, headers, content = get(origin, path, {"Accept-Language": "en"})
    assert status == 200, f"{path}: HTTP {status}"
    assert headers.get("Content-Language") == "en", f"{path}: missing English response"
    return json.loads(content)


def verify_inventory(origin: str, assets: list[dict]) -> None:
    home = get_json(origin, "/home")
    actual = {p["id"]: p for section in home["sections"] for p in section["items"]}
    expected = {a["productId"]: a for a in assets if a["kind"] == "products"}
    assert actual.keys() <= expected.keys(), "Home products missing from artwork inventory"
    categories = get_json(origin, "/categories")
    category_assets = {a["categoryId"]: a for a in assets if a["kind"] == "categories"}
    assert {c["id"] for c in categories} == category_assets.keys(), "Category IDs differ"
    assert {c["imageUrl"] for c in home["categories"]} == {
        a["url"] for a in category_assets.values()
    }, "Home category images differ"
    assert {b["imageUrl"] for b in home["banners"]} == {
        a["url"] for a in assets if a["kind"] == "banners"
    }, "Home banner images differ"

    catalog = {}
    page = 1
    while True:
        body = get_json(origin, f"/products?page={page}&limit=50")
        catalog.update({p["id"]: p for p in body["items"]})
        if page >= body["totalPages"]:
            break
        page += 1
    assert expected.keys() <= catalog.keys(), "Artwork product missing from live catalog"
    if len(expected) == 300:
        assert expected.keys() == catalog.keys(), "Full catalog coverage differs"
    for product_id, item in expected.items():
        detail = get_json(origin, f"/products/{product_id}")
        for product in ([actual[product_id]] if product_id in actual else []) + [
            catalog[product_id],
            detail,
        ]:
            for field in ("brand", "name", "categoryId", "description"):
                assert product[field] == item[field], f"{product_id}: {field} differs"
            planned = [a["url"] for a in assets if a.get("productId") == product_id]
            assert product["images"] == planned, f"{product_id}: image URLs differ"
    print(f"PASS live inventory: {len(expected)} products, 5 categories, 2 banners")


def verify_assets(assets: list[dict], origin: str | None) -> None:
    for item in assets:
        path = ASSETS / item["file"]
        assert path.is_file(), f"Missing artwork: {item['file']}"
        content = path.read_bytes()
        assert content.startswith(b"\x89PNG\r\n\x1a\n"), f"Not PNG: {item['file']}"
        width, height = struct.unpack(">II", content[16:24])
        ratio = 16 / 9 if item["kind"] == "banners" else 1
        assert height > 0 and abs(width / height - ratio) < 0.01, (
            f"Wrong aspect ratio: {item['file']} ({width}x{height})"
        )
        assert item["status"] == "reviewed", f"Visual review pending: {item['file']}"
        assert item.get("sha256") == hashlib.sha256(content).hexdigest(), (
            f"Reviewed file changed: {item['file']}"
        )
        if origin:
            status, headers, body = get(origin, item["url"])
            assert status == 200 and body == content, f"HTTP content differs: {item['url']}"
            assert headers.get_content_type() == "image/png"
            assert headers.get("ETag") == f'"{hashlib.sha1(content).hexdigest()}"'
            assert headers.get("Cache-Control") == "public, max-age=86400"
            status, _, body = get(origin, item["url"], {"If-None-Match": headers["ETag"]})
            assert status == 304 and body == b"", f"Revalidation failed: {item['url']}"
    print(f"PASS {len(assets)} reviewed PNG assets" + (" and HTTP URLs" if origin else ""))


def validate_manifest(manifest: dict) -> None:
    assets = manifest["assets"]
    assert len(assets) == manifest["assetCount"], "Asset count differs"
    assert len({a["url"] for a in assets}) == len(assets), "Duplicate URL"
    assert len({a["file"] for a in assets}) == len(assets), "Duplicate file"
    products = {a["productId"] for a in assets if a["kind"] == "products"}
    assert len(products) == manifest["productCount"], "Product count differs"
    for product_id in products:
        pair = [a for a in assets if a.get("productId") == product_id]
        assert len(pair) == 2 and {a["view"] for a in pair} == {"front", "detail"}, (
            f"Missing image pair: {product_id}"
        )
    for a in assets:
        assert a["url"] == "/images/" + a["file"], "File/URL mismatch"


def verify_originals(assets: list[dict]) -> None:
    baseline = json.loads((MANIFEST.parent / "original-manifest.json").read_text())
    indexed = {a["url"]: a for a in assets}
    for original in baseline["assets"]:
        assert indexed.get(original["url"]) == original, "Original inventory entry changed"
        assert (
            hashlib.sha256((ASSETS / original["file"]).read_bytes()).hexdigest()
            == original["sha256"]
        ), "Original artwork changed"


def select_assets(assets: list[dict], category: str | None, reviewed_only: bool) -> list[dict]:
    selected = [a for a in assets if category is None or a.get("categoryId") == category]
    if reviewed_only:
        selected = [a for a in selected if a["status"] == "reviewed"]
    assert selected, "No assets selected"
    return selected


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--origin", help="Running persistent API origin, e.g. http://localhost:3001"
    )
    parser.add_argument("--inventory-only", action="store_true")
    parser.add_argument(
        "--reviewed-only",
        action="store_true",
        help="Verify only reviewed files; never declares full delivery complete",
    )
    parser.add_argument(
        "--category", choices=["vitamins", "minerals", "protein", "botanicals", "wellness"]
    )
    args = parser.parse_args()
    if args.inventory_only and not args.origin:
        parser.error("--inventory-only requires --origin")
    try:
        manifest = json.loads(MANIFEST.read_text())
        assets = manifest["assets"]
        validate_manifest(manifest)
        verify_originals(assets)
        if args.origin:
            verify_inventory(args.origin, assets)
        if not args.inventory_only:
            selected = select_assets(assets, args.category, args.reviewed_only)
            verify_assets(selected, args.origin)
            pending = sum(a["status"] != "reviewed" for a in assets)
            print(f"Coverage: {len(assets) - pending}/{len(assets)} reviewed; {pending} pending")
    except (AssertionError, OSError, ValueError, KeyError) as error:
        print(f"FAIL: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
