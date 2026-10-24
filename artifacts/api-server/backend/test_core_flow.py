"""The user's critical journey: file -> extracted text -> real ranking -> courses."""
import io
from pathlib import Path
import unittest
from unittest.mock import patch
from xml.sax.saxutils import escape
import zipfile

from fastapi.testclient import TestClient
from app import app
from career_courses import for_job
from explorer_api import service
from local_model_assets import assets_present

EXPERIENCE = (
    "Synthetic test resume. Python developer and machine learning coursework. "
    "Built classifiers with PyTorch, scikit-learn and SQL on fictional data. "
    "Performed feature engineering, cross validation, model evaluation and regression tests."
)


def docx(text=EXPERIENCE):
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml",
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>')
        archive.writestr("_rels/.rels",
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>')
        archive.writestr("word/document.xml",
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            f'<w:body><w:p><w:r><w:t xml:space="preserve">{escape(text)}</w:t></w:r></w:p></w:body></w:document>')
    return output.getvalue()


def pdf(text=EXPERIENCE):
    lines = [text[i:i+80] for i in range(0, len(text), 80)]
    commands = "BT /F1 10 Tf 40 780 Td 14 TL " + " ".join(
        "(" + line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)") + ") Tj T*"
        for line in lines) + " ET"
    stream = commands.encode("ascii")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream",
    ]
    result = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, obj in enumerate(objects, 1):
        offsets.append(len(result))
        result.extend(f"{index} 0 obj\n".encode() + obj + b"\nendobj\n")
    start = len(result)
    result.extend(f"xref\n0 {len(offsets)}\n0000000000 65535 f \n".encode())
    for offset in offsets[1:]:
        result.extend(f"{offset:010d} 00000 n \n".encode())
    result.extend(f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{start}\n%%EOF".encode())
    return bytes(result)


class CoreContractTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()
        service.cache_clear()

    def test_authorization_is_required_and_strict(self):
        for consent in (False, "true", None):
            response = self.client.post("/api/explorer/match", json={
                "text": EXPERIENCE, "is_synthetic": False, "processing_consent": consent,
            })
            self.assertEqual(response.status_code, 422)
            self.assertNotIn(EXPERIENCE, response.text)
        response = self.client.post("/api/explorer/upload", content=docx(), headers={
            "content-type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "x-document-format": "docx",
        })
        self.assertEqual(response.status_code, 422)

    def test_all_jobs_have_only_reviewed_courses_bound_to_the_right_job(self):
        jobs = self.client.get("/api/explorer/jobs").json()["jobs"]
        seen = set()
        for job in jobs:
            response = self.client.get(f"/api/explorer/jobs/{job['job_id']}/courses")
            self.assertEqual(response.status_code, 200, response.text)
            data = response.json()
            self.assertEqual(data["job_id"], job["job_id"])
            self.assertEqual(data["job_name"], job["job_name"])
            self.assertGreaterEqual(len(data["courses"]), 1)
            self.assertLessEqual(len(data["courses"]), 4)
            ids = [course["course_id"] for course in data["courses"]]
            self.assertEqual(len(ids), len(set(ids)))
            for course in data["courses"]:
                self.assertTrue(course["url"].startswith("https://"))
                self.assertTrue(course["checked_at"])
                self.assertTrue(course["reason"])
                self.assertTrue(course["job_evidence"])
                seen.add(course["course_id"])
        self.assertGreater(len(seen), 8)
        self.assertEqual(self.client.get("/api/explorer/jobs/nonexistent/courses").status_code, 404)

    def test_broken_docx_and_empty_pdf_are_explicit_errors(self):
        for kind, content, mime in [
            ("docx", b"not a valid Word file", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
            ("pdf", pdf(""), "application/pdf"),
        ]:
            response = self.client.post("/api/explorer/upload", content=content, headers={
                "content-type": mime, "x-document-format": kind, "x-processing-consent": "true",
            })
            self.assertEqual(response.status_code, 422, response.text)
            self.assertNotIn("rankings", response.json())

    def test_course_failure_does_not_return_irrelevant_placeholders(self):
        job = self.client.get("/api/explorer/jobs").json()["jobs"][0]
        with patch("explorer_api.for_job", side_effect=ValueError("private-details")):
            response = self.client.get(f"/api/explorer/jobs/{job['job_id']}/courses")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["detail"]["code"], "courses_unavailable")
        self.assertNotIn("private-details", response.text)

    @unittest.skipUnless(assets_present(), "Local model is required for the full actual-model journey.")
    def test_pdf_and_docx_complete_local_flow_without_external_analysis(self):
        for kind, content, mime in [
            ("pdf", pdf(), "application/pdf"),
            ("docx", docx(), "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
        ]:
            with patch("socket.socket.connect", side_effect=AssertionError("External connection prohibited")):
                uploaded = self.client.post("/api/explorer/upload", content=content, headers={
                    "content-type": mime, "x-document-format": kind, "x-processing-consent": "true",
                })
                self.assertEqual(uploaded.status_code, 200, uploaded.text)
                self.assertFalse(uploaded.json()["is_synthetic"])
                text = uploaded.json()["document"]["text"]
                self.assertIn("Python", text)
                result = self.client.post("/api/explorer/match", json={
                    "text": text, "is_synthetic": False, "processing_consent": True,
                })
                self.assertEqual(result.status_code, 200, result.text)
                ranks = result.json()["rankings"]
                self.assertEqual(len(ranks), 65)
                for rank in ranks:
                    self.assertEqual(rank["similarity_percent"], round(max(0, rank["similarity"]) * 100, 1))
                courses = self.client.get(f"/api/explorer/jobs/{ranks[0]['job_id']}/courses")
                self.assertEqual(courses.status_code, 200, courses.text)
                self.assertGreater(len(courses.json()["courses"]), 0)


if __name__ == "__main__":
    folder = Path("generated-artifacts/test-resumes")
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "synthetic-ml-resume.pdf").write_bytes(pdf())
    (folder / "synthetic-ml-resume.docx").write_bytes(docx())
    (folder / "synthetic-design-resume.docx").write_bytes(docx(
        "Synthetic design resume. Created fictional brand identities, illustrations, "
        "advertising posters and visual design with Photoshop, Figma, Stable Diffusion, "
        "Midjourney and typography. Managed visual assets and creative storyboards."))
    (folder / "invalid-resume.docx").write_bytes(b"invalid Word file")
    print("Created synthetic browser-test fixtures in", folder)
