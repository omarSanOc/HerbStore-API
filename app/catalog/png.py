import struct
import zlib
from functools import lru_cache

PNG_SIGNATURE = bytes([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A])


def _hash_string(text: str) -> int:
    value = 0x811C9DC5
    for character in text:
        value ^= ord(character)
        value = (value * 0x01000193) & 0xFFFFFFFF
    return value


def _hsl_to_rgb(hue: float, saturation: float, lightness: float) -> bytes:
    chroma = (1 - abs(2 * lightness - 1)) * saturation
    sector = hue / 60
    secondary = chroma * (1 - abs((sector % 2) - 1))
    values = [
        (chroma, secondary, 0),
        (secondary, chroma, 0),
        (0, chroma, secondary),
        (0, secondary, chroma),
        (secondary, 0, chroma),
        (chroma, 0, secondary),
    ][int(sector) % 6]
    offset = lightness - chroma / 2
    # JavaScript Math.round rounds positive .5 upward; Python's round uses bankers' rounding.
    return bytes(int((channel + offset) * 255 + 0.5) for channel in values)


def _chunk(kind: bytes, data: bytes) -> bytes:
    body = kind + data
    return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body))


@lru_cache(maxsize=700)
def placeholder_png(width: int, height: int, seed: str) -> bytes:
    hue = _hash_string(seed) % 360
    rows = bytearray()
    for row in range(height):
        progress = 0 if height == 1 else row / (height - 1)
        pixel = _hsl_to_rgb(hue, 0.55, 0.74 - 0.34 * progress)
        rows.extend(b"\x00")
        rows.extend(pixel * width)
    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return b"".join(
        [
            PNG_SIGNATURE,
            _chunk(b"IHDR", header),
            _chunk(b"IDAT", zlib.compress(bytes(rows), level=9)),
            _chunk(b"IEND", b""),
        ]
    )
