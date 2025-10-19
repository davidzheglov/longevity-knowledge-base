"use client";
import React from 'react';

type Chat = { id: number; title?: string };

export default function ChatList({ chats, activeId, onSelect, onCreate, onDelete }:
  { chats: Chat[]; activeId?: number | null; onSelect: (c: Chat)=>void; onCreate: ()=>void; onDelete: (id:number)=>void }){
  return (
    <div className="w-72 bg-gradient-to-b from-slate-800/60 to-slate-900/40 p-4 rounded-xl shadow-lg backdrop-blur-md">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-lg font-semibold">Chats</h3>
        <button onClick={onCreate} className="text-sm bg-primary px-3 py-1 rounded-full hover:brightness-110 transition">New</button>
      </div>
      <ul className="space-y-2 max-h-[60vh] overflow-auto">
        {chats.map(c=> (
          <li key={c.id} className={`flex items-center justify-between p-2 rounded-lg cursor-pointer transition hover:bg-slate-700/40 ${activeId===c.id? 'bg-slate-700/60 ring-1 ring-primary/60':''}`}>
            <button className="text-left flex-1 truncate" onClick={()=>onSelect(c)}>{c.title || `Chat ${c.id}`}</button>
            <div className="flex items-center gap-2">
              <button onClick={()=>onDelete(c.id)} className="text-xs text-rose-400 hover:text-rose-300">Delete</button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  )
}
