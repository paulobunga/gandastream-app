import { createContext, useContext } from 'react';
import { createBrowserRouter, RouterProvider, Outlet, Link } from 'react-router-dom';
import Runs from './pages/Runs';
import RunDetail from './pages/RunDetail';
import Review from './pages/Review';
import Publish from './pages/Publish';

export const API = 'http://localhost:8000/api/v1';

export const router = createBrowserRouter([
  { path: '/', element: <Layout />, children: [
    { index: true, element: <Runs /> },
    { path: 'runs/:runId', element: <RunDetail /> },
    { path: 'runs/:runId/review', element: <Review /> },
    { path: 'runs/:runId/publish', element: <Publish /> },
  ]},
]);

function Layout() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <nav className="border-b border-slate-800 px-4 py-3 flex items-center gap-4">
        <Link to="/" className="font-semibold tracking-tight text-lg">gandastream</Link>
        <Link to="/" className="text-sm text-slate-400">Runs</Link>
      </nav>
      <main className="p-4 max-w-screen-sm mx-auto">
        <Outlet />
      </main>
    </div>
  );
}

export default function App() {
  return <RouterProvider router={router} />;
}
