"use client";
import React from 'react';
import { useRouter } from 'next/navigation';
import { motion, useMotionValue, useTransform } from 'framer-motion';

export default function ProteinCard({ symbol, name, aliases, score } : { symbol:string; name:string; aliases?:string[]; score?:number }){
  const router = useRouter();
  const mvX = useMotionValue(0);
  const mvY = useMotionValue(0);
  const rotX = useTransform(mvY, v => v / 8);
  const rotY = useTransform(mvX, v => v / -8);

  return (
    <motion.div onMouseMove={(e)=>{ const r = (e.currentTarget as HTMLElement).getBoundingClientRect(); mvX.set(e.clientX - (r.left + r.width/2)); mvY.set(e.clientY - (r.top + r.height/2)); }} onMouseLeave={()=>{ mvX.set(0); mvY.set(0); }} style={{ rotateX: rotX, rotateY: rotY }} className="p-4 bg-slate-800/40 rounded-xl">
      <div className="flex items-center justify-between">
        <div>
          <div className="font-bold">{symbol}</div>
          <div className="text-sm text-slate-300">{name}</div>
        </div>
        <div className="text-xs">{score ?? '—'}</div>
      </div>
      <div className="mt-3 flex gap-2">
        <button onClick={()=> router.push(`/chat?id=${encodeURIComponent(symbol)}`)} className="px-2 py-1 rounded bg-primary">Open in Chat</button>
      </div>
    </motion.div>
  );
}
