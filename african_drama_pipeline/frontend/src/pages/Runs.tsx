import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { API } from '../App';

type Run = { id: string; status: string; region: string; genre: string; accent: string; created_at: string; updated_at: string };

export default function Runs() {
  const [runs, setRuns] = useState<Run[]>([]);
  const [form, setForm] = useState({ region: 'Uganda', genre: 'family_drama', accent: 'Ugandan', language: 'en' });
  const [loading, setLoading] = useState(false);

  useEffect(() => { fetchRuns(); }, []);

  const fetchRuns = async () => {
    const res = await fetch(`${API}/pipeline/runs`);
    const data = await res.json();
    setRuns(data);
  };

  const startRun = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    await fetch(`${API}/pipeline/run`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(form) });
    setLoading(false);
    await fetchRuns();
  };

  return (
    <div className="space-y-6">
      <section className="space-y-3">
        <h1 className="text-xl font-semibold">New Run</h1>
        <form onSubmit={startRun} className="space-y-2">
          <input className="w-full rounded bg-slate-900 border border-slate-800 p-3" placeholder="Region" value={form.region} onChange={e => setForm({...form, region: e.target.value})} />
          <input className="w-full rounded bg-slate-900 border border-slate-800 p-3" placeholder="Genre" value={form.genre} onChange={e => setForm({...form, genre: e.target.value})} />
          <input className="w-full rounded bg-slate-900 border border-slate-800 p-3" placeholder="Accent" value={form.accent} onChange={e => setForm({...form, accent: e.target.value})} />
          <input className="w-full rounded bg-slate-900 border border-slate-800 p-3" placeholder="Language" value={form.language} onChange={e => setForm({...form, language: e.target.value})} />
          <button disabled={loading} className="w-full rounded bg-indigo-500 py-3 font-medium disabled:opacity-50">{loading ? 'Starting...' : 'Start Pipeline'}</button>
        </form>
      </section>

      <section className="space-y-3">
        <h2 className="text-lg font-semibold">Runs</h2>
        <ul className="space-y-2">
          {runs.map(r => (
            <li key={r.id} className="rounded border border-slate-800 p-3 flex items-center justify-between">
              <div>
                <div className="font-mono text-xs text-slate-400">{r.id}</div>
                <div className="text-sm">{r.region} • {r.genre}</div>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-xs rounded bg-slate-800 px-2 py-1">{r.status}</span>
                <Link to={`/runs/${r.id}`} className="text-indigo-400 text-sm">Open</Link>
              </div>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
