"""Download and parse Brendan McKay's Hadamard equivalence-class corpus."""

from __future__ import annotations

import hashlib
import json
import urllib.request
from pathlib import Path

import numpy as np

from .matrices import SignMatrix, normalize_hadamard

BASE_URL = "https://users.cecs.anu.edu.au/~bdm/data/hadamard"
SUPPORTED_ORDERS = (4, 8, 12, 16, 20, 24, 28)
EXPECTED_CLASS_COUNTS = {
    4: 1,
    8: 1,
    12: 1,
    16: 5,
    20: 3,
    24: 60,
    28: 487,
}


def corpus_url(order: int) -> str:
    if order not in SUPPORTED_ORDERS:
        raise ValueError(f"unsupported corpus order {order}; choose from {SUPPORTED_ORDERS}")
    return f"{BASE_URL}/had{order}.txt"


def parse_hex_matrix(line: str, order: int) -> SignMatrix:
    """Decode one whitespace-separated hexadecimal Hadamard representative."""

    tokens = line.split()
    if len(tokens) != order:
        raise ValueError(f"expected {order} hexadecimal rows, found {len(tokens)}")

    matrix = np.empty((order, order), dtype=np.int64)
    limit = 1 << order
    for row_index, token in enumerate(tokens):
        value = int(token, 16)
        if not 0 <= value < limit:
            raise ValueError(f"hexadecimal row {token!r} does not fit order {order}")
        for column_index in range(order):
            bit = (value >> (order - column_index - 1)) & 1
            matrix[row_index, column_index] = 1 if bit else -1
    return normalize_hadamard(matrix)


def load_corpus_file(path: Path, order: int) -> list[SignMatrix]:
    lines = [line.strip() for line in path.read_text(encoding="ascii").splitlines() if line.strip()]
    matrices = [parse_hex_matrix(line, order) for line in lines]
    expected = EXPECTED_CLASS_COUNTS[order]
    if len(matrices) != expected:
        raise ValueError(f"expected {expected} order-{order} matrices, found {len(matrices)}")
    return matrices


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download_corpus(orders: list[int], destination: Path) -> dict[int, Path]:
    """Download missing corpus files and write source/hash metadata."""

    destination.mkdir(parents=True, exist_ok=True)
    paths: dict[int, Path] = {}
    metadata: dict[str, object] = {"source": BASE_URL, "files": {}}
    for order in orders:
        url = corpus_url(order)
        path = destination / f"had{order}.txt"
        if not path.exists():
            print(f"downloading {url}")
            with urllib.request.urlopen(url, timeout=60) as response:
                path.write_bytes(response.read())
        paths[order] = path
        metadata["files"][str(order)] = {
            "url": url,
            "path": str(path),
            "sha256": _sha256(path),
            "expected_classes": EXPECTED_CLASS_COUNTS[order],
        }
    (destination / "manifest.json").write_text(
        json.dumps(metadata, indent=2) + "\n",
        encoding="utf-8",
    )
    return paths
