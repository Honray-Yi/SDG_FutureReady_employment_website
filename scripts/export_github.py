"""Export selected source files, never environment files, model weights or chat state."""
from pathlib import Path, PurePosixPath
import hashlib
import json
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "generated-artifacts/FutureReady-GitHub.zip"
ROOT_FILES = {
    "README.md", ".gitignore", ".npmrc", "package.json", "pnpm-lock.yaml",
    "pnpm-workspace.yaml", "pyproject.toml", "uv.lock", "tsconfig.json", "tsconfig.base.json",
    "requirements.lock",
}
PREFIXES = ("artifacts/future-ready/", "artifacts/future-ready-presentation/", "artifacts/api-server/", "lib/", "src/", "scripts/", "docs/", ".github/")
EXCLUDE_PARTS = {
    "node_modules", "__pycache__", ".replit-artifact", "dist", ".cache", "uploads", "sessions",
    ".git", ".local", ".agents", ".conversation", "coverage", ".venv", ".pythonlibs",
}


def eligible(name):
    path = PurePosixPath(name)
    if not (name in ROOT_FILES or name.startswith(PREFIXES)):
        return False
    if EXCLUDE_PARTS.intersection(path.parts):
        return False
    if path.name.startswith(".env") or path.suffix.lower() in {".pyc", ".pyo", ".pem", ".key", ".tsbuildinfo"}:
        return False
    if path.name in {"users.json", ".DS_Store"}:
        return False
    return name != "scripts/post-merge.sh"  # Replit-specific, not ordinary local setup


def main():
    if (ROOT / ".git").exists():
        names = subprocess.check_output(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"], cwd=ROOT,
        ).decode().split("\0")
    else:
        # A downloaded source ZIP is exportable before git init, too.
        names = [p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*")
                 if not EXCLUDE_PARTS.intersection(p.relative_to(ROOT).parts)]
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    manifest = {}
    with zipfile.ZipFile(OUTPUT, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name in sorted(set(filter(None, names))):
            source = ROOT / name
            if not eligible(name) or not source.is_file() or source.is_symlink():
                continue
            archive.write(source, "FutureReady/" + name)
            manifest[name] = {"bytes": source.stat().st_size,
                              "sha256": hashlib.sha256(source.read_bytes()).hexdigest()}
            count += 1
        archive.writestr("FutureReady/release-manifest.json",
                         json.dumps({"schema_version": 1, "files": manifest}, indent=2) + "\n")
    print(f"Exported {count} source files to {OUTPUT.relative_to(ROOT)} ({OUTPUT.stat().st_size:,} bytes).")


if __name__ == "__main__":
    main()
