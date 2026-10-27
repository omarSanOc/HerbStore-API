from pathlib import Path

from app.catalog.png import placeholder_png


def image_content(asset_path: Path, size: tuple[int, int], seed: str) -> bytes:
    """Read an already validated catalog path; absent artwork retains its placeholder."""
    try:
        return asset_path.read_bytes()
    except FileNotFoundError:
        return placeholder_png(*size, seed)
