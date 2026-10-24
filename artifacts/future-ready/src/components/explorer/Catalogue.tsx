import { useMemo, useState } from 'react';
import { Search } from 'lucide-react';
import type { Job } from '@workspace/api-client-react';
import { useLanguage } from '../../i18n';
import { jobName, jobText } from './jobDisplay';
import { SdgBadges } from './SdgContributions';

export function Catalogue({ jobs, selectedId, onSelect }: { jobs: Job[]; selectedId: string | null; onSelect: (id: string) => void }) {
  const { language, t } = useLanguage();
  const [q, setQ] = useState('');
  const shown = useMemo(() => { const s = q.trim().toLowerCase(); return s ? jobs.filter(j => [j.job_name, j.job_text, j.job_name_en, j.job_text_en].some(v => v?.toLowerCase().includes(s))) : jobs; }, [jobs, q]);
  return <div className="rx-catalogue">
    <div className="search-field"><Search size={16} aria-hidden /><input aria-label={t('Search the job catalogue','搜索职业目录')} placeholder={t(`Search ${jobs.length} roles in English or Chinese`, `搜索 ${jobs.length} 个职业，支持中英文`)} value={q} onChange={e => setQ(e.target.value)} />{q && <button className="clear-search" aria-label={t('Clear search','清除搜索')} onClick={() => setQ('')}>×</button>}</div>
    <p className="muted small" role="status">{t(`${shown.length} of ${jobs.length} roles. Run an analysis to see match scores.`, `显示 ${shown.length} / ${jobs.length} 个职业，分析后可查看匹配分数。`)}</p>
    {shown.length === 0 ? <div className="empty-state"><h3>{t(`No role matches “${q}”`, `没有匹配“${q}”的职业`)}</h3><p>{t('Try a shorter or different word.','请尝试更短或其他关键词。')}</p></div> :
      <div className="role-list">{shown.map(j => <button key={j.job_id} className={`role-row rx-row ${selectedId === j.job_id ? 'selected' : ''}`} aria-pressed={selectedId === j.job_id} onClick={() => onSelect(j.job_id)}><span className="rank" /><span className="role-copy"><strong>{jobName(j,language)}</strong><span>{jobText(j,language).slice(0, 110)}…</span><SdgBadges contributions={j.sdg_contributions}/></span></button>)}</div>}
  </div>;
}
