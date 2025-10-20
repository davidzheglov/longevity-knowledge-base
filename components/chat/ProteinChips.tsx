"use client";
import React from 'react';

export default function ProteinChips({ onInsert } : { onInsert: (s:string)=>void }){
  const chips = [
    { key: 'SIRT1', prompt: 'Summarize human evidence for SIRT1...' },
    { key: 'mTOR', prompt: 'Summarize human evidence for mTOR...' },
    { key: 'AMPK', prompt: 'Summarize human evidence for AMPK...' }
  ];
  return (
    <div className="flex gap-2 mb-2">
      {chips.map(c=> <button key={c.key} className="px-2 py-1 rounded bg-slate-800/40" onClick={()=>onInsert(c.prompt)}>{c.key}</button>)}
    </div>
  );
}
