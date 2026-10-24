import { useEffect, useMemo, useRef, useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { ArrowRight, LoaderCircle, RefreshCw, ShieldCheck, Trash2, Upload } from 'lucide-react';
import { createSemanticMatch, getGetExplorerStatusQueryKey, useCreateSemanticMatch, useGetExplorerDemos, useGetExplorerJobs, useGetExplorerStatus } from '@workspace/api-client-react';
import type { ExtractedDocument, SemanticMatch } from '@workspace/api-client-react';
import { Catalogue } from './explorer/Catalogue';
import { Rankings } from './explorer/Rankings';
import { JobDetail } from './explorer/JobDetail';
import { errorMessage } from './explorer/errors';
import { samples } from './explorer/samples';
import { savedLanguage, saveLanguage, useLanguage, type Language } from '../i18n';
import './resume-explorer.css';

const MAX = 100000, MAX_BYTES = 8 * 1024 * 1024;
const MIME = { pdf: 'application/pdf', docx: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' } as const;
type Notice = { file: string; pages: number; chars: number } | { sample: string } | null;

export function ResumeExplorer() {
  const { language, t } = useLanguage();
  const qc = useQueryClient();
  const status = useGetExplorerStatus(), jobsQ = useGetExplorerJobs(), demosQ = useGetExplorerDemos();
  const [keywordLanguage, setKeywordLanguage] = useState<Language>(() => savedLanguage('fr-keyword-language'));
  const matchCtrl = useRef<AbortController | null>(null);
  const mutation = useCreateSemanticMatch({ mutation: { mutationFn: ({ data }) => {
    const controller = new AbortController(); matchCtrl.current = controller;
    return createSemanticMatch(data, { signal: controller.signal });
  } } });
  const [text, setText] = useState(''), [synthetic, setSynthetic] = useState(false), [consent, setConsent] = useState(false);
  const [result, setResult] = useState<SemanticMatch | null>(null), [selectedId, setSelectedId] = useState<string | null>(null);
  const [tab, setTab] = useState<'results' | 'catalogue'>('catalogue');
  const [note, setNote] = useState<Notice>(null), [error, setError] = useState<unknown>(null), [extracting, setExtracting] = useState(false);
  const serial = useRef(0), upCtrl = useRef<AbortController | null>(null);
  useEffect(() => () => { serial.current++; upCtrl.current?.abort(); matchCtrl.current?.abort(); }, []);
  const st = status.data, jobs = jobsQ.data?.jobs ?? [];
  const jobById = useMemo(() => new Map(jobs.map(j => [j.job_id, j])), [jobs]);
  const selectedJob = selectedId ? jobById.get(selectedId) ?? null : null;
  const selectedRank = result?.rankings.find(r => r.job_id === selectedId) ?? null;
  const busy = mutation.isPending, tooShort = text.trim().length < 20;
  const canRun = consent && !tooShort && !busy && !extracting && !!st && st.model_ready && (st.state === 'ready' || st.state === 'awaiting_index') && text.length <= MAX;
  function reset() {
    serial.current++; matchCtrl.current?.abort(); upCtrl.current?.abort(); mutation.reset();
    setResult(null); setSelectedId(null); setError(null); setExtracting(false);
  }
  function edit(next: string, notice: Notice = null) { reset(); setText(next.slice(0, MAX)); setNote(notice); if (!next) setTab('catalogue'); }
  function analyze() {
    if (!canRun) return;
    const id = ++serial.current; setError(null);
    mutation.mutate({ data: { text, is_synthetic: synthetic, processing_consent: consent, keyword_language: keywordLanguage, top_k: 65 } }, {
      onSuccess: m => { if (id !== serial.current) return; setResult(m); setSelectedId(m.rankings[0]?.job_id ?? null); setTab('results'); void qc.invalidateQueries({ queryKey: getGetExplorerStatusQueryKey() }); },
      onError: e => { if (id === serial.current && (e as Error).name !== 'AbortError') setError(e); },
    });
  }
  async function upload(file?: File) {
    if (!file) return;
    if (!consent) { setError(new Error('consent_required')); return; }
    reset(); setText(''); setNote(null); setSynthetic(false);
    const ext = file.name.split('.').pop()?.toLowerCase();
    if (ext !== 'pdf' && ext !== 'docx') { setError(new Error('unsupported_type')); return; }
    if (file.size > MAX_BYTES) { setError(new Error('file_too_large')); return; }
    const id = serial.current; const c = new AbortController(); upCtrl.current = c; setExtracting(true);
    try {
      const res = await fetch('/api/explorer/upload', { method: 'POST', signal: c.signal, credentials: 'include', headers: { 'Content-Type': MIME[ext], 'X-Processing-Consent': 'true', 'X-Document-Format': ext }, body: file });
      const body: unknown = await res.json().catch(() => null);
      if (!res.ok) throw Object.assign(new Error('document_failed'), { data: body });
      if (id !== serial.current) return;
      const doc = (body as ExtractedDocument).document;
      if (doc.text.length > MAX) throw new Error('too_many_characters');
      setText(doc.text); setNote({ file: file.name, pages: doc.page_count, chars: doc.text.length });
    } catch (e) { if (id === serial.current && (e as Error).name !== 'AbortError') setError(e); }
    finally { if (id === serial.current) setExtracting(false); }
  }
  const stateTitle = st?.state === 'model_missing' ? t('Local model needs setup', '需要配置本地模型') : st?.state === 'awaiting_index' ? t('First analysis builds the local index', '首次分析将建立本地索引') : st?.state === 'cache_invalid' ? t('Index needs a manual rebuild', '需要手动重建索引') : t('Catalogue unavailable', '职业目录不可用');
  return <section className="explorer" aria-label={t('Resume and career explorer', '简历与职业探索')}>
    <div className="rx-top notice"><strong>{t('Resume → Career matches → Learning resources · No API key needed', '简历 → 职业匹配 → 推荐课程 · 无需 API 密钥')}</strong><p>{t(`Compare your experience with ${st?.occupation_count ?? 65} roles using a multilingual model on this app's server. Matching percentages are semantic similarity, not hiring probabilities.`, `使用本应用后端的多语言模型，对比 ${st?.occupation_count ?? 65} 个职业。匹配百分比是语义相似度，不是录用概率。`)}</p></div>
    {status.isError ? <div className="error-state"><h2>{t('Status unavailable', '状态不可用')}</h2><p>{errorMessage(status.error, language)}</p><button className="button" onClick={() => void status.refetch()}>{t('Retry', '重试')}</button></div>
      : status.isLoading ? <div className="loading-state"><div className="spinner" /></div>
        : st && st.state !== 'ready' && <div className="notice" role="status"><strong>{stateTitle}</strong><p>{st.state === 'awaiting_index' ? t('The first request may take longer. All model inference is local to this server.', '首次请求可能较慢，所有模型推理都在本应用后端进行。') : t('Ask the site owner to restore the catalogue or model files, or explicitly rebuild an incompatible index. No remote fallback is used.', '请站点维护者恢复职业目录、模型文件或显式重建不兼容索引；不会静默切换远程服务。')}</p><button className="button" onClick={() => void status.refetch()} disabled={status.isFetching}><RefreshCw size={15}/>{t('Refresh status', '刷新状态')}</button></div>}
    <div className="app-layout rx-layout">
      <aside className="profile-panel rx-input">
        <h2>{t('1. Upload and review', '1. 上传并检查简历')}</h2>
        <p className="small muted">{t('Remove contact details you do not need to share. Files, extracted text and resume vectors are processed temporarily, not saved.', '建议去除不必分享的联系方式。原文件、提取文本和简历向量只用于临时处理，不持久保存。')}</p>
        <label className="radio-row rx-check"><input type="checkbox" checked={consent} onChange={e => { setConsent(e.target.checked); reset(); }}/>{t('I am authorized to use this resume and agree to temporary processing on this app’s server. No text is sent to an external analysis service.', '我有权处理此简历，并同意本应用后端临时解析及分析；不会发送给外部分析服务。')}</label>
        <label className="keyword-language" htmlFor="keyword-language"><strong>{t('Keyword recognition', '关键词识别语言')}</strong><select id="keyword-language" value={keywordLanguage} onChange={e => { const v = e.target.value as Language; setKeywordLanguage(v); saveLanguage('fr-keyword-language', v); edit(text); }}><option value="en">{t('English keywords', '英文关键词')}</option><option value="zh">{t('Chinese keywords', '中文关键词')}</option></select></label>
        <p className="small muted">{t('This selects the keyword glossary, not the interface language. Semantic matching remains multilingual. Change it before running a new analysis.', '此选项控制关键词词表，不控制界面语言。语义匹配始终支持多语言；更改后请重新分析。')}</p>
        <p className="field-label">{t('Try a synthetic sample', '加载合成示例')}</p>
        <div className="rx-demos">{demosQ.isLoading ? <span className="muted small">{t('Loading samples…', '正在加载示例…')}</span> : demosQ.isError ? <button className="text-button" onClick={() => void demosQ.refetch()}>{t('Retry samples', '重试示例')}</button> : (demosQ.data?.profiles ?? []).map(d => {
          const sample = samples[d.profile_id]; if (!sample) return null;
          return <button key={d.profile_id} className="button" onClick={() => { edit(keywordLanguage === 'en' ? sample.textEn : sample.textZh, { sample: d.profile_id }); setSynthetic(true); }}>{t(sample.en, sample.zh)}</button>;
        })}</div>
        <label className={`rx-upload ${extracting ? 'busy' : ''}`}>{extracting ? <LoaderCircle className="rx-spin" size={20}/> : <Upload size={20}/>}<strong>{extracting ? t('Extracting resume text…', '正在提取简历文本…') : t('Upload PDF / DOCX resume', '上传简历 PDF / DOCX')}</strong><span>{t('Up to 8 MB. Confirm authorization first. Text-based PDFs only; scanned documents need OCR before upload.', '最多 8 MB，请先确认授权。支持文字版 PDF；扫描件须先转为可复制文本。')}</span><input aria-label={t('Upload PDF or DOCX resume', '上传简历 PDF 或 DOCX')} className="sr-only" type="file" accept=".pdf,.docx" disabled={!consent || extracting || busy} onChange={e => { void upload(e.target.files?.[0]); e.target.value = ''; }}/></label>
        <label htmlFor="rx-text">{t('Text to analyze', '待分析文本')} ({text.length.toLocaleString()} / {MAX.toLocaleString()})</label>
        <textarea id="rx-text" rows={9} maxLength={MAX} value={text} onChange={e => { setSynthetic(false); edit(e.target.value); }} placeholder={t('Paste experience text, or upload a resume and review it here (at least 20 characters).', '粘贴经历，或上传后检查提取文本（至少 20 字符）。')}/>
        {note && <p className="small muted" role="status">{'file' in note ? t(`Extracted ${note.pages} page(s), ${note.chars.toLocaleString()} characters from ${note.file}. Review the text, then analyze.`, `已从 ${note.file} 提取 ${note.pages} 页、${note.chars.toLocaleString()} 字符，请检查后分析。`) : t(`Loaded synthetic sample: ${samples[note.sample].en}.`, `已加载合成示例：${samples[note.sample].zh}。`)}</p>}
        <button className="button primary rx-go" disabled={!canRun} onClick={analyze}>{busy ? <><LoaderCircle className="rx-spin" size={16}/>{t('Analyzing career matches…', '正在计算职业匹配…')}</> : <>{t('2. Analyze resume', '2. 分析简历')}<ArrowRight size={16}/></>}</button>
        {text && <button className="text-button" onClick={() => { edit(''); setSynthetic(false); }}><Trash2 size={13}/>{t('Clear text and results', '清除文本与结果')}</button>}
        {!!error && <p role="alert" className="rx-error">{errorMessage(error, language)}</p>}
        <p className="profile-note">{t('Local multilingual E5 · 384 dimensions. Long text is chunked, pooled and compared by cosine similarity. Server resource limits apply.', '后端本地多语言 E5 · 384 维。长文本分块聚合后计算余弦相似度；受服务器资源限额约束。')}</p>
      </aside>
      <div className="main-surface rx-main">
        <div className="rx-tabs" role="tablist"><button role="tab" aria-selected={tab === 'results'} className={tab === 'results' ? 'active' : ''} disabled={!result} onClick={() => setTab('results')}>{t('Ranked results', '职业排名')}</button><button role="tab" aria-selected={tab === 'catalogue'} className={tab === 'catalogue' ? 'active' : ''} onClick={() => setTab('catalogue')}>{t('Job catalogue', '职业目录')} ({jobs.length || 65})</button></div>
        {result && <section className="notice" aria-label={t('Recognized keywords', '已识别关键词')}><strong>{t('Recognized keywords', '已识别关键词')} · {result.keyword_language === 'en' ? t('English', '英文') : t('Chinese', '中文')}</strong><div className="keyword-evidence">{result.keywords.map(k => <span className="keyword-chip" key={k.keyword_id} title={k.evidence}>{language === 'en' ? k.label_en : k.label_zh}</span>)}</div><p className="small muted">{result.keywords.length ? t('Found in your text using the selected glossary. Keyword presence is not proof of proficiency and does not change semantic scores.', '根据所选词表在原文中找到。关键词出现不证明技能熟练度，也不会改变语义分数。') : t('No supported keywords found in this glossary. Semantic results still work; select the other keyword language if appropriate.', '该词表未识别到支持的关键词，语义匹配仍有效；如有需要可切换识别语言。')}</p></section>}
        {tab === 'results' && result && <p className="small muted rx-meta" role="status">{t(`${result.rankings.length} roles ranked · ${result.input_tokens} tokens · ${result.chunk_count} chunk(s)`, `${result.rankings.length} 个职业已排序 · ${result.input_tokens} token · ${result.chunk_count} 个分块`)}</p>}
        {busy && <p className="rx-progress" role="status"><LoaderCircle className="rx-spin" size={15}/>{t('Analyzing on this app’s server…', '正在本应用后端进行分析…')}</p>}
        {jobsQ.isError ? <div className="error-state"><h2>{t('Catalogue unavailable', '职业目录不可用')}</h2><p>{errorMessage(jobsQ.error, language)}</p><button className="button" onClick={() => void jobsQ.refetch()}>{t('Retry', '重试')}</button></div> : jobsQ.isLoading ? <div className="loading-state"><div className="spinner"/></div> : <div className="workspace-columns"><div className="role-browser">{tab === 'results' && result ? <Rankings rankings={result.rankings} selectedId={selectedId} onSelect={setSelectedId}/> : <Catalogue jobs={jobs} selectedId={selectedId} onSelect={setSelectedId}/>}</div><JobDetail job={selectedJob ?? selectedRank} ranking={tab === 'results' ? selectedRank : null} match={tab === 'results' ? result : null}/></div>}
        <details className="context-details" open><summary><ShieldCheck size={15}/>{t('Privacy and interpretation', '隐私与结果解释')}</summary><p>{t('Processing stays on this app’s server. Resume files, text and vectors are not persistently stored or sent to external analysis APIs. Model assets are downloaded only during setup.', '解析、分词和推理都在本应用后端进行。原文件、简历文本和向量不持久保存，也不发送给外部分析 API。模型文件只在安装时下载。')}</p><p>{t('Percent = max(0, cosine) × 100. This is not a hiring probability or a skill assessment. E5 scores can be high overall; compare rankings and gaps. Keywords only explain supported text overlap.', '百分比 = max(0, cosine) × 100，不是录用概率或技能评估。E5 分数通常整体偏高，应比较排名和差距。关键词仅解释可识别的文本交集。')}</p><p>{t('The catalogue contains 65 user-provided role descriptions, not live vacancies. English descriptions are display summaries; canonical multilingual embedding documents and scores are unchanged. Courses cover selected foundations, not every specialist skill.', '目录包含用户提供的 65 个职业描述，不是实时职位。英文介绍是展示摘要，不改变原始向量文档和分数。课程覆盖部分基础内容，并非全部专科技能。')}</p></details>
      </div>
    </div>
  </section>;
}
