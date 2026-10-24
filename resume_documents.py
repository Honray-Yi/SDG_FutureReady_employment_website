"""Memory-only bounded PDF/DOCX extraction. Uploaded files never touch disk."""
import io,json,sys,zipfile
from xml.etree import ElementTree as ET
from intake.pdf_worker import extract as pdf_extract
MAX_BYTES=8*1024*1024
def extract(raw,kind):
    if len(raw)>MAX_BYTES:return {'error':'file_too_large','message':'文件不能超过 8MB。'}
    if kind=='pdf':
        result=pdf_extract(raw)
        if 'error' in result:return result
        return {'text':'\n'.join(result['pages']),'page_count':result['page_count'],'format':'pdf','page_count_basis':'PDF pages','scanned_supported':False}
    if kind!='docx':return {'error':'unsupported_type','message':'只支持可复制文字的 PDF 和 DOCX。'}
    if not raw.startswith(b'PK'):return {'error':'invalid_docx','message':'不是有效 DOCX。'}
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            items=archive.infolist()
            if len(items)>1000 or sum(x.file_size for x in items)>20*1024*1024:return {'error':'docx_expansion_limit','message':'DOCX 解压后的内容过大。'}
            if any(x.file_size>1000000 and x.compress_size and x.file_size/x.compress_size>100 for x in items):return {'error':'docx_expansion_limit','message':'DOCX 压缩比异常。'}
            xml=archive.read('word/document.xml')
            if b'<!DOCTYPE' in xml or b'<!ENTITY' in xml:return {'error':'invalid_docx','message':'不接受带自定义实体的 DOCX。'}
            root=ET.fromstring(xml);ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            paragraphs=[''.join(p.itertext()) for p in root.findall('.//w:p',ns)]
            # itertext includes field instructions; only display w:t text nodes as evidence.
            paragraphs=[''.join(t.text or '' for t in p.findall('.//w:t',ns)) for p in root.findall('.//w:p',ns)]
            text='\n'.join(paragraphs)
            explicit=1+sum(b.get('{'+ns['w']+'}type')=='page' for b in root.findall('.//w:br',ns))
            pages=explicit
            if 'docProps/app.xml' in archive.namelist():
                app=ET.fromstring(archive.read('docProps/app.xml'))
                node=next((n for n in app.iter() if n.tag.rsplit('}',1)[-1]=='Pages'),None)
                if node is not None and node.text and node.text.isdigit():pages=max(pages,int(node.text))
            if pages>20:return {'error':'too_many_pages','message':'最多支持 20 页。DOCX 按页数元数据与显式分页检查。'}
            if len(text)>100000:return {'error':'too_much_text','message':'文件文字量超出限制。'}
            if len(text.strip())<20:return {'error':'no_extractable_text','message':'未提取到足够文字；扫描版暂不支持，没有 OCR。'}
            return {'text':text,'format':'docx','page_count':pages,'page_count_basis':'metadata and explicit page breaks; no Word layout rendering','scanned_supported':False}
    except (ValueError,KeyError,zipfile.BadZipFile,ET.ParseError,RuntimeError):return {'error':'invalid_docx','message':'DOCX 无法解析，请重新导出。'}
if __name__=='__main__':
    print(json.dumps(extract(sys.stdin.buffer.read(MAX_BYTES+1),sys.argv[1]),ensure_ascii=True))
