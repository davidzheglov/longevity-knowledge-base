"use client";
import React from 'react';

export type Artifact = { id: string; label?: string; type?: string; path?: string; name?: string; size?: number; url?: string };

export default function ArtifactsPanel({ artifacts }: { artifacts: Artifact[] }){
  if (!artifacts || artifacts.length === 0) {
    return (
      <div className="mt-6 rounded-xl border border-white/10 bg-slate-800/40 p-4">
        <div className="text-sm font-semibold mb-2">Run artifacts</div>
        <div className="text-xs text-slate-300">No artifacts yet. They will appear here after a tool runs.</div>
      </div>
    );
  }
  // Sort by type then name for readability
  const list = [...artifacts].sort((a,b)=> (a.type||'').localeCompare(b.type||'') || (a.name||'').localeCompare(b.name||''));
  return (
    <div className="mt-6 rounded-xl border border-white/10 bg-slate-800/40 p-4">
      <div className="text-sm font-semibold mb-2">Run artifacts</div>
      <ul className="space-y-2">
        {list.map((a)=> (
          <li key={a.id} className="flex items-start justify-between gap-3 text-xs">
            <div className="min-w-0">
              <div className="truncate">
                {a.url ? (
                  <a href={a.url} target="_blank" rel="noreferrer" className="underline hover:text-indigo-200">
                    {a.name || a.label || a.id}
                  </a>
                ) : (
                  <span>{a.name || a.label || a.id}</span>
                )}
              </div>
              <div className="opacity-75 mt-0.5">
                <span className="inline-block rounded bg-white/10 px-1.5 py-0.5 mr-2">{(a.type||'').toUpperCase() || 'FILE'}</span>
                {typeof a.size === 'number' && <span>{(a.size/1024).toFixed(1)} KB</span>}
              </div>
            </div>
            {a.url && (
              <a href={a.url} target="_blank" rel="noreferrer" title="Open" className="shrink-0 opacity-80 hover:opacity-100">
                ⤴
              </a>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
