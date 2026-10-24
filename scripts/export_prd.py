"""Create a simple, editable Word PRD using standard Office Open XML."""
from pathlib import Path
import re
from xml.sax.saxutils import escape
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/Product-Requirements-Document.en.md"
OUTPUT = ROOT / "generated-artifacts/FutureReady-Product-Requirements-Document.docx"


def main():
    paragraphs = []
    for line in SOURCE.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        level = len(line) - len(line.lstrip("#"))
        style = "Title" if level == 1 else "Heading1" if level == 2 else "Heading2" if level == 3 else "Normal"
        text = re.sub(r"\*\*(.*?)\*\*", r"\1", line[level:].strip() if level else line)
        paragraphs.append(
            f'<w:p><w:pPr><w:pStyle w:val="{style}"/></w:pPr>'
            f'<w:r><w:t xml:space="preserve">{escape(text)}</w:t></w:r></w:p>')
    document = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        '<w:body>' + "".join(paragraphs) +
        '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/>'
        '<w:pgMar w:top="1134" w:right="1134" w:bottom="1134" w:left="1134"/>'
        '</w:sectPr></w:body></w:document>')
    styles = (
        '<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        '<w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Calibri" w:eastAsia="Microsoft YaHei"/>'
        '<w:sz w:val="21"/></w:rPr></w:rPrDefault>'
        '<w:pPrDefault><w:pPr><w:spacing w:after="140" w:line="300" w:lineRule="auto"/>'
        '</w:pPr></w:pPrDefault></w:docDefaults>'
        '<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/></w:style>'
        + "".join(
            f'<w:style w:type="paragraph" w:styleId="{name}"><w:name w:val="{name}"/>'
            f'<w:basedOn w:val="Normal"/><w:pPr><w:keepNext/><w:spacing w:before="280" w:after="160"/>'
            f'<w:outlineLvl w:val="{outline}"/></w:pPr><w:rPr><w:b/><w:color w:val="164E46"/>'
            f'<w:sz w:val="{size}"/></w:rPr></w:style>'
            for name, size, outline in [("Title", 38, 0), ("Heading1", 28, 0), ("Heading2", 24, 1)])
        + '</w:styles>')
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUTPUT, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml",
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
            '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/></Types>')
        archive.writestr("_rels/.rels",
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>')
        archive.writestr("word/document.xml", document)
        archive.writestr("word/styles.xml", styles)
        archive.writestr("word/_rels/document.xml.rels",
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>')
    print(OUTPUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
