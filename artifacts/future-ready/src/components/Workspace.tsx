import { ArrowRight, Search } from 'lucide-react';
import { useState } from 'react';
import { date, fixed, signed } from '../api';
import type { Bootstrap, Match, Role, Skill } from '../types';
import { ExternalLink, SdgLinks } from './Shared';

function ScoreBar({ label, value }: { label: string; value: number }) {
  return <div className="score-bar"><span>{label}</span><div className="bar-track"><span style={{ width: `${value}%` }} /></div><span>{fixed(value)}</span></div>;
}

function Explanation({ role, data }: { role: Role; data: Bootstrap }) {
  const skillById = new Map(data.skills.map(s => [s.skill_id, s.label]));
  return <details className="explanation"><summary className="button">Why this match?<ArrowRight size={17} /></summary><div className="explanation-body">
    <h3>Signals contribute {Math.round(role.signal_weight * 100)}% of this index</h3>
    <p>The rest comes from weighted coverage of the role’s required skill levels. The signal component combines 70% research momentum and 30% prevalence in the job sample.</p>
    <div className="comparison"><div><span>Neutral research</span><strong>{fixed(role.comparison.neutral_score)}</strong><small>Rank {role.comparison.neutral_rank}</small></div><ArrowRight size={20} aria-hidden="true" /><div><span>Observed research</span><strong>{fixed(role.score)}</strong><small>Rank {role.rank}</small></div></div>
    <p><strong>{signed(role.comparison.score_change)} index points</strong> when measured research momentum replaces a neutral value. The profile and job sample stay fixed. This is a model comparison, not a second market snapshot.</p>
    <h4>Evidence used for this direction</h4><ul>{role.signal_evidence.map(s => <li key={s.skill_id}>{skillById.get(s.skill_id) ?? s.skill_id}: {s.research_status === 'usable' ? 'measured research momentum' : 'neutral research baseline (missing or low count)'}</li>)}</ul>
    <p className="small">Research momentum is 0.5 + half of relative topic-share change, clipped to −1…1. Missing evidence uses a neutral value. Negative research trends are preserved; they do not establish falling hiring demand.</p>
  </div></details>;
}

export function Workspace({ data, result, role, selectRole, onPath, onSources }: { data: Bootstrap; result: Match; role: Role; selectRole: (id: string) => void; onPath: () => void; onSources: () => void }) {
  const [search, setSearch] = useState('');
  const filtered = result.roles.filter(r => `${r.title} ${r.focus_label}`.toLowerCase().includes(search.toLowerCase().trim()));
  const skillById = new Map<string, Skill>(data.skills.map(s => [s.skill_id, s]));
  const path = result.pathways[role.role_id];
  const gaps = role.skills_gap.filter(s => s.gap !== null && s.gap > 0);
  return <div className="workspace-columns">
    <section className="role-browser" aria-labelledby="roles-title"><h2 id="roles-title">Explore roles</h2><p className="muted">{result.roles.length} evidence-linked directions</p>
      <div className="search-field"><Search size={18} aria-hidden="true" /><input aria-label="Find a role" placeholder="Find a role" value={search} onChange={event => setSearch(event.target.value)} />{search && <button className="clear-search" onClick={() => setSearch('')} aria-label="Clear role search">×</button>}</div>
      <div className="role-list" aria-label="Ranked roles">{filtered.length ? filtered.map(r => <button key={r.role_id} className={`role-row ${role.role_id === r.role_id ? 'selected' : ''}`} aria-pressed={role.role_id === r.role_id} onClick={() => selectRole(r.role_id)}><span className="rank">{String(r.rank).padStart(2, '0')}</span><span className="role-copy"><strong>{r.title}</strong><span>{r.focus_label}</span></span><span className="role-score"><strong>{fixed(r.score)}</strong><small>match index</small></span></button>) : <div className="empty-state"><h3>No matching roles</h3><p>Try “data”, “systems” or “AI”.</p><button className="text-button" onClick={() => setSearch('')}>Clear search</button></div>}</div>
    </section>
    <section className="role-detail" aria-labelledby="role-title"><h2 id="role-title">{role.title}</h2><p className="role-focus">{role.focus_label}</p>
      <div className="score-heading"><div className="score-ring" style={{ background: `conic-gradient(var(--teal) ${role.score}%, var(--border) 0)` }}><div><strong data-testid="match-score">{fixed(role.score)}</strong><span>/100</span></div></div><div><h3>Provisional match index</h3><p>Lower bound {fixed(role.score)}–{fixed(role.score_upper_bound)} · {fixed(role.assessment_coverage)}% assessed within mapped requirements. Not a hiring probability.</p></div></div>
      <div className="score-bars"><ScoreBar label="Skill alignment" value={role.skill_fit} /><ScoreBar label="Research momentum" value={role.research_component} /><ScoreBar label="Job sample signal" value={role.job_sample_component} /></div>
      <Explanation role={role} data={data} />
      <section className="gap-section"><h3>Your next skills</h3>{role.unknown_skill_ids.length > 0 && <p className="notice">Confirm first: {role.unknown_skill_ids.map(id => skillById.get(id)?.label ?? id).join(", ")}. Unknown is not zero; no course gap is inferred.</p>}{gaps.length ? <ul className="gap-list">{gaps.map(gap => <li key={gap.skill_id}><span>{skillById.get(gap.skill_id)?.label ?? gap.skill_id}</span><span className="gap-level">{gap.current_level}<ArrowRight size={14} aria-hidden="true" />{gap.target_level}<span className="sr-only"> on a 0 to 3 scale</span></span><span className="gap-markers" aria-hidden="true">{[1, 2, 3].map(n => <i key={n} className={gap.current_level !== null && n <= gap.current_level ? 'have' : n <= gap.target_level ? 'need' : ''} />)}</span></li>)}</ul> : <p>No confirmed skill gaps. Unknown requirements still need assessment.</p>}<p className="small muted">Current → target level · 0–3 scale</p></section>
      <div className="path-preview"><div><h3>A learning path, step by step</h3><p>{path.steps.length} resources · {path.estimated_course_hours} hours · about {path.estimated_course_weeks} weeks</p></div><button className="button primary" onClick={onPath}>View learning path<ArrowRight size={16} /></button></div>
      <details className="context-details"><summary>Role context & sustainable development</summary><div><p>{role.eligibility_note}</p>{role.unmapped_requirements.length > 0 && <p className="notice">Outside the Module 1 taxonomy: {role.unmapped_requirements.map(r => r.skill_id).join(", ")}. These requirements are excluded from the index and still need separate assessment.</p>}<ExternalLink href={role.role_source}>Official occupation reference (O*NET)</ExternalLink><p className="small">The AI focus and required skill levels are team-curated. The occupational title is a US taxonomy reference.</p><p>Malaysia crosswalk: {role.malaysia_reference_codes.join(', ') || 'Not mapped'}. {role.is_mycol_critical === true ? 'Mapped to a MyCOL 2024/25 critical group.' : role.is_mycol_critical === false ? 'Mapped group is not on the MyCOL 2024/25 critical list.' : 'Critical status is not established for this exact role.'} This is an approximate crosswalk, not a count of vacancies.</p><SdgLinks items={role.sdg_mappings} /><h4>Skill-level SDG rationale</h4>{gaps.map(gap => <details key={gap.skill_id}><summary>{skillById.get(gap.skill_id)?.label}</summary><SdgLinks items={skillById.get(gap.skill_id)?.sdg_mappings ?? []} /></details>)}</div></details>
      <footer className="evidence-footer"><span>Research collected {date(result.metadata.research_retrieved_at)} · Cached observations</span><button className="text-button" onClick={onSources}>Review the evidence<ArrowRight size={14} /></button></footer>
    </section>
  </div>;
}
