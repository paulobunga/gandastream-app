import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { API } from '../App';

type Run = { id: string; status: string; region: string; genre: string; accent: string; created_at: string; updated_at: string };

export default function RunDetail() {
  const { runId } = useParams();
  const [run, setRun] = useState<Run | null>(null);

  useEffect(() => {
    if (!runId) return;
    fetch(`${API}/pipeline/runs/${runId}`).then(r => r.json()).then(setRun);
  }, [runId]);

  if (!run) return <div className="text-slate-400">Loading...</div>;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-semibold">Run</h1>
          <div className="font-mono text-xs text-slate-400">{run.id}</div>
        </div>
        <span className="text-xs rounded bg-slate-800 px-2 py-1">{run.status}</span>
      </div>
      <div className="rounded border border-slate-800 p-3 text-sm space-y-1">
        <div>Region: {run.region}</div>
        <div>Genre: {run.genre}</div>
        <div>Accent: {run.accent}</div>
        <div>Created: {run.created_at}</div>
        <div>Updated: {run.updated_at}</div>
      </div>
      <div className="flex gap-3">
        <Link to={`/runs/${run.id}/review`} className="flex-1 rounded bg-indigo-500 py-3 text-center font-medium">Review Draft</Link>
        <Link to={`/runs/${run.id}/publish`} className="flex-1 rounded bg-emerald-500 py-3 text-center font-medium">Publish</Link>
      </div>
    </div>
  );
}
