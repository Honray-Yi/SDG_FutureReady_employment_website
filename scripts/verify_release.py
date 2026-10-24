"""Verify an exported ZIP without reusing project modules, model cache or Replit secrets.

Installs locked Python wheels into a temporary --target directory, NOT a virtualenv.
Downloads the pinned public model afresh. Needs internet and ~2 GB free disk.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, default=ROOT / "generated-artifacts/FutureReady-GitHub.zip")
    args = parser.parse_args()
    output = ROOT / "generated-artifacts"
    output.mkdir(exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="github-verification-", dir=output))
    with zipfile.ZipFile(args.archive) as archive:
        for name in archive.namelist():
            if not (work / name).resolve().is_relative_to(work.resolve()):
                raise ValueError("Unsafe archive path.")
        archive.extractall(work)
    project = work / "FutureReady"
    manifest = json.loads((project / "release-manifest.json").read_text())["files"]
    for name, expected in manifest.items():
        contents = (project / name).read_bytes()
        if len(contents) != expected["bytes"] or hashlib.sha256(contents).hexdigest() != expected["sha256"]:
            raise ValueError(f"Release integrity failed: {name}")
    required = ["README.md", "requirements.lock", "pnpm-lock.yaml",
                "artifacts/api-server/catalogue/job_list.csv", "artifacts/api-server/backend/app.py",
                "lib/api-spec/openapi.yaml", "artifacts/future-ready/src/main.tsx"]
    assert all((project / name).is_file() for name in required)
    assert not any(part in {".cache", "node_modules", ".pythonlibs"} for name in manifest for part in Path(name).parts)
    env = {k: v for k, v in os.environ.items() if not (
        k.startswith("REPLIT_") or k in {"REPL_ID", "DATABASE_URL", "PRIVATE_OBJECT_DIR",
        "PUBLIC_OBJECT_SEARCH_PATHS", "DEFAULT_OBJECT_STORAGE_BUCKET_ID", "SESSION_SECRET", "OPENAI_API_KEY",
        "PORT", "BASE_PATH", "FUTUREREADY_LOCAL_API_ORIGIN", "VIRTUAL_ENV", "PYTHONPATH"})}
    target = project / ".cache/verification-python"
    env["PYTHONPATH"] = str(target)
    env["PYTHONNOUSERSITE"] = "1"
    steps = []
    completed = False

    def run(name, command, extra=None):
        print(f"\n=== {name} ===", flush=True)
        start = time.monotonic()
        subprocess.run(command, cwd=project, env={**env, **(extra or {})}, check=True)
        steps.append({"name": name, "status": "passed", "seconds": round(time.monotonic() - start, 2)})

    try:
        run("Fresh locked Node dependencies", ["pnpm", "install", "--frozen-lockfile"])
        run("Fresh locked Python dependencies (isolated target, no virtualenv)", [
            "uv", "pip", "install", "--python", sys.executable, "--target", str(target),
            "--require-hashes", "-r", "requirements.lock"])
        run("Fresh model download with SHA-256 verification", [
            sys.executable, "artifacts/api-server/backend/local_model_assets.py", "--from-hub"])
        run("Build complete career vector index", [sys.executable, "artifacts/api-server/backend/build_job_index.py"])
        run("Backend regression and real-model tests", [sys.executable, "-m", "unittest", "discover",
            "-s", "artifacts/api-server/backend", "-p", "test_*.py", "-q"])
        run("OpenAPI regeneration", ["pnpm", "--filter", "@workspace/api-spec", "run", "codegen"])
        run("All workspace TypeScript checks", ["pnpm", "run", "typecheck"])
        run("Production frontend build", ["pnpm", "--filter", "@workspace/future-ready", "run", "build"],
            {"PORT": "5173", "BASE_PATH": "/", "NODE_ENV": "production"})
        run("Standalone launcher and full HTTP workflow", [sys.executable, "scripts/smoke_local.py"])
        run("Approved presentation copy and Office deliverables", [sys.executable, "scripts/verify_presentation.py"])
        run("Slide manifest validation", ["pnpm", "--filter", "@workspace/future-ready-presentation", "run", "validate-slides"])
        run("Production presentation build", ["pnpm", "--filter", "@workspace/future-ready-presentation", "run", "build"])
        completed = True
    finally:
        report = {"archive_sha256": hashlib.sha256(args.archive.read_bytes()).hexdigest(),
                  "source_files": len(manifest), "isolated_directory": str(work.relative_to(ROOT)),
                  "python": sys.version.split()[0], "steps": steps,
                  "complete": completed}
        report_path = output / "GitHub-Verification.json"
        report_path.write_text(json.dumps(report, indent=2) + "\n")
        print(f"Verification report: {report_path}", flush=True)


if __name__ == "__main__":
    main()
