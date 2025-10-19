"use client";
import React, { useEffect, useRef } from 'react';

type Message = { id: number; role: string; content: string };

export default function ChatWindow({ messages } : { messages: Message[] }){
  const endRef = useRef<HTMLDivElement|null>(null);
  useEffect(()=>{ endRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' }) },[messages]);

  return (
    <div className="flex flex-col gap-4 p-6 rounded-xl bg-gradient-to-b from-slate-900/40 to-slate-900/20 shadow-inner h-[60vh] overflow-auto">
      {messages.length===0 && (
        <div className="text-center text-slate-400 mt-8">No messages yet. Say hi 👋</div>
      )}
      {messages.map(m=> (
        <div key={m.id} className={`max-w-[70%] ${m.role==='user' ? 'self-end bg-gradient-to-tr from-primary to-accent text-white' : 'self-start bg-slate-700/60 text-slate-100'} p-3 rounded-2xl shadow-md transform transition-all duration-300`}> 
          <div className="text-sm">{m.content}</div>
          <div className="text-xs text-slate-300 mt-1 opacity-80">{m.role==='user'? 'You' : 'Assistant'}</div>
        </div>
      ))}
      <div ref={endRef} />
    </div>
  )
}
