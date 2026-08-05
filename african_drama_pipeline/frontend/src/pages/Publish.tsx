import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { API } from '../App';

export default function Publish() {
  const { runId } = useParams();
  const [platform, setPlatform] = useState('tiktok');
  const [result, setResult] = useState<any>(null);

  const publish = async () => {
    const res = await fetch(`${API}/pipeline/runs/${runId}/publish?platform=${platform}`, { method: 'POST' });
    const data = await res.json();
    setResult(data);
  };

  return (
    <div className="space-y-4">
      <h1 className="text-lg font-semibold">Publish</h1>
      <select value={platform} onChange={e => setPlatform(e.target.value)} className="w-full rounded bg-slate-900 border border-slate-800 p-3">
        <option value="tiktok">TikTok</option>
        <option value="youtube">YouTube Shorts</option>
        <option value="instagram">Instagram Reels</option>
      </select>
      <button onClick={publish} className="w-full rounded bg-emerald-500 py-3 font-medium">Publish Now</button>
      {result && (
        <div className="rounded border border-slate-800 p-3 text-sm">
          <div>Status: {result.status}</div>
          <div>Post URL: {result.post_url}</div>
        </div>
      )}
      <Link to={`/runs/${runId}`} className="block text-center text-indigo-400 text-sm">Back to run</Link>
    </div>
  );
}
