import { useState } from 'react';
import { ArrowDown, Minus, TrendingUp, TrendingDown } from 'lucide-react';
import { date, signed } from '../api';
import type { Bootstrap, Profile } from '../types';
import { ExternalLink, SdgLinks } from './Shared';

export function SkillsRadar({ data, profile }: { data: Bootstrap; profile?: Profile }) {
  const [filter, setFilter] = useState('all');
  const [descending, setDescending] = useState(true);
  const [selected, setSelected] = useState<string | null>(null);
  const skills = new Map(data.skills.map(s => [s.skill_id, s]));
  const signals = data.signals.filter(s => filter === 'all' || (filter === 'measured' ? s.research_status === 'usable' : s.research_status !== 'usable')).toSorted((a, b) => {
    const av = a.research_share_relative_change, bv = b.research_share_relative_change;
    if (av == null) return bv == null ? 0 : 1;
    if (bv == null) return -1;
    return descending ? bv - av : av - bv;
  });
  const selectedSignal = data.signals.find(s => s.skill_id === selected);
  const windows = data.metadata.research_windows;
  return <section className="radar-panel" aria-labelledby="radar-title"><div className="section-toolbar"><div><h2 id="radar-title">Research attention, in context</h2><p className="muted">Topic-share change across two 90-day windows.</p></div><label className="filter-label">Show<select aria-label="Research signal filter" value={filter} onChange={event => setFilter(event.target.value)}><option value="all">All skills</option><option value="measured">Usable research signals</option><option value="missing">Missing or low-count signals</option></select></label></div>
    <div className="notice"><strong>Research momentum ≠ hiring growth</strong><p>The job column is frequency in a {data.metadata.job_sample_size}-job Europe-oriented snapshot. Malaysia demand is not inferred from this sample.</p></div>
    <div className="radar-table"><div className="radar-table-head"><span>Skill / topic</span><button onClick={() => setDescending(value => !value)} aria-label={`Sort topic-share change ${descending ? 'ascending' : 'descending'}`}>Topic-share change<ArrowDown size={14} style={{ transform: descending ? undefined : 'rotate(180deg)' }} /></button><span>Jobs in sample</span></div>{signals.map(signal => {
      const change = signal.research_share_relative_change;
      const Icon = change == null ? Minus : change > 0 ? TrendingUp : TrendingDown;
      return <button key={signal.skill_id} className={`radar-row ${selected === signal.skill_id ? 'active' : ''}`} onClick={() => setSelected(signal.skill_id)} aria-pressed={selected === signal.skill_id}><span>{skills.get(signal.skill_id)?.label ?? signal.skill_id}<small>{skills.get(signal.skill_id)?.skill_category}{profile && <> · Your level: {profile.skill_levels[signal.skill_id] == null ? 'Unknown' : `${profile.skill_levels[signal.skill_id]}/3`}</>}</small></span><span className={`trend-value ${change == null ? 'unknown' : change > 0 ? 'positive' : 'negative'}`}><Icon size={17} />{change == null ? 'Not measured' : `${signed(change * 100)}%`}{signal.research_status === 'low_count' && <small>Low count</small>}</span><span className="job-count">{signal.job_snapshot_count ?? '—'}<small>of {signal.job_sample_size}</small></span></button>;
    })}</div>
    {selectedSignal && <section className="signal-detail" aria-live="polite"><h3>{skills.get(selectedSignal.skill_id)?.label}</h3><p className="notice">{skills.get(selectedSignal.skill_id)?.measurement_scope} Job counts reflect only the terms observed in the retained snapshot; unmeasured is not zero.</p><p>Research papers matching the topic: {selectedSignal.research_previous_count ?? 'not measured'} → {selectedSignal.research_current_count ?? 'not measured'}. Relative topic-share change accounts for the total research volume in each window.</p><p className="small">Raw count change: {selectedSignal.research_growth_pct == null ? 'not measured' : `${signed(selectedSignal.research_growth_pct)}%`}. Keyword overlap, indexing delays and seasonality can affect these observations. No causal explanation is established.</p><div className="source-links">{(selectedSignal.source_urls ?? []).map((url, i) => <ExternalLink key={url} href={url}>Research query {i + 1}</ExternalLink>)}</div><details><summary>Skill SDG mapping</summary><SdgLinks items={skills.get(selectedSignal.skill_id)?.sdg_mappings ?? []} /></details></section>}
    <p className="small muted">Previous window: {date(windows.previous.window_start)} – {date(windows.previous.window_end_exclusive)} (end exclusive). Current: {date(windows.current.window_start)} – {date(windows.current.window_end_exclusive)} (end exclusive). Research retrieved {date(data.metadata.research_retrieved_at)}.</p>
  </section>;
}
