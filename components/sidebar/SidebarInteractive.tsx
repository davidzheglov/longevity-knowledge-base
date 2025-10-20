"use client";
import React from 'react';
import { motion } from 'framer-motion';

export default function SidebarInteractive(){
  const sessions = [{id:1,title:'Welcome'}, {id:2,title:'SIRT1 Deep Dive'}];
  return (
    <aside className="w-72 p-4">
      {sessions.map(s=> (
        <motion.div key={s.id} whileHover={{ x:6 }} className="p-2 rounded mb-2 bg-slate-800/40">{s.title}</motion.div>
      ))}
    </aside>
  );
}
