import type { SemanticRanking } from '@workspace/api-client-react';
import { useLanguage } from '../../i18n';
import { jobName, jobText } from './jobDisplay';
import { SdgBadges } from './SdgContributions';

export function Rankings({ rankings, selectedId, onSelect }: { rankings: SemanticRanking[]; selectedId: string | null; onSelect: (id: string) => void }) {
  const { language,t }=useLanguage();
  return <div className="role-list rx-rank-list">{rankings.map(r => <button key={r.job_id} className={`role-row ${selectedId === r.job_id ? 'selected' : ''}`} aria-pressed={selectedId === r.job_id} onClick={() => onSelect(r.job_id)}>
    <span className="rank">{String(r.rank).padStart(2, '0')}</span>
    <span className="role-copy"><strong>{jobName(r,language)}</strong><span>{jobText(r,language).slice(0, 100)}…</span><SdgBadges contributions={r.sdg_contributions}/></span>
    <span className="role-score"><strong>{r.similarity_percent.toFixed(1)}%</strong><small>{t('Semantic match','语义匹配度')}</small></span>
  </button>)}</div>;
}
