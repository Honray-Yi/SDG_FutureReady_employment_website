import { useCallback, useEffect, useState } from 'react';
import { ArrowRight, ArrowUpRight, LockKeyhole, Mail, Pause, Play, Sparkles } from 'lucide-react';
import App from '../../App';
import { Orb } from './Orb';
import { ParticleEntrance } from './ParticleEntrance';
import './welcome.css';
import { LanguageSwitcher, useLanguage } from '../../i18n';
import { demoAuth, demoCredentials, authMessage } from '../../demoAuth';

export function WelcomeGate() {
  const { t, language } = useLanguage();
  const [screen,setScreen]=useState<'welcome'|'entrance'|'app'>('welcome');
  const [paused,setPaused]=useState(false);
  const [email,setEmail]=useState('');
  const [password,setPassword]=useState('');
  const [account,setAccount]=useState<string|null>(null);
  const [checking,setChecking]=useState(true);
  const [busy,setBusy]=useState(false);
  const [authError,setAuthError]=useState('');
  const complete=useCallback(()=>setScreen('app'),[]);
  useEffect(()=>{
    let active=true;
    demoAuth('me').then(session=>{if(active&&session){setAccount(session.user.email);setScreen('app');}})
      .catch(()=>{if(active)setAuthError('auth_unavailable');}).finally(()=>{if(active)setChecking(false);});
    return ()=>{active=false;};
  },[]);
  useEffect(()=>{
    if(screen!=='app')return;
    const check=()=>{void demoAuth('me').then(session=>{if(!session){setAccount(null);setScreen('welcome');setAuthError('auth_expired');}}).catch(()=>{});};
    const timer=window.setInterval(check,60000);
    window.addEventListener('focus',check);
    return ()=>{window.clearInterval(timer);window.removeEventListener('focus',check);};
  },[screen]);
  async function signIn() {
    setBusy(true);setAuthError('');
    try {
      const session=await demoAuth('login',{email,password});
      if(!session)throw new Error('auth_unavailable');
      setAccount(session.user.email);setPassword('');setScreen('entrance');
    } catch(error) {setAuthError(error instanceof Error?error.message:'auth_unavailable');}
    finally {setBusy(false);}
  }
  async function signOut() {
    setBusy(true);setAuthError('');
    try {await demoAuth('logout');setAccount(null);setPassword('');setAuthError('');setScreen('welcome');}
    catch(error){setAuthError(error instanceof Error?error.message:'auth_unavailable');}
    finally {setBusy(false);}
  }
  useEffect(()=>{
    if(screen!=='app')document.title=t('Future Ready — Your next chapter','Future Ready — 你的职业新篇章');
    if(screen==='app')requestAnimationFrame(()=>document.getElementById('main-content')?.focus());
    if(screen==='welcome')window.scrollTo(0,0);
  },[screen,language,t]);
  if(screen==='app')return <div className="demo-app-reveal"><App onExitDemo={()=>{void signOut();}} demoAccount={account??undefined} authBusy={busy} authError={authError?authMessage(authError,language):undefined}/></div>;
  if(screen==='entrance')return <ParticleEntrance onComplete={complete}/>;
  return <div className="welcome-page">
    <section className="welcome-art" aria-label={t('Future Ready introduction','Future Ready 简介')}>
      <a className="welcome-wordmark" href="#" aria-label="Future Ready welcome"><span className="brand-symbol" aria-hidden="true">✳</span> Future Ready<span className="brand-period">.</span></a>
      <div className="orb-composition"><Orb paused={paused}/></div>
      <div className="welcome-story"><div className="welcome-eyebrow"><span/> {t('A NEW WORLD OF POSSIBILITY','开启更多可能')}</div>
        <h1>{t('Your future.','你的未来。')}<br/><span>{t('In a new light.','从新的视角出发。')}</span></h1>
        <p>{t('Discover where your skills can take you.','发现你的经历可以通往何处。')}<br/>{t('Make your next move a meaningful one.','让下一步更有方向。')}</p>
      </div>
      <div className="art-footer"><span>{t('HUMAN POTENTIAL, REIMAGINED','重新发现人的潜能')}</span><button className="motion-control" onClick={()=>setPaused(x=>!x)} aria-label={paused?t('Play orb animation','播放光球动画'):t('Pause orb animation','暂停光球动画')} aria-pressed={paused}>{paused?<Play size={13}/>:<Pause size={13}/>}</button></div>
    </section>
    <section className="welcome-access" aria-labelledby="welcome-title">
      <div className="access-top"><span>{t('CAREER EXPLORATION, EVOLVED','更清晰的职业探索')}</span><LanguageSwitcher/></div>
      <div className="access-content">
        <div className="access-icon" aria-hidden="true"><Sparkles size={24} strokeWidth={1.1}/></div>
        <div className="welcome-eyebrow access-eyebrow">{t('THE NEXT CHAPTER IS YOURS','下一章，由你开启')}</div>
        <h2 id="welcome-title">{t('Welcome back.','欢迎回来。')}</h2>
        <p className="access-description">{t('A clearer direction. A future full of possibility.','方向更清晰，未来有更多可能。')}</p>
        <form onSubmit={e=>{e.preventDefault();void signIn();}} aria-describedby="demo-disclosure demo-account">
          <div className="credential-preview"><div className="account-label">{t('ACCOUNT ACCESS','账号入口')} <span>{t('Demo sign-in','演示登录')}</span></div>
            <label htmlFor="preview-email">{t('Email address','电子邮箱')}</label><div className="welcome-field"><Mail size={16} aria-hidden="true"/><input id="preview-email" type="email" placeholder="you@example.com" required maxLength={254} value={email} onChange={e=>setEmail(e.target.value)} disabled={busy||checking} autoComplete="username"/></div>
            <label htmlFor="preview-password">{t('Password','密码')} <LockKeyhole size={12} aria-hidden="true"/></label><div className="welcome-field"><LockKeyhole size={16} aria-hidden="true"/><input id="preview-password" type="password" placeholder="••••••••••" required maxLength={256} value={password} onChange={e=>setPassword(e.target.value)} disabled={busy||checking} autoComplete="current-password"/></div>
          </div>
          <div className="demo-disclosure" id="demo-disclosure"><span className="demo-dot"/><p>{t('Public shared demo account. Do not enter a real personal password. This is not a production identity service.','公开共享演示账号，请勿输入个人真实密码。这不是生产身份认证服务。')}</p></div>
          {authError&&<p className="auth-error" role="alert">{authMessage(authError,language)}</p>}
          <button className="enter-demo" type="submit" disabled={busy||checking}><span>{checking?t('Checking session…','正在检查会话…'):busy?t('Signing in…','正在登录…'):t('Log in to demo','登录演示')}</span><ArrowRight size={19}/></button>
          <div className="demo-account" id="demo-account"><span>{t('Public demo credentials','公开演示凭据')}</span><code>{demoCredentials.email}</code><code>{demoCredentials.password}</code><button type="button" disabled={busy||checking} onClick={()=>{setEmail(demoCredentials.email);setPassword(demoCredentials.password);setAuthError('');}}>{t('Fill demo credentials','填入演示凭据')}</button></div>
        </form>
      </div>
      <div className="access-footer"><span>© {new Date().getFullYear()} Future Ready</span><span>{t('Built around your potential','以你的潜能为中心')} <span aria-hidden="true">↗</span></span></div>
    </section>
  </div>;
}
