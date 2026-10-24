"""Check approved presentation copy, required PRD sections and Office deliverables."""
from html import unescape
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DECK = ROOT / "artifacts/future-ready-presentation"


def normalized(text):
    return re.sub(r"\s+", " ", unescape(text)).strip()


def main():
    outline = (ROOT / "docs/Presentation-Outline.md").read_text()
    expected = []
    for block in re.split(r"^## ", outline, flags=re.MULTILINE)[1:]:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        expected.append([normalized(line.removeprefix("- ")) for line in lines])
    manifest = json.loads((DECK / "src/data/slides-manifest.json").read_text())
    assert len(manifest) == len(expected) == 10
    assert [entry["position"] for entry in manifest] == list(range(1, 11))
    for entry, copy in zip(manifest, expected, strict=True):
        source = (DECK / entry["filepath"]).read_text()
        actual = [normalized(re.sub(r"<[^>]+>", "", match.group(2)))
                  for match in re.finditer(r"<(h1|p)\b[^>]*>(.*?)</\1>", source, re.DOTALL)]
        assert actual == copy, f"Approved copy mismatch: {entry['filepath']}\n{actual!r}\n{copy!r}"
    prd = (ROOT / "docs/Product-Requirements-Document.en.md").read_text()
    required = ["1. Problem", "2. SDG Alignment", "3. Target Users", "4. Scope", "5. Key Features"]
    assert all(f"## {heading}" in prd for heading in required)
    deliverables = ROOT / "docs/deliverables"
    with zipfile.ZipFile(deliverables / "FutureReady-Product-Requirements-Document.docx") as package:
        document = ET.fromstring(package.read("word/document.xml"))
        text = "".join(document.itertext())
        assert all(heading in text for heading in required)
        assert package.testzip() is None
    with zipfile.ZipFile(deliverables / "FutureReady-Project-Presentation.pptx") as package:
        slides = [name for name in package.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", name)]
        assert len(slides) == 10
        for name in slides:
            ET.fromstring(package.read(name))
        assert package.testzip() is None
    print("Passed: 10 slides match approved copy; all five required PRD sections; valid DOCX and 10-slide PPTX.")


if __name__ == "__main__":
    main()
