import json
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app import app
from demo_auth import COOKIE, DEMO_EMAIL, DEMO_PASSWORD, DemoStore, ITERATIONS, SESSION_SECONDS, password_hash
from sdg_mapping import CATEGORIES, GROUPS, sdgs_for_job
from semantic_catalogue import load_catalogue, normalize_text


class DemoAuthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory()
        cls.path = Path(cls.directory.name) / "users.json"
        cls.service = DemoStore(cls.path)

    @classmethod
    def tearDownClass(cls):
        cls.directory.cleanup()

    def setUp(self):
        self.service.sessions.clear()
        self.service.attempts.clear()
        self.patch = patch("demo_auth.store", return_value=self.service)
        self.patch.start()
        self.client = TestClient(app, base_url="https://testserver")

    def tearDown(self):
        self.client.close()
        self.patch.stop()

    def login(self, password=DEMO_PASSWORD, email=DEMO_EMAIL):
        return self.client.post("/api/demo-auth/login", json={"email": email, "password": password},
                                headers={"X-Demo-Action": "1"})

    def test_hashed_salted_password_persistence(self):
        stored = self.path.read_text()
        self.assertNotIn(DEMO_PASSWORD, stored)
        record = json.loads(stored)["users"][0]
        self.assertEqual(record["iterations"], ITERATIONS)
        self.assertEqual(record["password_hash"], password_hash(DEMO_PASSWORD, record["salt"]))
        self.assertEqual(self.path.stat().st_mode & 0o777, 0o600)
        reloaded = DemoStore(self.path)
        self.assertEqual(reloaded.user, self.service.user)
        self.assertEqual(reloaded.sessions, {})

    def test_cookie_login_restore_rotation_and_logout(self):
        self.assertEqual(self.client.get("/api/demo-auth/me").status_code, 401)
        response = self.login(email=DEMO_EMAIL.upper())
        self.assertEqual(response.status_code, 200)
        cookie = response.headers["set-cookie"].lower()
        for flag in ("httponly", "secure", "samesite=lax", "path=/", "max-age=7200"):
            self.assertIn(flag, cookie)
        first_token = self.client.cookies.get(COOKIE)
        self.assertEqual(self.client.get("/api/demo-auth/me").json()["user"]["email"], DEMO_EMAIL)
        self.assertNotIn("password", response.text)
        self.login()
        with self.assertRaises(Exception):
            self.service.current(first_token)
        response = self.client.post("/api/demo-auth/logout", headers={"X-Demo-Action": "1"})
        self.assertEqual(response.status_code, 204)
        self.assertEqual(len(self.service.sessions), 0)
        self.assertEqual(self.client.get("/api/demo-auth/me").status_code, 401)

    def test_wrong_password_and_unknown_user_same_generic_error(self):
        a = self.login(password="WrongDemoPassword").json()
        b = self.login(email="nobody@example.invalid").json()
        self.assertEqual(a, b)
        self.assertEqual(a["detail"]["code"], "auth_invalid")
        self.assertNotIn("WrongDemoPassword", json.dumps(a))
        self.assertEqual(len(self.service.sessions), 0)

    def test_expiry_and_process_restart_invalidate_session(self):
        self.login()
        for key in self.service.sessions:
            self.service.sessions[key] = time.monotonic() - 1
        self.assertEqual(self.client.get("/api/demo-auth/me").status_code, 401)
        self.login()
        restarted = DemoStore(self.path)
        with self.assertRaises(Exception):
            restarted.current(self.client.cookies.get(COOKIE))
        self.assertEqual(SESSION_SECONDS, 7200)

    def test_mutations_require_header_and_reject_cross_site(self):
        payload = {"email": DEMO_EMAIL, "password": DEMO_PASSWORD}
        self.assertEqual(self.client.post("/api/demo-auth/login", json=payload).status_code, 403)
        self.assertEqual(self.client.post("/api/demo-auth/login", json=payload,
            headers={"X-Demo-Action": "1", "Sec-Fetch-Site": "cross-site"}).status_code, 403)
        self.login()
        self.assertEqual(self.client.post("/api/demo-auth/logout").status_code, 403)
        self.assertEqual(self.client.get("/api/demo-auth/me").status_code, 200)

    def test_rate_limit_is_real(self):
        for _ in range(8):
            self.assertEqual(self.login(password="wrong").status_code, 401)
        self.assertEqual(self.login().status_code, 429)

    def test_malformed_store_is_not_silently_reset(self):
        bad = self.path.parent / "broken.json"
        bad.write_text("{not json")
        with self.assertRaises(ValueError):
            DemoStore(bad)
        self.assertEqual(bad.read_text(), "{not json")

    def test_validation_does_not_echo_password_and_errors_are_not_cacheable(self):
        secret = "UntrustedInput" * 30
        response = self.login(password=secret)
        self.assertEqual(response.status_code, 422)
        self.assertNotIn(secret, response.text)
        response = self.login(password="wrong")
        self.assertEqual(response.headers.get("cache-control"), "no-store")


class SDGTests(unittest.TestCase):
    def test_all_roles_have_explicit_valid_mapping_and_sources(self):
        jobs, _ = load_catalogue()
        known = {j["job_name"] for j in jobs}
        self.assertEqual(len(jobs), 65)
        self.assertTrue(set(normalize_text(name) for names in GROUPS.values() for name in names) <= known)
        for job in jobs:
            records = sdgs_for_job(job)
            self.assertGreaterEqual(len(records), 1, job["job_name"])
            for item in records:
                self.assertTrue(item["target"].startswith(str(item["goal"]) + "."))
                self.assertEqual(item["url"], f"https://sdgs.un.org/goals/goal{item['goal']}")
                self.assertTrue(item["title_en"] and item["title_zh"] and item["reason_en"] and item["reason_zh"])
        self.assertEqual(sdgs_for_job({"job_name": "Unreviewed role"}), [])

    def test_domain_specific_mappings(self):
        jobs, _ = load_catalogue()
        goals = {j["job_name"]: {r["goal"] for r in sdgs_for_job(j)} for j in jobs}
        self.assertIn(3, goals["医疗AI应用专家"])
        self.assertIn(4, goals["AI培训讲师"])
        self.assertIn(16, goals["法律科技AI专家"])
        self.assertIn(7, goals["AI芯片设计工程师"])
        self.assertIn(11, goals["自动驾驶算法工程师"])

    def test_public_catalogue_includes_sdgs_without_changing_embedding_source(self):
        jobs, config = load_catalogue()
        original = repr(jobs)
        with TestClient(app) as client:
            response = client.get("/api/explorer/jobs")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(all(j["sdg_contributions"] for j in response.json()["jobs"]))
        self.assertEqual(repr(jobs), original)
        self.assertEqual(load_catalogue()[1]["catalogue_hash"], config["catalogue_hash"])
