import { ExternalLink, RefreshCw } from 'lucide-react';
import { useGetJobCourses } from '@workspace/api-client-react';
import { errorMessage } from './errors';
import { useLanguage } from '../../i18n';

export function CourseSuggestions({ jobId }: { jobId: string }) {
  const { language,t }=useLanguage();
  const query = useGetJobCourses(jobId,{language});
  return <section className="rx-courses" aria-label={t('Recommended learning courses','推荐学习课程')}>
    <h3>{t('Recommended learning courses','推荐学习课程')}</h3>
    {query.isLoading ? <p role="status">{t('Loading courses for this role…','正在读取该职业的课程…')}</p>
      : query.isError ? <div className="notice" role="alert"><p>{errorMessage(query.error,language)}</p><button className="button" onClick={() => void query.refetch()}><RefreshCw size={14} />{t('Retry courses','重试课程')}</button></div>
        : query.data && <>
          <p className="small muted">{query.data.basis}</p>
          {!query.data.courses.length && <p>{t('No source-reviewed course is available for this role. Unrelated placeholders are not substituted.','暂没有符合来源审核条件的课程，不会显示无关课程作为占位。')}</p>}
          {query.data.courses.map(c => <article className="rx-course" key={c.course_id}>
            <span className="small muted">{c.provider} · {c.level}</span>
            <h4><a href={c.url} target="_blank" rel="noopener noreferrer" referrerPolicy="no-referrer">{c.title}<ExternalLink size={14} aria-label={t('Open provider in a new tab','在新标签页打开课程官网')} /></a></h4>
            <p><strong>{c.topic}</strong> — {c.reason}</p>
            <p className="small muted">{t('Matched role topic: ','对应职业主题：')}{c.job_evidence}</p>
            <p className="small muted">{language==='en'?`${c.access} ${c.cost_note}`:'公开学习内容可访问；证书、云算力或实验可能另收费，请在官网确认。'}</p>
            <a className="text-button" href={c.source_url} target="_blank" rel="noopener noreferrer" referrerPolicy="no-referrer">{t('Provider source · Checked','课程来源 · 核验日期')} {c.checked_at.slice(0, 10)}</a>
          </article>)}
          <p className="small muted">{query.data.coverage_note}</p>
        </>}
  </section>;
}
