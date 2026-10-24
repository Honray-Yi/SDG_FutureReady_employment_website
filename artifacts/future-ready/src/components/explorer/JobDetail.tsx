import { Download } from 'lucide-react';
import type { Job, SemanticMatch, SemanticRanking } from '@workspace/api-client-react';
import { CourseSuggestions } from './CourseSuggestions';
import { useLanguage } from '../../i18n';
import { jobName, jobText } from './jobDisplay';
import { SdgContributions } from './SdgContributions';

export function JobDetail({ job, ranking, match }: { job: Job | null; ranking: SemanticRanking | null; match: SemanticMatch | null }) {
  const { language,t }=useLanguage();
  if (!job) return <div className="empty-state"><h3>{t('Select a role','选择一个职业')}</h3><p>{t('Choose a role to read its description. Analyze your resume to see matching evidence and courses.','选择职业查看介绍；分析简历后可查看匹配依据与推荐课程。')}</p></div>;
  const matched = (match?.keywords ?? []).filter(k => ranking?.matched_keyword_ids?.includes(k.keyword_id));
  const exportJson = () => {
    if (!match) return;
    const blob = new Blob([JSON.stringify(match, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob); const a = document.createElement('a');
    a.href = url; a.download = `semantic-match-${match.input_sha256.slice(0, 8)}.json`; a.click(); URL.revokeObjectURL(url);
  };
  return <div className="role-detail rx-detail">
    <h2>{jobName(job,language)}</h2>
    {ranking ? <div className="comparison"><div><span>{t('Semantic match','语义匹配度')}</span><strong>{ranking.similarity_percent.toFixed(1)}%</strong><small>{t('Raw cosine','原始余弦值')} {ranking.similarity.toFixed(4)}</small></div><div><span>{t('Rank','排名')}</span><strong>{ranking.rank}</strong></div><div><span>{t('Gap from top role','与第一名的差距')}</span><strong>{ranking.relative_difference.toFixed(4)}</strong></div></div>
      : <p className="muted">{t('Catalogue view. Analyze your resume to see how it compares with this description.','职业目录视图，分析简历后可查看与该职业的语义匹配。')}</p>}
    {ranking && <><p className="small muted">{t('Percent = max(0, cosine) × 100, not hiring odds or skill mastery. E5 scores can be high overall; compare ranks and gaps. The 65 scores do not need to sum to 100%.','百分比 = max(0, cosine) × 100，不是录用概率或技能掌握率。E5 分数通常整体偏高，应比较排名和差距；65 个分数不需要加总为 100%。')}</p>
      <h4>{t('Keywords shared with this role','与该职业匹配的关键词')}</h4><div className="keyword-evidence">{matched.map(k=><span className="keyword-chip" key={k.keyword_id} title={k.evidence}>{language==='en'?k.label_en:k.label_zh}</span>)}</div>{!matched.length&&<p className="small muted">{t('No glossary overlap found. The semantic score still reflects the complete text, not a keyword count.','未找到词表交集。语义分数仍来自完整文本，而非关键词数量。')}</p>}</>}
    <h4>{t('Role description','职业介绍')}</h4><p>{jobText(job,language)}</p>
    <SdgContributions contributions={job.sdg_contributions}/>
    {ranking && <CourseSuggestions key={job.job_id} jobId={job.job_id} />}
    {match && <button className="button" onClick={exportJson}><Download size={15} />{t('Export result as JSON','导出 JSON 结果')}</button>}
  </div>;
}
