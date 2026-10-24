import type { Language } from '../../i18n';
const messages: Record<string,[string,string]> = {
  consent_required: ['Confirm authorization before uploading or analyzing a resume.','请先确认简历处理授权。'],
  unsupported_type: ['Only text-based PDF and DOCX files are supported.','只支持文字版 PDF 和 DOCX。'],
  file_too_large: ['The file must be 8 MB or smaller.','文件不能超过 8 MB。'],
  invalid_docx: ['This is not a readable DOCX file. Export it again from Word or use a text-based PDF.','不是有效 DOCX，请重新导出或使用文字版 PDF。'],
  invalid_pdf: ['This PDF could not be read. Export a new text-based PDF and try again.','PDF 无法解析，请重新导出文字版 PDF。'],
  no_extractable_text: ['Not enough text could be extracted. Scanned documents need OCR before upload.','未提取到足够文字，扫描件需要先进行 OCR。'],
  pdf_no_text: ['No readable text was found. Scanned documents need OCR before upload.','没有可读取文字，扫描件需要先进行 OCR。'],
  too_many_pages: ['The PDF must contain no more than 20 pages.','PDF 不能超过 20 页。'],
  too_many_characters: ['The extracted text exceeds 100,000 characters. Use a shorter document.','提取文本超过 100,000 字符，请缩短文档。'],
  too_many_tokens: ['The resume exceeds the 12,000-token limit. Shorten it and try again.','简历超过 12,000 token，请缩短后重试。'],
  docx_expansion_limit: ['The expanded DOCX is too large or unusually compressed. Export a simpler document.','DOCX 解压内容过大或压缩比异常，请重新导出更简单的文档。'],
  model_missing: ['Local model files are missing. Ask the site owner to restore them.','本地模型文件缺失，请联系站点维护者恢复。'],
  cache_invalid: ['The job index is incompatible. The site owner needs to rebuild it.','职业索引不兼容，需要站点维护者重建。'],
  catalogue_invalid: ['The career catalogue is unavailable. Please retry later.','职业目录暂不可用，请稍后重试。'],
  analysis_limit: ['The server’s hourly analysis limit has been reached. Please try again later.','已达到服务器每小时分析限额，请稍后重试。'],
  busy: ['The server is processing other resumes. Please try again shortly.','服务器正在处理其他简历，请稍后重试。'],
  model_unavailable: ['The local model could not run. Please try again later.','本地模型暂时无法推理，请稍后重试。'],
  local_inference_failed: ['Local inference could not finish. Please try again later.','本地推理未能完成，请稍后重试。'],
  courses_unavailable: ['Courses are temporarily unavailable. Retry courses without rerunning your resume analysis.','课程暂不可用，可单独重试，不必重新分析简历。'],
  document_failed: ['The document could not be processed. Check the format, authorization and file limits, then retry.','无法处理文档，请检查格式、授权与文件限制后重试。'],
};
export function errorMessage(e: unknown, language: Language='en'): string {
  const detail = (e as { data?: { detail?: unknown } } | null)?.data?.detail;
  const code = detail && typeof detail==='object' ? (detail as {code?:string}).code : undefined;
  const local = e instanceof Error ? e.message : '';
  const known = messages[code ?? local];
  if(known)return known[language==='en'?0:1];
  const message = typeof detail==='string' ? detail : detail && typeof detail==='object' ? (detail as {message?:string}).message : local;
  if(message && ((language==='en'&&!/[\u3400-\u9fff]/.test(message)) || (language==='zh'&&/[\u3400-\u9fff]/.test(message))))return message;
  return language==='en'?'The request could not be completed. Check your input and try again.':'请求未能完成，请检查输入后重试。';
}
