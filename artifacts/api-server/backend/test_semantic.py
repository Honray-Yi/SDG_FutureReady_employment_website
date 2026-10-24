"""Local E5 tests. Deterministic test vectors never enter the running app cache."""
import asyncio
import csv
import io
import json
from pathlib import Path
import socket
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import zipfile

from fastapi.testclient import TestClient
import numpy as np

from app import app
from explorer_api import service
from local_encoder import LocalModelError
from local_model_assets import assets_present
from semantic_cache import InvalidCache, load_cache, save_cache
from semantic_catalogue import DIMENSIONS, MODEL, load_catalogue, normalize_text
from semantic_matching import AnalysisError, SemanticMatcher

SYNTHETIC = "Synthetic experience: I built a fictional data analysis project and tested model outputs."


def vector(axis):
    row = [0.0] * DIMENSIONS
    row[axis] = 1.0
    return row


class EncoderStub:
    def __init__(self, responses):
        self.responses, self.calls = responses, []

    def encode(self, chunks):
        self.calls.append(chunks)
        item = self.responses.pop(0)
        if isinstance(item, Exception):
            raise item
        return np.array(item, dtype="<f4")


class MatchingTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.csv, self.cache = self.root / "jobs.csv", self.root / "jobs.npz"
        with self.csv.open("w", encoding="utf-8", newline="") as output:
            writer = csv.writer(output)
            writer.writerow(["job_name", "job_text"])
            writer.writerow(["测试职业 A", "合成数据工程项目经历与数据分析。"])
            writer.writerow(["测试职业 B", "合成视觉设计和创作经历。"])
        self.files = patch("semantic_matching.assets_present", return_value=True)
        self.tokens = patch("semantic_matching.tokenizer", return_value=SimpleNamespace(
            encode=lambda text, **_: SimpleNamespace(ids=list(range(len(text.split())))),
        ))
        self.files.start()
        self.tokens.start()

    def tearDown(self):
        self.tokens.stop()
        self.files.stop()
        self.tmp.cleanup()

    async def test_cosine_math_sort_and_cache_reuse(self):
        stub = EncoderStub([[vector(0), vector(1)], [vector(0)], [vector(1)]])
        with patch("semantic_matching.encoder", return_value=stub):
            matcher = SemanticMatcher(self.csv, self.cache)
            first = await matcher.match(SYNTHETIC)
            second = await matcher.match(SYNTHETIC + " Alternate fictional project.")
        self.assertEqual(first["rankings"][0]["job_name"], "测试职业 A")
        self.assertEqual(first["rankings"][0]["similarity"], 1.0)
        self.assertEqual(first["rankings"][1]["similarity"], 0.0)
        self.assertEqual(second["rankings"][0]["job_name"], "测试职业 B")
        self.assertEqual([len(c) for c in stub.calls], [2, 1, 1])
        self.assertEqual(first["status"]["dimensions"], 384)
        self.assertEqual(first["status"]["mode"], "local_text_embedding")
        self.assertEqual(len(first["input_sha256"]), 64)
        with np.load(self.cache, allow_pickle=False) as saved:
            self.assertEqual(set(saved.files), {"manifest", "vectors"})
            self.assertNotIn(SYNTHETIC, str(saved["manifest"]))
        with patch("semantic_matching.encoder", side_effect=AssertionError("No inference expected")):
            restored = SemanticMatcher(self.csv, self.cache)
            self.assertTrue(restored.status()["cache_ready"])
            await restored.ensure_index()

    async def test_long_resume_chunk_weighting_and_no_truncation(self):
        stub = EncoderStub([[vector(0), vector(1)], [vector(0), vector(1)]])
        with patch("semantic_matching.encoder", return_value=stub):
            result = await SemanticMatcher(self.csv, self.cache).match("word " * 400)
        self.assertEqual(result["chunk_count"], 2)
        self.assertEqual(result["input_tokens"], 400)
        self.assertEqual([len(chunk) for chunk in stub.calls[1]], [384, 16])
        expected = 384 / np.sqrt(384 ** 2 + 16 ** 2)
        self.assertAlmostEqual(result["rankings"][0]["similarity"], expected, places=5)

    async def test_token_overflow_rejected_without_inference(self):
        with patch("semantic_matching.encoder", side_effect=AssertionError("must not run")):
            with self.assertRaises(AnalysisError) as caught:
                await SemanticMatcher(self.csv, self.cache).match("word " * 13000)
        self.assertEqual(caught.exception.code, "too_many_tokens")

    async def test_model_missing_is_explicit_never_a_fallback(self):
        with patch("semantic_matching.assets_present", return_value=False):
            matcher = SemanticMatcher(self.csv, self.cache)
            self.assertEqual(matcher.status()["state"], "model_missing")
            with self.assertRaises(AnalysisError) as caught:
                await matcher.match(SYNTHETIC)
            self.assertEqual(caught.exception.code, "model_missing")
        self.assertFalse(self.cache.exists())

    async def test_old_model_or_wrong_dimension_cache_is_rejected(self):
        _, config = load_catalogue(self.csv)
        for changed in [{"dimensions": 128}, {"model": "obsolete-remote-model"}, {"prefix": "passage: "}]:
            save_cache(self.cache, np.array([vector(0), vector(1)], dtype="<f4"), {**config, **changed})
            matcher = SemanticMatcher(self.csv, self.cache)
            self.assertEqual(matcher.status()["state"], "cache_invalid")
            with self.assertRaises(AnalysisError):
                await matcher.match(SYNTHETIC)

    async def test_inference_failure_is_sanitized(self):
        stub = EncoderStub([LocalModelError("MUST-NOT-LEAK-TEXT")])
        with patch("semantic_matching.encoder", return_value=stub):
            with self.assertRaises(AnalysisError) as caught:
                await SemanticMatcher(self.csv, self.cache).match(SYNTHETIC)
        self.assertEqual(caught.exception.code, "model_unavailable")
        self.assertNotIn("MUST-NOT-LEAK", caught.exception.message)
        self.assertFalse(self.cache.exists())

    async def test_invalid_vectors_are_rejected(self):
        for invalid in [[0.0] * 128, [float("nan")] * DIMENSIONS, [0.0] * DIMENSIONS]:
            stub = EncoderStub([[invalid, invalid]])
            with patch("semantic_matching.encoder", return_value=stub):
                with self.assertRaises(AnalysisError):
                    await SemanticMatcher(self.csv, self.cache).match(SYNTHETIC)
        self.assertFalse(self.cache.exists())

    async def test_concurrent_first_calls_build_index_once(self):
        stub = EncoderStub([[vector(0), vector(1)], [vector(0)], [vector(1)]])
        with patch("semantic_matching.encoder", return_value=stub):
            matcher = SemanticMatcher(self.csv, self.cache)
            values = await asyncio.gather(matcher.match(SYNTHETIC), matcher.match(SYNTHETIC))
        self.assertEqual(len(values), 2)
        self.assertEqual(sum(len(c) == 2 for c in stub.calls), 1)

    async def test_resource_budget_prevents_inference(self):
        matcher = SemanticMatcher(self.csv, self.cache)
        matcher.requests.extend([time.monotonic()] * 30)
        with patch("semantic_matching.encoder", side_effect=AssertionError("must not run")):
            with self.assertRaises(AnalysisError) as caught:
                await matcher.match(SYNTHETIC)
        self.assertEqual(caught.exception.code, "analysis_limit")

    async def test_ids_stable_and_cache_bound_to_text_and_weights(self):
        jobs, config = load_catalogue(self.csv)
        save_cache(self.cache, np.array([vector(0), vector(1)], dtype="<f4"), config)
        self.csv.write_text(self.csv.read_text().replace("合成视觉设计", "全新的合成视觉设计"), encoding="utf-8")
        changed_jobs, changed = load_catalogue(self.csv)
        self.assertEqual(jobs[1]["job_id"], changed_jobs[1]["job_id"])
        with self.assertRaises(InvalidCache):
            load_cache(self.cache, changed)
        with self.assertRaises(InvalidCache):
            load_cache(self.cache, {**config, "model_sha256": "changed"})
        self.assertEqual(normalize_text("  Ａ\n B  "), "A B")


class ExplorerContractTests(unittest.TestCase):
    def setUp(self):
        service.cache_clear()
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()
        service.cache_clear()

    def test_independent_endpoints_need_no_key(self):
        self.assertEqual(self.client.get("/api/healthz").status_code, 200)
        status = self.client.get("/api/explorer/status").json()
        self.assertEqual(status["model"], MODEL)
        self.assertEqual(status["mode"], "local_text_embedding")
        self.assertNotIn("key_configured", status)
        jobs = self.client.get("/api/explorer/jobs").json()
        self.assertEqual(len(jobs["jobs"]), 65)
        self.assertEqual(len(self.client.get("/api/explorer/demos").json()["profiles"]), 5)

    def test_missing_model_returns_no_fake_scores(self):
        with patch("semantic_matching.assets_present", return_value=False):
            response = self.client.post("/api/explorer/match", json={"text": SYNTHETIC, "is_synthetic": True})
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["detail"]["code"], "model_missing")
        self.assertNotIn("rankings", response.json())

    def test_synthetic_confirmation_and_no_external_consent_required(self):
        for extras in [{"is_synthetic": False}, {"is_synthetic": "true"}, {},
                       {"is_synthetic": True, "external_processing_consent": True}]:
            response = self.client.post("/api/explorer/match", json={"text": SYNTHETIC, **extras})
            self.assertEqual(response.status_code, 422)
            self.assertNotIn(SYNTHETIC, response.text)

    def test_body_limit(self):
        response = self.client.post("/api/explorer/match", content=b"a" * (512 * 1024 + 1))
        self.assertEqual(response.status_code, 413)

    def test_docx_extraction_is_local_and_independent(self):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as output:
            output.writestr("word/document.xml",
                '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                f"<w:body><w:p><w:r><w:t>{SYNTHETIC}</w:t></w:r></w:p></w:body></w:document>")
        with patch("socket.socket.connect", side_effect=AssertionError("network prohibited")):
            response = self.client.post("/api/explorer/upload", content=buffer.getvalue(), headers={
                "content-type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "x-document-format": "docx", "x-synthetic-profile": "true",
            })
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["document"]["text"], SYNTHETIC)
        self.assertNotIn("rankings", response.json())


@unittest.skipUnless(assets_present(), "Provision local model files before the offline model smoke test.")
class RealLocalModelTests(unittest.TestCase):
    def test_actual_model_offline_distinct_profiles_and_repeatability(self):
        service.cache_clear()
        texts = [
            "合成经历：我用 Python 和 PyTorch 在虚构数据集训练机器学习分类器，调参、交叉验证、分析预测误差，使用 scikit-learn 进行特征工程。",
            "合成经历：我为虚构品牌制作海报与视觉设计，使用 Photoshop、Illustrator、Figma 和 Stable Diffusion 生成创意插画与广告图。",
        ]
        with patch("socket.socket.connect", side_effect=AssertionError("Network prohibited during inference")):
            with TestClient(app) as client:
                one = client.post("/api/explorer/match", json={"text": texts[0], "is_synthetic": True})
                two = client.post("/api/explorer/match", json={"text": texts[1], "is_synthetic": True})
                again = client.post("/api/explorer/match", json={"text": texts[0], "is_synthetic": True})
        self.assertEqual(one.status_code, 200, one.text)
        self.assertEqual(two.status_code, 200, two.text)
        self.assertEqual(one.json()["rankings"], again.json()["rankings"])
        self.assertNotEqual(one.json()["rankings"][0]["job_id"], two.json()["rankings"][0]["job_id"])
        self.assertEqual(len(one.json()["rankings"]), 65)
        scores = [row["similarity"] for row in one.json()["rankings"]]
        self.assertEqual(scores, sorted(scores, reverse=True))
        self.assertTrue(all(-1 <= score <= 1 for score in scores))
        self.assertEqual(one.json()["status"]["dimensions"], 384)
        self.assertNotIn("external_processing_consent", one.json())
        service.cache_clear()


if __name__ == "__main__":
    unittest.main()
