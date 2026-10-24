import { ChevronDown } from 'lucide-react';
import type { Bootstrap, Profile } from '../types';
import { LevelDots } from './Shared';

export function ProfilePanel({ data, profile, scenario, hours, onProfile, onScenario, onHours }: { data: Bootstrap; profile: Profile; scenario: string; hours: number; onProfile: (id: string) => void; onScenario: (id: string) => void; onHours: (hours: number) => void }) {
  const skillById = new Map(data.skills.map(skill => [skill.skill_id, skill]));
  const weight = data.scenarios.find(s => s.scenario_id === scenario)?.signal_weight ?? 0;
  const hourOptions = [...new Set([4, 5, 6, 8, 10, 15, 20, hours])].sort((a, b) => a - b);
  return <aside className="profile-panel" aria-label="Synthetic profile controls"><details open>
    <summary><h2>Your starting point</h2><ChevronDown size={18} /></summary>
    <div className="profile-body">
      <label htmlFor="profile">Synthetic demo profile</label>
      <select id="profile" value={profile.profile_id} onChange={event => onProfile(event.target.value)}>{!data.profiles.some(p => p.profile_id === profile.profile_id) && <option value={profile.profile_id}>{profile.current_role} · imported</option>}{data.profiles.map(p => <option key={p.profile_id} value={p.profile_id}>{p.current_role}</option>)}</select>
      <label htmlFor="hours" className="spaced-label">Weekly learning time</label>
      <select id="hours" value={hours} onChange={event => onHours(Number(event.target.value))}>{hourOptions.map(h => <option key={h} value={h}>{h} hours / week</option>)}</select>
      <a className="button spaced-label" href="/intake">Create Skill Profile</a><section className="profile-section"><h3>Current skills</h3><ul className="skill-list">{Object.entries(profile.skill_levels).map(([id, level]) => <li key={id}><span>{skillById.get(id)?.label ?? id}</span><LevelDots level={level} /></li>)}</ul><p className="small muted">Synthetic, self-confirmed levels. Unknown is distinct from 0.</p></section>
      <fieldset className="profile-section"><legend>Adoption scenario</legend>{data.scenarios.map(s => <label className="radio-row" key={s.scenario_id}><input type="radio" name="scenario" value={s.scenario_id} checked={scenario === s.scenario_id} onChange={() => onScenario(s.scenario_id)} />{s.scenario_id === 'moderate' ? 'Moderate' : 'Fast'}</label>)}<p className="small muted">{Math.round(weight * 100)}% signal weight</p></fieldset>
      <p className="profile-note">Fictional profiles. No real CVs.</p>
    </div>
  </details></aside>;
}
