#!/usr/bin/env python3
"""Deliver THE THURSDAY GLOBE front page to the output directory.

The entry image sits beside this file as ``entry.png``.  Before it is
delivered the program proves, using only the standard library, that
the bytes form a complete image within the contest limits:

* the file is no larger than 1 MiB,
* a PNG carries the right signature, every chunk's CRC32 matches,
  an IHDR comes first, an IEND closes the file, and the picture is
  at most 1024 by 1024 pixels,
* a JPEG starts with SOI and ends with the EOI marker.

Delivery is atomic: the image is written to a temporary file in the
destination directory, its SHA-256 is compared with the source, and
only then is it renamed to ``entry.png``.
"""

from __future__ import annotations

import hashlib
import os
import struct
import sys
import tempfile
import zlib
from pathlib import Path

MAX_BYTES = 1_048_576
MAX_SIDE = 1024
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
JPEG_SOI = b"\xff\xd8"
JPEG_EOI = b"\xff\xd9"


class EntryError(RuntimeError):
    """Raised when the bundled image fails a validity check."""


def check_png(data: bytes) -> tuple[int, int]:
    """Walk every PNG chunk, verify CRCs, and return (width, height)."""
    if not data.startswith(PNG_SIGNATURE):
        raise EntryError("missing PNG signature")
    pos = len(PNG_SIGNATURE)
    width = height = 0
    seen_iend = False
    seen_idat = False
    first = True
    while pos < len(data):
        if pos + 8 > len(data):
            raise EntryError("truncated chunk header")
        (length,) = struct.unpack(">I", data[pos : pos + 4])
        kind = data[pos + 4 : pos + 8]
        body_start = pos + 8
        body_end = body_start + length
        crc_end = body_end + 4
        if crc_end > len(data):
            raise EntryError(f"truncated {kind!r} chunk")
        body = data[body_start:body_end]
        (stored_crc,) = struct.unpack(">I", data[body_end:crc_end])
        actual_crc = zlib.crc32(kind + body) & 0xFFFFFFFF
        if stored_crc != actual_crc:
            raise EntryError(f"CRC mismatch in {kind.decode('latin1')} chunk")
        if first and kind != b"IHDR":
            raise EntryError("first chunk is not IHDR")
        first = False
        if kind == b"IHDR":
            if length != 13:
                raise EntryError("IHDR length is not 13")
            width, height = struct.unpack(">II", body[:8])
        elif kind == b"IDAT":
            if length == 0:
                raise EntryError("empty IDAT chunk")
            seen_idat = True
        elif kind == b"IEND":
            seen_iend = True
            pos = crc_end
            break
        pos = crc_end
    if not seen_idat:
        raise EntryError("no IDAT chunk: the header describes no image data")
    if not seen_iend:
        raise EntryError("no IEND chunk")
    if pos != len(data):
        raise EntryError("trailing bytes after IEND")
    return width, height


def check_jpeg(data: bytes) -> None:
    """A JPEG is accepted when it opens with SOI and closes with EOI."""
    if not data.startswith(JPEG_SOI):
        raise EntryError("missing JPEG SOI marker")
    if JPEG_EOI not in data[-4096:]:
        raise EntryError("no JPEG EOI marker near end of file")


def validate(data: bytes) -> str:
    """Check size limits and dispatch on the image's real format."""
    if not data:
        raise EntryError("entry image is empty")
    if len(data) > MAX_BYTES:
        raise EntryError(f"entry image is {len(data)} bytes, over {MAX_BYTES}")
    if data.startswith(PNG_SIGNATURE):
        width, height = check_png(data)
        if width > MAX_SIDE or height > MAX_SIDE:
            raise EntryError(f"image is {width}x{height}, over {MAX_SIDE} a side")
        if width == 0 or height == 0:
            raise EntryError("image has a zero dimension")
        return f"PNG {width}x{height}"
    if data.startswith(JPEG_SOI):
        check_jpeg(data)
        return "JPEG"
    raise EntryError("entry image is neither PNG nor JPEG")


def output_directory() -> Path:
    """MAKEFUN_OUTPUT_DIR wins, then /output, then ./output."""
    chosen = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if chosen:
        return Path(chosen)
    system_output = Path("/output")
    if system_output.is_dir() and os.access(system_output, os.W_OK):
        return system_output
    return Path("output")


def deliver(source: Path, destination_dir: Path) -> Path:
    data = source.read_bytes()
    description = validate(data)
    digest = hashlib.sha256(data).hexdigest()
    destination_dir.mkdir(parents=True, exist_ok=True)
    target = destination_dir / "entry.png"
    fd, tmp_name = tempfile.mkstemp(dir=destination_dir, prefix=".entry-")
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        written = Path(tmp_name).read_bytes()
        if hashlib.sha256(written).hexdigest() != digest:
            raise EntryError("written copy does not match source SHA-256")
        os.replace(tmp_name, target)
    except BaseException:
        Path(tmp_name).unlink(missing_ok=True)
        raise
    print(f"delivered {target} ({description}, {len(data)} bytes, sha256 {digest})")
    return target


def main() -> int:
    source = Path(__file__).resolve().parent / "entry.png"
    if not source.is_file():
        print(f"error: {source} not found", file=sys.stderr)
        return 1
    try:
        deliver(source, output_directory())
    except EntryError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
