"use client";
import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import styles from './chat.module.css';
import MagneticButton from '@/components/ui/MagneticButton';

export default function ChatList({ sessions: initial = null, activeId, onSelect = ()=>{}, onCreate = ()=>{}, onDelete = ()=>{} , onNewFocus, onLoaded = (s:any)=>{} }: any){
  const [sessions, setSessions] = useState<any[] | null>(initial);
  const [loading, setLoading] = useState(false);

  useEffect(()=>{
    let mounted = true;
    async function load(){
      if (initial !== null) return; // parent provided list
      setLoading(true);
      try{
        const res = await fetch('/api/chats', { credentials: 'include' });
        if (res.ok){
          const data = await res.json();
          if (!mounted) return;
          // Accept either an array response or an object { chats: [...] }
          const list = Array.isArray(data) ? data : (Array.isArray(data?.chats) ? data.chats : []);
          setSessions(list);
          onLoaded(list);
        } else {
          // fallback to sessionStorage for guests
          const raw = sessionStorage.getItem('visitor_chats');
          const list = raw ? JSON.parse(raw) : [];
          if (!mounted) return;
          setSessions(list);
          onLoaded(list);
        }
      }catch(err){
        const raw = sessionStorage.getItem('visitor_chats');
        const list = raw ? JSON.parse(raw) : [];
        if (!mounted) return;
        setSessions(list);
        onLoaded(list);
      }finally{ if (mounted) setLoading(false); }
    }
    load();
    return ()=>{ mounted = false; };
  },[initial]);

  const list = sessions || [];

  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-lg font-semibold">Sessions</h3>
        <MagneticButton variant="primary" onClick={async ()=>{ onCreate(); onNewFocus && onNewFocus(); }}>{'New Chat'}</MagneticButton>
      </div>
      <div className={styles.sessions}>
        <AnimatePresence>
          {list.map((s:any)=> (
            <motion.div key={s.id} layout initial={{ opacity:0, y:6 }} animate={{ opacity:1, y:0 }} exit={{ opacity:0, y:-6 }} className={`p-3 rounded-lg cursor-pointer group relative ${activeId===s.id? 'ring-1 ring-primary/40':''}`} onClick={()=> onSelect(s)}>
              <div className="font-semibold">{s.title || `Chat ${s.id}`}</div>
              <div className="text-sm text-slate-400">{s.preview || 'No messages yet'}</div>

              <button
                aria-label={`Delete chat ${s.id}`}
                onClick={(e)=>{ e.stopPropagation(); onDelete(s.id); }}
                className="absolute right-2 top-2 text-sm text-slate-300 bg-slate-800/40 p-1 rounded opacity-70 hover:opacity-100"
                title="Delete chat"
              >
                🗑️
              </button>
            </motion.div>
          ))}
        </AnimatePresence>
        {loading && <div className="text-sm text-slate-400 p-2">Loading…</div>}
      </div>
    </div>
  );
}
