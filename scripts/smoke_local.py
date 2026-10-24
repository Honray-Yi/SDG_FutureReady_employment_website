"""Exercise the portable local stack; requires installed deps, model and job index."""
import http.cookiejar
import io
import json
import math
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def port():
    with socket.socket() as connection:
        connection.bind(("127.0.0.1", 0))
        return connection.getsockname()[1]


def main():
    frontend, backend = port(), port()
    while backend == frontend:
        backend = port()
    cookies = http.cookiejar.CookieJar()
    client = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookies))
    base = f"http://127.0.0.1:{frontend}"

    def request(path, body=None, headers=None, method=None):
        if isinstance(body, dict):
            body = json.dumps(body).encode()
            headers = {"Content-Type": "application/json", **(headers or {})}
        with client.open(urllib.request.Request(base + path, data=body, headers=headers or {},
                                                method=method), timeout=60) as response:
            raw = response.read()
            return json.loads(raw) if raw and "application/json" in response.headers.get("Content-Type", "") else raw

    with tempfile.TemporaryFile(mode="w+") as log:
        process = subprocess.Popen(
            [sys.executable, str(ROOT / "scripts/dev_local.py"), "--frontend-port", str(frontend),
             "--backend-port", str(backend)], cwd=ROOT, stdout=log, stderr=log,
        )
        try:
            for attempt in range(100):
                if process.poll() is not None:
                    raise RuntimeError("Local launcher exited before it was ready.")
                try:
                    page = request("/")
                    status = request("/api/explorer/status")
                    if b"root" in page and status.get("state") == "ready":
                        break
                except (OSError, urllib.error.URLError):
                    pass
                time.sleep(.5)
            else:
                raise RuntimeError("Frontend proxy/model did not become ready in 50 seconds.")
            jobs = request("/api/explorer/jobs")["jobs"]
            assert len(jobs) == 65 and all(j["sdg_contributions"] and j["job_name_en"] for j in jobs)
            account = request("/api/demo-auth/login",
                              {"email": "demo@futureready.example", "password": "FutureReadyDemo2026!"},
                              {"X-Demo-Action": "1"})
            assert account["user"]["is_demo"]
            assert request("/api/demo-auth/me")["user"]["email"] == account["user"]["email"]
            text = ("Synthetic resume. I built machine learning classifiers using Python, SQL, "
                    "PyTorch and scikit-learn, performed feature engineering, cross-validation "
                    "and model evaluation on fictional datasets.")
            document = io.BytesIO()
            with zipfile.ZipFile(document, "w") as archive:
                archive.writestr("[Content_Types].xml", '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>')
                archive.writestr("word/document.xml",
                                 '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>'
                                 + text + '</w:t></w:r></w:p></w:body></w:document>')
            uploaded = request("/api/explorer/upload", document.getvalue(), {
                "Content-Type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "X-Document-Format": "docx", "X-Processing-Consent": "true",
            })
            assert "Python" in uploaded["document"]["text"]
            result = request("/api/explorer/match", {
                "text": uploaded["document"]["text"], "processing_consent": True, "keyword_language": "en",
            })
            assert len(result["rankings"]) == 65
            assert {"python", "sql", "ml"} <= {k["keyword_id"] for k in result["keywords"]}
            for role in result["rankings"]:
                assert role["sdg_contributions"] and math.isfinite(role["similarity"])
                assert role["similarity_percent"] == round(max(0, role["similarity"]) * 100, 1)
            selected = result["rankings"][0]
            courses = request(f"/api/explorer/jobs/{selected['job_id']}/courses?language=en")
            assert courses["courses"]
            assert all(c["url"].startswith("https://") for c in courses["courses"])
            request("/api/demo-auth/logout", headers={"X-Demo-Action": "1"}, method="POST")
            try:
                request("/api/demo-auth/me")
            except urllib.error.HTTPError as error:
                assert error.code == 401
            else:
                raise AssertionError("Session remained valid after logout.")
            print(json.dumps({"frontend_proxy": "passed", "demo_login_restore_logout": "passed",
                              "docx_upload": "passed", "real_local_model_ranking": 65,
                              "sdg_coverage": 65, "selected_role_courses": len(courses["courses"])}))
        except BaseException:
            log.seek(0)
            # Server logs contain no request bodies or credential values.
            print(log.read()[-4500:], file=sys.stderr)
            raise
        finally:
            if process.poll() is None:
                process.send_signal(signal.SIGINT)
                try:
                    process.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()


if __name__ == "__main__":
    main()
