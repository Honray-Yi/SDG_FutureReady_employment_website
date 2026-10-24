"""Bounded subprocess PDF extraction; no application-level disk writes."""
import io,json,sys
from pypdf import PdfReader

def extract(raw):
    if not raw.startswith(b'%PDF-'):return {'error':'invalid_pdf','message':'文件不是有效的PDF。'}
    try:
        reader=PdfReader(io.BytesIO(raw),strict=False)
        if reader.is_encrypted:return {'error':'encrypted_pdf','message':'暂不支持加密PDF，请先解密或使用表单。'}
        if len(reader.pages)>20:return {'error':'too_many_pages','message':'最多支持20页PDF。'}
        pages=[]; total=0
        for page in reader.pages:
            text=page.extract_text() or '';total+=len(text)
            if total>100000:return {'error':'too_much_text','message':'PDF文字量超出处理限制，请只保留简历页面。'}
            pages.append(text)
        if sum(len(t.strip()) for t in pages)<20:
            return {'error':'no_extractable_text','message':'没有提取到足够文字。可能是扫描件；本版不含OCR，请使用可选中文字的PDF或手动表单。'}
        return {'pages':pages,'page_count':len(pages),'characters':total}
    except Exception:
        return {'error':'invalid_pdf','message':'PDF无法解析。请重新导出PDF或使用表单。'}

if __name__=='__main__':
    # Resource limits supported on Unix; Windows still has parent timeout.
    try:
        import resource
        resource.setrlimit(resource.RLIMIT_CPU,(12,12))
    except (ImportError,ValueError,OSError):pass
    # ASCII JSON is UTF-8-compatible even when Windows defaults stdout to GBK.
    print(json.dumps(extract(sys.stdin.buffer.read(8*1024*1024+1)),ensure_ascii=True))
