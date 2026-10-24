import re
import unittest
from fastapi.testclient import TestClient
from app import app
from explorer_api import service
from job_localization import display_fields
from keyword_matching import recognize
from local_model_assets import assets_present
from semantic_catalogue import load_catalogue

TEXT = "Synthetic resume. I built machine learning models with Python, PyTorch, SQL and scikit-learn, performed feature engineering and cross-validation."


class KeywordTests(unittest.TestCase):
    def test_english_defaults_and_case_insensitivity(self):
        text = "PYTHON, SQL, machine-learning and PyTorch"
        found = recognize(text)
        self.assertEqual({x["keyword_id"] for x in found}, {"python", "sql", "ml", "pytorch"})
        for item in found:
            self.assertEqual(text[item["start"]:item["end"]], item["evidence"])

    def test_word_boundaries_and_deduplication(self):
        found = recognize("JavaScript; JavaScript; pythonic; sqlserver; java; C++; aiops")
        ids = [x["keyword_id"] for x in found]
        self.assertEqual(set(ids), {"javascript", "java", "cpp"})
        self.assertEqual(len(ids), len(set(ids)))

    def test_explicit_chinese_glossary_and_shared_technical_tokens(self):
        text = "我使用 Python 与 SQL 完成机器学习、特征工程和交叉验证。"
        self.assertEqual({x["keyword_id"] for x in recognize(text, "en")}, {"python", "sql"})
        self.assertTrue({"ml", "features", "evaluation", "python", "sql"} <= {x["keyword_id"] for x in recognize(text, "zh")})
        self.assertNotIn("ml", {x["keyword_id"] for x in recognize("machine learning", "zh")})

    def test_all_65_display_translations_preserve_source(self):
        jobs, config = load_catalogue()
        original = repr(jobs)
        for job in jobs:
            translated = display_fields(job)
            self.assertTrue(translated["job_name_en"])
            self.assertTrue(translated["job_text_en"])
            self.assertFalse(re.search(r"[\u3400-\u9fff]", str(translated)))
        self.assertEqual(original, repr(jobs))
        self.assertEqual(load_catalogue()[1]["catalogue_hash"], config["catalogue_hash"])


class LanguageContractTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        service.cache_clear()

    def tearDown(self):
        self.client.close()
        service.cache_clear()

    def test_english_catalogue_and_course_language_cache_identity(self):
        jobs = self.client.get("/api/explorer/jobs").json()["jobs"]
        self.assertEqual(len(jobs), 65)
        job = jobs[0]
        self.assertEqual(job["job_name_en"], "Machine Learning Engineer")
        en = self.client.get(f"/api/explorer/jobs/{job['job_id']}/courses").json()
        zh = self.client.get(f"/api/explorer/jobs/{job['job_id']}/courses?language=zh").json()
        self.assertEqual([c["course_id"] for c in en["courses"]], [c["course_id"] for c in zh["courses"]])
        self.assertFalse(re.search(r"[\u3400-\u9fff]", en["basis"]))
        self.assertTrue(re.search(r"[\u3400-\u9fff]", zh["basis"]))
        for c in en["courses"]:
            for field in ("topic", "reason", "job_evidence"):
                self.assertFalse(re.search(r"[\u3400-\u9fff]", c[field]))
        self.assertEqual(self.client.get(f"/api/explorer/jobs/{job['job_id']}/courses?language=fr").status_code, 422)

    def test_invalid_recognition_language_is_explicit(self):
        response = self.client.post("/api/explorer/match", json={
            "text": TEXT, "processing_consent": True, "keyword_language": "automatic",
        })
        self.assertEqual(response.status_code, 422)
        self.assertNotIn(TEXT, response.text)

    @unittest.skipUnless(assets_present(), "Local model files required.")
    def test_keyword_language_does_not_modify_real_semantic_rankings(self):
        results = []
        for language in ("en", "zh"):
            response = self.client.post("/api/explorer/match", json={
                "text": TEXT, "processing_consent": True, "keyword_language": language,
            })
            self.assertEqual(response.status_code, 200, response.text)
            data = response.json()
            self.assertEqual(data["keyword_language"], language)
            results.append(data)
            ids = {k["keyword_id"] for k in data["keywords"]}
            for rank in data["rankings"]:
                self.assertTrue(set(rank["matched_keyword_ids"]) <= ids)
                self.assertTrue(rank["job_name_en"])
        self.assertIn("ml", {k["keyword_id"] for k in results[0]["keywords"]})
        self.assertNotIn("ml", {k["keyword_id"] for k in results[1]["keywords"]})
        self.assertEqual([(r["job_id"], r["similarity"]) for r in results[0]["rankings"]],
                         [(r["job_id"], r["similarity"]) for r in results[1]["rankings"]])
        self.assertGreater(sum(len(r["matched_keyword_ids"]) for r in results[0]["rankings"]), 0)
