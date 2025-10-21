"use client";
import React, { useState } from 'react';
import { motion, useReducedMotion } from 'framer-motion';

export default function MessageInput({ value, onChange, onSend } : { value:string; onChange: (v:string)=>void; onSend: ()=>void }){
  const [sending, setSending] = useState(false);
  const reduce = useReducedMotion();

  async function handleSend(){
    if (!value.trim()) return;
    setSending(true);
    await onSend();
    setSending(false);
  }

  function onKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>){
    // Enter to send, Shift+Enter for newline
    if (e.key === 'Enter' && !e.shiftKey){
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <div className="mt-4 flex items-center gap-3">
      <textarea value={value} onChange={(e)=>onChange(e.target.value)} onKeyDown={onKeyDown} rows={1} className="flex-1 resize-none rounded-xl p-3 bg-slate-800/60 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-primary transition" placeholder="Type a message..." />
      <motion.button whileTap={reduce ? {} : { scale: 0.97 }} onClick={handleSend} disabled={sending} className="bg-white/90 text-slate-900 px-4 py-2 rounded-full shadow hover:scale-105 active:scale-95 transition">
        {sending ? 'Sending...' : 'Send'}
      </motion.button>
    </div>
  )
}
