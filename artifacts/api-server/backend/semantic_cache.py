"""An atomic, metadata-checked job-vector cache; never stores resume text/vectors."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import tempfile

import numpy as np

from semantic_catalogue import DIMENSIONS, canonical_json


class InvalidCache(ValueError):
    pass


def unit_rows(values: object, count: int) -> np.ndarray:
    vectors = np.asarray(values, dtype="<f4")
    if vectors.shape != (count, DIMENSIONS) or not np.isfinite(vectors).all():
        raise ValueError("Invalid embedding shape or nonfinite values.")
    lengths = np.linalg.norm(vectors, axis=1, keepdims=True)
    if (lengths < 1e-8).any():
        raise ValueError("Zero-length embedding.")
    return np.asarray(vectors / lengths, dtype="<f4")


def matrix_hash(matrix: np.ndarray) -> str:
    return hashlib.sha256(matrix.astype("<f4").tobytes(order="C")).hexdigest()


def load_cache(path: Path, expected: dict) -> np.ndarray | None:
    if not path.exists():
        return None
    try:
        if path.stat().st_size > 10 * 1024 * 1024:
            raise ValueError("Oversize cache.")
        with np.load(path, allow_pickle=False) as cached:
            metadata = json.loads(str(cached["manifest"].item()))
            matrix = cached["vectors"].copy()
        if metadata["configuration"] != expected:
            raise ValueError("Incompatible model, dimensions, document order or text hashes.")
        if metadata["matrix_sha256"] != matrix_hash(matrix):
            raise ValueError("Matrix checksum mismatch.")
        normalized = unit_rows(matrix, len(expected["documents"]))
        if not np.allclose(matrix, normalized, atol=1e-5):
            raise ValueError("Cached rows are not unit-normalized.")
        return normalized
    except (ValueError, KeyError, OSError, TypeError, EOFError) as exc:
        raise InvalidCache("缓存损坏或配置不匹配；请通过 build_job_index.py --rebuild 在本机重建。") from exc


def save_cache(path: Path, matrix: np.ndarray, configuration: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    metadata = {
        "configuration": configuration,
        "matrix_sha256": matrix_hash(matrix),
    }
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, suffix=".npz", delete=False) as out:
            temporary = Path(out.name)
            np.savez_compressed(out, vectors=matrix, manifest=canonical_json(metadata))
            out.flush()
            os.fsync(out.fileno())
        # Matrix + configuration commit together, never a partially paired .npy/JSON.
        os.replace(temporary, path)
    finally:
        if temporary and temporary.exists():
            temporary.unlink()
