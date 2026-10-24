import { ArrowUpRight, RefreshCw } from 'lucide-react';
import type { ReactNode } from 'react';
import type { Sdg } from '../types';

export function ExternalLink({ href, children, className = '' }: { href: string; children: ReactNode; className?: string }) {
  return <a className={`external-link ${className}`} href={href} target="_blank" rel="noopener noreferrer">{children}<ArrowUpRight size={15} aria-hidden="true" /><span className="sr-only"> (opens in a new tab)</span></a>;
}
export function ErrorState({ message, retry }: { message: string; retry: () => void }) {
  return <div className="error-state" role="alert"><h2>Let’s reconnect.</h2><p>{message}</p><button className="button" onClick={retry}><RefreshCw size={16} />Try again</button></div>;
}
export function Loading() {
  return <div className="loading-state" role="status"><span className="spinner" aria-hidden="true" /><p>Reading the evidence and matching skills…</p></div>;
}
export function SdgLinks({ items }: { items: Sdg[] }) {
  return <div className="sdg-list">{items.map(item => <div key={item.target_code}><ExternalLink href={item.source_url}>SDG {item.sdg_id} · {item.sdg_label}</ExternalLink><p className="small">Target {item.target_code} · Team interpretation</p><p className="small" lang="zh-CN">{item.rationale_zh}</p></div>)}</div>;
}
export function LevelDots({ level }: { level: number | null }) {
  if (level === null) return <span className="small muted">Unknown</span>;
  return <span className="dots" aria-label={`${level} of 3`}>{[1, 2, 3].map(n => <i key={n} className={n <= level ? 'filled' : ''} />)}</span>;
}
