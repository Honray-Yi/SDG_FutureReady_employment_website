import { useEffect, useState } from 'react';
import { ArrowRight } from 'lucide-react';
import { useApi } from './api';
import type { Bootstrap, Match, Page } from './types';
import { ProfilePanel } from './components/ProfilePanel';
import { Workspace } from './components/Workspace';
import { SkillsRadar } from './components/SkillsRadar';
import { LearningPath } from './components/LearningPath';
import { SourcesDialog } from './components/SourcesDialog';
import { ErrorState, Loading } from './components/Shared';
import { ResumeExplorer } from './components/ResumeExplorer';
import { LanguageSwitcher, useLanguage } from './i18n';

const pages: { id: Page; label: string }[] = [{ id: 'explore', label: 'Text explorer' }, { id: 'workspace', label: 'Synthetic demo: Workspace' }, { id: 'radar', label: 'Skills radar' }, { id: 'path', label: 'Synthetic demo: Learning path' }];
const currentPage = (): Page => pages.find(p => `#${p.id}` === window.location.hash)?.id ?? 'explore';
const legacy = new URLSearchParams(window.location.search).get('catalog') === 'legacy';
const MODULE1_PROFILE_HANDOFF_KEY = 'future-ready.module1-profile-handoff.v1';

export default function App({ onExitDemo, demoAccount, authBusy, authError }: { onExitDemo?: () => void; demoAccount?: string; authBusy?: boolean; authError?: string }) {
  const { language,t }=useLanguage();
  const pageLabel=(id:Page)=>id==='explore'?t('Resume explorer','简历探索'):id==='workspace'?t('Synthetic demo: Workspace','独立合成演示：工作台'):id==='radar'?t('Skills radar','技能趋势'):t('Synthetic demo: Learning path','独立合成演示：学习路径');
  const [page, setPage] = useState<Page>(currentPage);
  const [revision, setRevision] = useState(0);
  const [profileId, setProfileId] = useState<string | null>(null);
  const [scenario, setScenario] = useState('moderate');
  const [hoursOverride, setHoursOverride] = useState<number | null>(null);
  const [selectedRole, setSelectedRole] = useState<string | null>(null);
  const [sourcesOpen, setSourcesOpen] = useState(false);
  const [imported, setImported] = useState<Record<string, unknown> | null>(null);
  const [importError, setImportError] = useState('');
  const [pendingHandoff, setPendingHandoff] = useState<string | null>(null);
  const bootstrap = useApi<Bootstrap>(legacy ? '/api/legacy/bootstrap' : '/api/bootstrap', null, revision);
  const data = bootstrap.data;
  const profile = data?.profiles.find(p => p.profile_id === profileId) ?? data?.profiles[0];
  const hours = hoursOverride ?? profile?.hours_per_week ?? 8;
  const match = useApi<Match>(profile ? legacy ? '/api/legacy/match' : '/api/match' : null, profile ? JSON.stringify({ ...(imported ? {profile: imported} : {profile_id: profile.profile_id}), scenario, hours_per_week: hours }) : null, revision);
  const result = match.data;
  const role = result?.roles.find(r => r.role_id === selectedRole) ?? result?.roles[0];
  useEffect(() => { const handler = () => setPage(currentPage()); window.addEventListener('hashchange', handler); return () => window.removeEventListener('hashchange', handler); }, []);
  useEffect(() => { document.title = `FutureReady — ${pageLabel(page)}`; }, [page,language]);
  function navigate(next: Page) { window.location.hash = next; setPage(next); }
  function changeProfile(id: string) { setImported(null); setImportError(''); const input = document.getElementById('module1-profile') as HTMLInputElement | null; if (input) input.value = ''; setProfileId(id); setHoursOverride(null); setSelectedRole(null); }
  function importProfileJson(text: string) {
    if (new TextEncoder().encode(text).length > 256 * 1024) throw Error(t('Profile JSON must be under 256 KB.','档案 JSON 不能超过 256 KB。'));
    const value: unknown = JSON.parse(text);
    if (!value || typeof value !== 'object' || Array.isArray(value)) throw Error(t('Select a Module 1 exported profile JSON.','请选择 Module 1 导出的档案 JSON。'));
    const profile = value as Record<string, unknown>;
    if (profile.is_synthetic !== true) throw Error(t('Only synthetic Module 1 profiles are permitted.','仅支持 Module 1 合成档案。'));
    if (!Array.isArray(profile.skills) || typeof profile.dictionary_hash !== 'string' || typeof profile.skill_dictionary_version !== 'string') throw Error(t('Select a Module 1 exported profile JSON.','请选择 Module 1 导出的档案 JSON。'));
    setImported(profile); setImportError(''); setSelectedRole(null);
  }
  async function importProfile(file?: File) {
    if (!file) return;
    try {
      if (file.size > 256 * 1024) throw Error(t('Profile JSON must be under 256 KB.','档案 JSON 不能超过 256 KB。'));
      importProfileJson(await file.text());
    } catch (error) { setImportError(error instanceof Error ? error.message : t('Cannot read this profile.','无法读取此档案。')); }
  }
  useEffect(() => {
    try {
      const pending = sessionStorage.getItem(MODULE1_PROFILE_HANDOFF_KEY);
      if (!pending) return;
      sessionStorage.removeItem(MODULE1_PROFILE_HANDOFF_KEY);
      setPendingHandoff(pending);
      window.location.hash = 'workspace';
      setPage('workspace');
    } catch (error) {
      setImportError(error instanceof Error ? error.message : t('Cannot read this profile.','无法读取此档案。'));
    }
  }, []);
  useEffect(() => {
    if (!pendingHandoff || !data || !profile || page === 'explore') return;
    setPendingHandoff(null);
    try {
      const fileInput = document.getElementById('module1-profile') as HTMLInputElement | null;
      let handedOffFile: File | undefined;
      try {
        if (fileInput && typeof DataTransfer !== 'undefined' && typeof File !== 'undefined') {
          const transfer = new DataTransfer();
          transfer.items.add(new File([pendingHandoff], 'skills-profile-module1.json', { type: 'application/json' }));
          fileInput.files = transfer.files;
          handedOffFile = fileInput.files?.[0];
        }
      } catch { /* Older browsers still import the same JSON directly. */ }
      if (handedOffFile) void importProfile(handedOffFile);
      else importProfileJson(pendingHandoff);
    } catch (error) {
      setImportError(error instanceof Error ? error.message : t('Cannot read this profile.','无法读取此档案。'));
    }
  }, [pendingHandoff, data, profile, page]);
  function reload() { setSourcesOpen(false); setRevision(value => value + 1); }
  const title = page === 'explore' ? t('Find your next direction.','发现你的下一步方向。') : page === 'workspace' ? t('A clearer path to what’s next.','更清晰的下一步。') : page === 'radar' ? t('Weigh the signals.','理解趋势信号。') : t('Turn direction into progress.','把方向转化为行动。');
  const subtitle = page === 'explore' ? t('Local semantic matching, bilingual keyword evidence and source-reviewed learning resources.','本地语义匹配、双语关键词依据，以及有来源记录的学习资源。') : page === 'workspace' ? t('Explore future roles through your skills and real-world signals.','通过技能与趋势探索未来职业。') : page === 'radar' ? t('Understand changes in AI research and the limits of the evidence.','了解 AI 研究变化及证据的适用边界。') : t('A practical learning sequence with sources and prerequisites.','基于来源与先修条件的学习顺序。');
  return <><a className="skip-link" href="#main-content">{t('Skip to content','跳转至正文')}</a><header className="app-header"><a className="wordmark" href="#explore" onClick={() => navigate('explore')}>FutureReady</a><nav aria-label={t('Main navigation','主导航')}>{pages.map(item => <button key={item.id} aria-current={page === item.id ? 'page' : undefined} className={page === item.id ? 'active' : ''} onClick={() => navigate(item.id)}>{pageLabel(item.id)}</button>)}</nav><LanguageSwitcher/><button className="button sources-button" disabled={!data} onClick={() => setSourcesOpen(true)}>{t('Data & sources','数据与来源')}<ArrowRight size={16} /></button></header>
    <div className="demo-session-bar">{demoAccount&&<span>{t('Signed in as','当前账号')} {demoAccount}</span>}{onExitDemo&&<button className="button" disabled={authBusy} onClick={onExitDemo}>{authBusy?t('Signing out…','正在退出…'):t('Log out','退出登录')}</button>}{authError&&<p role="alert">{authError}</p>}</div>
    <main id="main-content" tabIndex={-1}><div className="page-intro"><h1>{title}</h1><p>{subtitle}</p><a className="text-button" href={legacy?'/?#workspace':'/?catalog=legacy#workspace'}>{legacy?t('Back to the Module 1 workspace','返回模块 1 工作台'):t('View the five historical synthetic profiles','查看原有 5 个合成档案')} · {t('Independent historical demo, separate from resume results','独立历史合成演示，与简历分析结果无关')}</a></div>
      {page !== 'explore' && <div className="notice"><strong>{t('Independent synthetic demo','独立合成演示')}</strong><p>{t('These reference pages use their own historical source data, which may contain original-language content. They are not driven by resume explorer results.','这些参考页面使用独立历史来源数据，可能保留原文内容，并非当前简历的分析结果。')}</p></div>}{page === 'explore' ? <ResumeExplorer/> : bootstrap.error ? <ErrorState message={bootstrap.error} retry={reload} /> : !data || !profile ? <Loading /> : <div className="app-layout"><ProfilePanel data={data} profile={imported && result && !match.error ? result.profile : profile} scenario={scenario} hours={hours} onProfile={changeProfile} onScenario={setScenario} onHours={setHoursOverride} /><div className="main-surface"><div className="profile-import"><label htmlFor="module1-profile">{t('Import synthetic Module 1 profile JSON','导入模块 1 合成档案 JSON')}</label><input id="module1-profile" type="file" accept=".json,application/json" onChange={event => { void importProfile(event.target.files?.[0]); event.target.value=''; }} />{imported && result && !match.error && <p role="status">{t('Module 1 profile imported and analyzed','已导入并分析 Module 1 技能档案')}: {result.profile.current_role}</p>}{imported && <button className="button" onClick={() => { setImported(null); const input = document.getElementById('module1-profile') as HTMLInputElement | null; if (input) input.value = ''; }}>{t('Use demo profile','使用演示档案')}</button>}{importError && <p role="alert">{importError}</p>}</div>
        {page === 'radar' ? <SkillsRadar data={data} profile={imported && result && !match.error ? result.profile : profile} /> : match.error ? <ErrorState message={match.error} retry={reload} /> : !result || !role ? <Loading /> : page === 'workspace' ? <Workspace data={data} result={result} role={role} selectRole={setSelectedRole} onPath={() => navigate('path')} onSources={() => setSourcesOpen(true)} /> : <LearningPath data={data} result={result} role={role} onRole={setSelectedRole} />}
      </div></div>}
    </main><footer className="app-footer"><span>{t('FutureReady · Built for informed career exploration','FutureReady · 帮助你更有依据地探索职业')}</span><span>{t('Transparent evidence · Local analysis · Human judgement','透明依据 · 本地分析 · 人工判断')}</span></footer>{sourcesOpen && data && <SourcesDialog data={data} onClose={() => setSourcesOpen(false)} reload={reload} />}
  </>;
}
