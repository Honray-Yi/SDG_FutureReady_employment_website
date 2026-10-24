import { useEffect, useState } from 'react';

export function useApi<T>(url: string | null, body: string | null, revision: number) {
  const [state, setState] = useState<{ data: T | null; error: string | null; loading: boolean }>({ data: null, error: null, loading: true });
  useEffect(() => {
    if (!url) return;
    const controller = new AbortController();
    setState({ data: null, error: null, loading: true });
    async function run() {
      try {
        const response = await fetch(url!, { signal: controller.signal, method: body ? 'POST' : 'GET', headers: body ? { 'Content-Type': 'application/json' } : undefined, body: body ?? undefined });
        if (!response.ok) {
          let message = 'The service could not complete the request.';
          try { const result = await response.json(); if (typeof result.detail === 'string') message = result.detail; } catch { /* Proxy errors can be non-JSON. */ }
          throw new Error(message);
        }
        const data = await response.json() as T;
        if (!controller.signal.aborted) setState({ data, error: null, loading: false });
      } catch (error) {
        if (!controller.signal.aborted) setState({ data: null, error: error instanceof TypeError ? 'Cannot reach the API. Check the local server, then try again.' : (error as Error).message, loading: false });
      }
    }
    void run();
    return () => controller.abort();
  }, [url, body, revision]);
  return state;
}

export function date(value?: string | null) {
  return value ? new Intl.DateTimeFormat('en-GB', { day: '2-digit', month: 'short', year: 'numeric', timeZone: 'UTC' }).format(new Date(value)) : 'Not available';
}
export const fixed = (n: number) => n.toFixed(1);
export const signed = (n: number) => `${n > 0 ? '+' : ''}${fixed(n)}`;
