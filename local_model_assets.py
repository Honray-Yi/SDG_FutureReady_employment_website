"""Reproducible public model assets: App Storage durability, local inference only.

Only setup/build code downloads assets. No inference path contacts the hub/GCS.
"""
from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import tempfile
import urllib.request

from semantic_catalogue import MODEL_REVISION, MODEL_SHA256, TOKENIZER_SHA256

ROOT = Path(__file__).resolve().parents[3]
MODEL_DIR = ROOT / ".cache/futureready/models" / MODEL_REVISION
REPOSITORY = "Xenova/multilingual-e5-small"
ASSETS = {
    "onnx/model_quantized.onnx": (MODEL_SHA256, 118308185),
    "tokenizer.json": (TOKENIZER_SHA256, 17082730),
}


def file_hash(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def assets_present() -> bool:
    return all((MODEL_DIR / name).is_file() and (MODEL_DIR / name).stat().st_size == size
               for name, (_, size) in ASSETS.items())


def verify_assets() -> None:
    for name, (expected, size) in ASSETS.items():
        path = MODEL_DIR / name
        if not path.is_file() or path.stat().st_size != size or file_hash(path) != expected:
            raise ValueError("Local model asset missing or checksum mismatch.")


def storage_location():
    # The standard Replit sidecar credentials flow; SDK owns authentication.
    # Never print credentials, signed URLs, environment values, or request texts.
    import google.auth
    from google.cloud import storage
    credentials, _ = google.auth.load_credentials_from_dict({
        "type": "external_account",
        "audience": "replit",
        "subject_token_type": "access_token",
        "token_url": "http://127.0.0.1:1106/token",
        "credential_source": {
            "url": "http://127.0.0.1:1106/credential",
            "format": {"type": "json", "subject_token_field_name": "access_token"},
        },
    }, scopes=["https://www.googleapis.com/auth/cloud-platform"])
    client = storage.Client(project="replit", credentials=credentials)
    private = os.environ["PRIVATE_OBJECT_DIR"].strip("/").split("/", 1)
    return client.bucket(private[0]), private[1] + "/models/" + MODEL_REVISION


def prepare(from_hub: bool = False, store: bool = False) -> None:
    location = storage_location() if store or not from_hub else None
    for name, (expected, size) in ASSETS.items():
        target = MODEL_DIR / name
        target.parent.mkdir(parents=True, exist_ok=True)
        valid = target.is_file() and target.stat().st_size == size and file_hash(target) == expected
        if not valid:
            with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as out:
                temporary = Path(out.name)
            try:
                if from_hub:
                    url = f"https://huggingface.co/{REPOSITORY}/resolve/{MODEL_REVISION}/{name}"
                    request = urllib.request.Request(url, headers={"User-Agent": "FutureReady-model-setup"})
                    with urllib.request.urlopen(request, timeout=120) as source, temporary.open("wb") as out:
                        total = 0
                        for chunk in iter(lambda: source.read(1024 * 1024), b""):
                            total += len(chunk)
                            if total > size:
                                raise ValueError("Asset exceeded its expected size.")
                            out.write(chunk)
                else:
                    bucket, prefix = location
                    bucket.blob(prefix + "/" + name).download_to_filename(str(temporary), timeout=120)
                if temporary.stat().st_size != size or file_hash(temporary) != expected:
                    raise ValueError("Downloaded model asset checksum mismatch.")
                os.replace(temporary, target)
            finally:
                temporary.unlink(missing_ok=True)
        if store:
            bucket, prefix = location
            blob = bucket.blob(prefix + "/" + name)
            blob.metadata = {"sha256": expected, "source": REPOSITORY, "revision": MODEL_REVISION}
            blob.upload_from_filename(str(target), timeout=180)
    verify_assets()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Restore version-pinned E5 assets; no resume data is transmitted.")
    parser.add_argument("--from-hub", action="store_true", help="Download public model files for initial provisioning.")
    parser.add_argument("--store", action="store_true", help="Persist public model files in App Storage.")
    args = parser.parse_args()
    prepare(args.from_hub, args.store)
    print("Local E5 model and tokenizer verified; no user documents transmitted.")
