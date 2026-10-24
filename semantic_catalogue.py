"""Canonical documents for direct local multilingual E5 matching."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import re
import unicodedata

MODEL = "intfloat/multilingual-e5-small"
DIMENSIONS = 384
MODEL_REVISION = "761b726dd34fb83930e26aab4e9ac3899aa1fa78"
MODEL_SHA256 = "f80102d3f2a1229f387d3c81909990d8945513e347b0eab049f7de3c6f98c193"
TOKENIZER_SHA256 = "0b44a9d7b51c3c62626640cda0e2c2f70fdacdc25bbbd68038369d14ebdf4c39"
PREPROCESSING = "nfkc-whitespace-v1"
CHUNK_TOKENS = 384
MAX_INPUT_TOKENS = 12000
AGGREGATION = "token-weighted mean of unit chunk embeddings, then L2 normalization"
CATALOGUE_PATH = Path(__file__).resolve().parents[1] / "catalogue/job_list.csv"


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", text)).strip()


def sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def load_catalogue(path: Path = CATALOGUE_PATH) -> tuple[list[dict], dict]:
    with path.open(encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        if reader.fieldnames != ["job_name", "job_text"]:
            raise ValueError("Expected CSV columns job_name,job_text.")
        jobs = []
        for row in reader:
            name = normalize_text(row.get("job_name") or "")
            description = normalize_text(row.get("job_text") or "")
            if not name or not description:
                raise ValueError("Empty job name or description.")
            jobs.append({
                "job_id": "job-" + sha256(name)[:16],
                "job_name": name,
                "job_text": description,
            })
    if not jobs or len({job["job_id"] for job in jobs}) != len(jobs):
        raise ValueError("Catalogue must be nonempty with unique normalized job names.")
    # IDs survive reordering and description edits. Hashes bind every vector to its text.
    documents = [
        {"job_id": job["job_id"], "text_sha256": sha256(job_document(job))}
        for job in jobs
    ]
    manifest = {
        "schema": "futureready-local-job-embeddings-v2",
        "model": MODEL,
        "revision": MODEL_REVISION,
        "model_sha256": MODEL_SHA256,
        "tokenizer_sha256": TOKENIZER_SHA256,
        "runtime": "onnx-int8-cpu",
        "prefix": "query: ",
        "pooling": "attention-mask mean, including special and prefix tokens",
        "dimensions": DIMENSIONS,
        "preprocessing": PREPROCESSING,
        "chunk_tokens": CHUNK_TOKENS,
        "max_input_tokens": MAX_INPUT_TOKENS,
        "aggregation": AGGREGATION,
        "job_document": "normalized job_name + job_text",
        "documents": documents,
        "catalogue_hash": sha256(canonical_json(jobs)),
    }
    return jobs, manifest


def job_document(job: dict) -> str:
    return normalize_text(job["job_name"] + "\n" + job["job_text"])
