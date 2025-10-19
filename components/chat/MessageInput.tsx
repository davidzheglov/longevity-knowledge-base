"use client";
import React, { useState } from 'react';

export default function MessageInput({ value, onChange, onSend } : { value:string; onChange: (v:string)=>void; onSend: ()=>void }){
  const [sending, setSending] = useState(false);
  async function handleSend(){
    if (!value.trim()) return;
    setSending(true);
    await onSend();
    setSending(false);
  }

  return (
    <div className="mt-4 flex items-center gap-3">
      <textarea value={value} onChange={(e)=>onChange(e.target.value)} rows={1} className="flex-1 resize-none rounded-xl p-3 bg-slate-800/60 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-primary transition" placeholder="Type a message..." />
      <button onClick={handleSend} disabled={sending} className="bg-gradient-to-r from-primary to-accent px-4 py-2 rounded-full shadow hover:scale-105 active:scale-95 transition">
        {sending ? 'Sending...' : 'Send'}
      </button>
    </div>
  )
}
