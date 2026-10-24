"""Portable development launcher; not a production server."""
import argparse
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frontend-port", type=int, default=5173)
    parser.add_argument("--backend-port", type=int, default=8080)
    args = parser.parse_args()
    if not all(1 <= port <= 65535 for port in (args.frontend_port, args.backend_port)):
        parser.error("Ports must be in 1..65535.")
    if args.frontend_port == args.backend_port:
        parser.error("Frontend and backend ports must differ.")
    pnpm = shutil.which("pnpm")
    if not pnpm:
        parser.error("Install pnpm before running this launcher.")
    children = []
    try:
        children.append(subprocess.Popen(
            [sys.executable, str(ROOT / "artifacts/api-server/backend/run_server.py")],
            cwd=ROOT, env={**os.environ, "PORT": str(args.backend_port)},
            start_new_session=os.name == "posix",
        ))
        children.append(subprocess.Popen(
            [pnpm, "--filter", "@workspace/future-ready", "run", "dev"], cwd=ROOT,
            env={**os.environ, "PORT": str(args.frontend_port), "BASE_PATH": "/",
                 "FUTUREREADY_LOCAL_API_ORIGIN": f"http://127.0.0.1:{args.backend_port}"},
            start_new_session=os.name == "posix",
        ))
        print(f"FutureReady: http://localhost:{args.frontend_port} (Ctrl+C to stop)", flush=True)
        while all(child.poll() is None for child in children):
            time.sleep(0.2)
        return next((child.returncode or 1 for child in children if child.poll() is not None), 1)
    except KeyboardInterrupt:
        return 0
    finally:
        for child in children:
            if child.poll() is None:
                if os.name == "posix":
                    os.killpg(child.pid, signal.SIGTERM)
                else:
                    child.terminate()
        for child in children:
            try:
                child.wait(timeout=8)
            except subprocess.TimeoutExpired:
                if os.name == "posix":
                    os.killpg(child.pid, signal.SIGKILL)
                else:
                    child.kill()
                child.wait()


if __name__ == "__main__":
    sys.exit(main())
