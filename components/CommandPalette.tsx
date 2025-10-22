"use client";
import React, { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';

let opener: (()=>void) | null = null;
export function openCommandPalette(){ if (opener) opener(); }

export default function CommandPalette(){
  const [open, setOpen] = useState(false);
  const [index, setIndex] = useState(0);
  const ref = useRef<HTMLDivElement|null>(null);
  const items = ['New Chat','Browse Proteins','Manifesto','Toggle Theme','Keyboard Shortcuts'];

  useEffect(()=>{ opener = ()=> setOpen(s=>!s); return ()=> { if (opener) opener=null; } },[]);

  useEffect(()=>{
    function onKey(e: KeyboardEvent){
      const mod = e.metaKey || e.ctrlKey;
      if (mod && e.key.toLowerCase() === 'k'){ e.preventDefault(); setOpen(s=>!s); }
      if (!open) return;
      if (e.key === 'Escape') setOpen(false);
      if (e.key === 'ArrowDown'){ e.preventDefault(); setIndex(i=> Math.min(i+1, items.length-1)); }
      if (e.key === 'ArrowUp'){ e.preventDefault(); setIndex(i=> Math.max(i-1, 0)); }
      if (e.key === 'Enter'){ handleSelect(index); }
    }
    window.addEventListener('keydown', onKey);
    return ()=> window.removeEventListener('keydown', onKey);
  },[open,index]);

  function handleSelect(i:number){ const it = items[i]; setOpen(false); if (it === 'New Chat') window.location.href = '/chat'; if (it === 'Browse Proteins') window.location.href = '/proteins'; if (it === 'Manifesto') window.location.href = '/manifesto'; if (it === 'Toggle Theme'){ const html = document.documentElement; html.classList.toggle('dark'); } if (it === 'Keyboard Shortcuts'){ alert('⌘K to open. Arrow keys to navigate. Enter to select. Esc to close.'); } }

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-24">
      <div className="absolute inset-0 bg-black/50" onClick={()=> setOpen(false)} />
      <motion.div initial={{ opacity:0, scale:0.98 }} animate={{ opacity:1, scale:1 }} transition={{ duration:0.14 }} ref={ref} className="w-[min(720px,90vw)] bg-slate-800/70 backdrop-blur-md rounded-xl p-4">
        <input autoFocus placeholder="Type a command... (⌘K)" className="w-full p-3 rounded bg-slate-900/40" />
        <div className="mt-3 grid gap-2">
          {items.map((it,i)=> (
            <button key={it} className={`p-2 text-left ${i===index? 'bg-slate-700/40 rounded' : ''}`} onClick={()=> handleSelect(i)}>{it}</button>
          ))}
        </div>
      </motion.div>
    </div>
  );
}
