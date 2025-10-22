"use client";
import React, { useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const KEY = 'chat_search_mode';

const options = [
  { value: 'database', label: 'Database search' },
  { value: 'article', label: 'Article search' },
];

export default function SearchModeSelect({ value: initial, onChange } : { value?: string; onChange?: (v:string)=>void }){
  const [open, setOpen] = useState(false);
  const [value, setValue] = useState<string>(initial || (typeof window !== 'undefined' ? (localStorage.getItem(KEY) || 'database') : 'database'));
  const rootRef = useRef<HTMLDivElement|null>(null);
  const btnRef = useRef<HTMLButtonElement|null>(null);

  useEffect(()=>{ if (initial) setValue(initial); },[initial]);

  useEffect(()=>{
    function onDoc(e: MouseEvent){ if (!rootRef.current) return; if (!rootRef.current.contains(e.target as Node)) setOpen(false); }
    document.addEventListener('mousedown', onDoc);
    return ()=> document.removeEventListener('mousedown', onDoc);
  },[]);

  function select(v:string){
    setValue(v);
    try{ localStorage.setItem(KEY, v); }catch(e){}
    onChange && onChange(v);
    setOpen(false);
    btnRef.current?.focus();
  }

  function onKeyDown(e: React.KeyboardEvent){
    if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); setOpen(o=>!o); }
    if (e.key === 'Escape') setOpen(false);
  }

  const current = options.find(o=>o.value===value) || options[0];

  return (
    <div ref={rootRef} className="relative inline-block text-left">
      <div className="flex items-center gap-2">
        <label className="text-sm text-slate-300">Search</label>
        <button
          ref={btnRef}
          aria-haspopup="menu"
          aria-expanded={open}
          onKeyDown={onKeyDown}
          onClick={()=> setOpen(o=>!o)}
          className="inline-flex items-center gap-2 rounded-md bg-slate-800/60 px-3 py-2 text-sm hover:bg-slate-800/80 focus:outline-none focus:ring-2 focus:ring-primary"
        >
          <span className="truncate max-w-[10rem]">{current.label}</span>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" className={`transition-transform ${open? 'rotate-180':''}`}>
            <path d="M6 9l6 6 6-6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </button>
      </div>

      <AnimatePresence>
        {open && (
          <motion.ul
            initial={{ opacity: 0, y: -6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -6 }}
            transition={{ duration: 0.18 }}
            role="menu"
            aria-label="Search mode"
            className="absolute right-0 mt-2 w-56 rounded-md bg-slate-900/80 shadow-lg ring-1 ring-black/20 backdrop-blur z-50 overflow-hidden"
          >
            {options.map(opt=> (
              <li key={opt.value} role="menuitem">
                <button
                  onClick={()=> select(opt.value)}
                  className={`w-full text-left px-4 py-2 text-sm hover:bg-slate-800/60 transition-colors ${opt.value===value? 'bg-slate-800/60':''}`}
                >
                  <div className="flex items-center justify-between">
                    <span>{opt.label}</span>
                    {opt.value===value && <span className="text-xs text-primary">Selected</span>}
                  </div>
                </button>
              </li>
            ))}
          </motion.ul>
        )}
      </AnimatePresence>
    </div>
  );
}

