import type { SdgContribution } from '@workspace/api-client-react';
import { useLanguage } from '../../i18n';

export function SdgBadges({ contributions = [] }: { contributions?: SdgContribution[] }) {
  const { language, t } = useLanguage();
  return <span className="sdg-badges" aria-label={t('Potential SDG contributions', '潜在 SDG 贡献')}>
    {[...new Map(contributions.map(c => [c.goal,c])).values()].map(c =>
      <span key={c.goal} className="sdg-badge" title={`SDG ${c.goal}: ${language === 'en' ? c.title_en : c.title_zh}`}>SDG {c.goal} · {language === 'en' ? c.title_en : c.title_zh}</span>)}
  </span>;
}

export function SdgContributions({ contributions = [] }: { contributions?: SdgContribution[] }) {
  const { language, t } = useLanguage();
  return <section className="sdg-section" aria-label={t('Potential SDG contributions','潜在 SDG 贡献')}>
    <h3>{t('Potential SDG contributions','潜在 SDG 贡献')}</h3>
    <p className="small muted">{t('Curated alignment with UN Sustainable Development Goals, not UN endorsement or measured impact. Contribution depends on how the work is applied.','基于联合国可持续发展目标的人工参考映射，不代表联合国认证或已测量的影响；实际贡献取决于应用方式。')}</p>
    {contributions.map(c => <article className="sdg-card" key={`${c.goal}-${c.target}`}>
      <a href={c.url} target="_blank" rel="noreferrer">SDG {c.goal} · {language === 'en' ? c.title_en : c.title_zh} ↗</a>
      <p>{language === 'en' ? c.reason_en : c.reason_zh}</p>
      <small>{t('UN target','联合国子目标')} {c.target}</small>
    </article>)}
    {!contributions.length && <p className="small muted">{t('No reviewed mapping is available for this role.','该职业暂无已复核的目标映射。')}</p>}
  </section>;
}
