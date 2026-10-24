import { useEffect, useRef } from 'react';
import { RefreshCw, X } from 'lucide-react';
import { date } from '../api';
import type { Bootstrap } from '../types';
import { ExternalLink } from './Shared';

export function SourcesDialog({ data, onClose, reload }: { data: Bootstrap; onClose: () => void; reload: () => void }) {
  const ref = useRef<HTMLDialogElement>(null);
  const opener = useRef<HTMLElement | null>(null);
  useEffect(() => {
    const dialog = ref.current!;
    if (!opener.current && document.activeElement instanceof HTMLElement) opener.current = document.activeElement;
    dialog.showModal();
    return () => {
      dialog.close();
      queueMicrotask(() => { if (opener.current?.isConnected) opener.current.focus(); });
    };
  }, []);
  return <dialog ref={ref} onCancel={onClose} aria-labelledby="sources-title" className="sources-dialog"><div className="dialog-heading"><div><h2 id="sources-title">Data & sources</h2><p>Evidence you can inspect.</p></div><button className="icon-button" onClick={onClose} aria-label="Close data sources"><X size={22} /></button></div><div className="dialog-body"><div className="notice"><strong>Cached public observations</strong><p>This page reads the bundled snapshot. Reloading reads local files again; it does not fetch new external observations.</p><button className="button" onClick={reload}><RefreshCw size={15} />Reload snapshot</button></div>
    <dl className="source-dates"><dt>Research collected</dt><dd>{date(data.metadata.research_retrieved_at)}</dd><dt>Jobs collected</dt><dd>{date(data.metadata.jobs_retrieved_at)}</dd><dt>Signals calculated</dt><dd>{date(data.metadata.signals_computed_at)} (not a source refresh)</dd><dt>Snapshot ID</dt><dd><code>{data.metadata.snapshot_id}</code></dd></dl>
    <h3>What these results mean</h3><ul className="provenance-list"><li><strong>Observed:</strong> research counts and public job sample frequencies, with timestamps.</li><li><strong>Curated:</strong> occupation-to-skill mappings, course coverage and SDG interpretations.</li><li><strong>Synthetic:</strong> every demo profile and its skill levels. No real CVs are used.</li><li><strong>Computed:</strong> explainable ranking indices and learning sequences. No LLM is used, and scores are not hiring probabilities.</li></ul>
    <p>{data.metadata.jobs_scope} MyCOL and DOSM provide separate Malaysia context. O*NET titles and BLS outlook are US references.</p>
    <h3>Source registry</h3><div className="source-registry">{data.sources.map(source => <article key={source.source_id}><ExternalLink href={source.url}>{source.source_id.replaceAll('_', ' ')}</ExternalLink><p>{source.use ?? source.kind.replaceAll('_', ' ')}</p>{source.geography && <p className="small muted">Scope: {source.geography}</p>}{source.limitations && <p className="small">{source.limitations}</p>}{source.docs && <ExternalLink href={source.docs}>Documentation</ExternalLink>}</article>)}</div>
    <h3>Update & fallback</h3><p>Run the included Python refresh script to retrieve new observations. A failed source refresh keeps its previous cache; the interface continues to show the actual retrieval dates. Keep related files together when deploying a new snapshot.</p><p className="small">No salary is displayed without verified evidence. Courses can change their access terms; open the provider page before enrolling.</p>
  </div></dialog>;
}
