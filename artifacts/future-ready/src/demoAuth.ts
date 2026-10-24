import type { DemoSession } from '@workspace/api-client-react';

export const demoCredentials = { email: 'demo@futureready.example', password: 'FutureReadyDemo2026!' };
const base = import.meta.env.BASE_URL.replace(/\/$/, '');
export async function demoAuth(action: 'login' | 'me' | 'logout', body?: { email: string; password: string }): Promise<DemoSession | null> {
  const response = await fetch(`${base}/api/demo-auth/${action}`, {
    method: action === 'me' ? 'GET' : 'POST',
    credentials: 'include', cache: 'no-store',
    headers: action === 'me' ? {} : { 'Content-Type': 'application/json', 'X-Demo-Action': '1' },
    ...(body ? { body: JSON.stringify(body) } : {}),
  });
  if (action === 'me' && response.status === 401) return null;
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error?.detail?.code ?? 'auth_unavailable');
  }
  return response.status === 204 ? null : response.json();
}

export function authMessage(code: string, language: 'en'|'zh') {
  const messages: Record<string,[string,string]> = {
    auth_invalid: ['Incorrect email or password. Use the public demo credentials below.','邮箱或密码不正确，请使用下方公开演示凭据。'],
    auth_rate_limited: ['Too many sign-in attempts. Please wait five minutes.','登录尝试过多，请等待五分钟。'],
    auth_capacity: ['The demo is at capacity. Please try later.','演示会话已达上限，请稍后重试。'],
    auth_origin: ['Please sign in from this site’s login form.','请从本站登录表单登录。'],
    auth_expired: ['Your demo session expired. Please sign in again.','演示会话已过期，请重新登录。'],
  };
  return (messages[code] ?? ['Demo sign-in is temporarily unavailable. Please try again.','演示登录暂不可用，请重试。'])[language === 'en' ? 0 : 1];
}
