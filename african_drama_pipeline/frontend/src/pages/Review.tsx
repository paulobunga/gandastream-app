import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { API } from '../App';

type Stage = { stage_name: string; status: string; output: any; error?: string };

export default function Review() {
  const { runId } = useParams();
  const [stages, setStages] = useState<Stage[]>([]);
  const [stageOutput, setStageOutput] = useState<any>(null);

  useEffect(() => {
    if (!runId) return;
    fetch(`${API}/pipeline/runs/${runId}`).then(r => r.json()).then(async (run) => {
      const items: Stage[] = [];
      const names = ['trends','screenplay','scenes','character_refs','shot_prompts','video_prompts','voice_assignments','clips','timeline','posts'];
      for (const name of names) {
        const res = await fetch(`${API}/pipeline/runs/${runId}/stages/${name}`);
        const data = await res.json();
        items.push(data);
      }
      setStages(items);
      setStageOutput(run);
    });
  }, [runId]);

  return (
    <div className="space-y-4">
      <h1 className="text-lg font-semibold">Draft Review</h1>
      <div className="space-y-2">
        {stages.map(s => (
          <div key={s.stage_name} className="rounded border border-slate-800 p-3 flex items-center justify-between">
            <div>
              <div className="font-medium">{s.stage_name}</div>
              <div className="text-xs text-slate-400">{s.status}</div>
            </div>
            <button onClick={() => setStageOutput({ selected: s.stage_name, output: s.output })} className="text-xs rounded bg-slate-800 px-2 py-1">View</button>
          </div>
        ))}
      </div>

      {stageOutput && (
        <pre className="rounded bg-slate-900 border border-slate-800 p-3 text-xs overflow-auto max-h-80">
          {JSON.stringify(stageOutput, null, 2)}
        </pre>
      )}

      <div className="flex gap-3">
        <button onClick={async () => { await fetch(`${API}/pipeline/runs/${runId}/approve`, { method: 'POST' }); window.location.reload(); }} className="flex-1 rounded bg-indigo-500 py-3 font-medium">Approve</button>
        <Link to={`/runs/${runId}/publish`} className="flex-1 rounded bg-emerald-500 py-3 text-center font-medium">Publish</Link>
      </div>
    </div>
  );
}
