"use client";
import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import styles from './chat.module.css';
import { Plus } from 'lucide-react';

export default function ChatList({ sessions: initial = null, activeId, onSelect = ()=>{}, onCreate = ()=>{}, onDelete = ()=>{} , onNewFocus, onLoaded = (s:any)=>{} }: any){
  const [sessions, setSessions] = useState<any[] | null>(initial);
  const [loading, setLoading] = useState(false);

  useEffect(()=>{
    let mounted = true;
    // If parent provided an explicit list, always reflect it immediately
    if (initial !== null){
      setSessions(initial);
      return () => { mounted = false; };
    }

    async function load(){
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
        <h3 className="text-lg font-semibold">Chats</h3>
        <motion.button  
        className="w-10 h-10 bg-[rgba(109,40,217,0.4)] text-white rounded-lg flex items-center justify-center transition-all hover:bg-[rgba(109,40,217,0.6)]"
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={async ()=>{ onCreate(); onNewFocus && onNewFocus(); }}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
        </motion.button>
      </div>
      <div className={styles.sessions}>
        <AnimatePresence>
          {list.map((s:any)=> (
            <motion.div key={s.id} layout initial={{ opacity:0, y:6 }} animate={{ opacity:1, y:0 }} exit={{ opacity:0, y:-6 }} className={`p-3 rounded-lg cursor-pointer group relative ${activeId===s.id? 'bg-[#0A1026]':''}`} onClick={()=> onSelect(s)}>
              <div className="font-semibold">{s.title || `Chat ${s.id}`}</div>
              <div className="text-sm text-slate-400">{s.preview || 'No messages yet'}</div>

              <button
                aria-label={`Delete chat ${s.id}`}
                onClick={(e)=>{ e.stopPropagation();
                  // Optimistically remove from local list for instant UI feedback
                  setSessions(prev => (prev||[]).filter(x=> x.id !== s.id));
                  try{ sessionStorage.setItem('visitor_chats', JSON.stringify((sessions||[]).filter(x=> x.id !== s.id))); }catch(e){}
                  onDelete(s.id);
                }}
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
