"use client";
import React, { useEffect, useState } from 'react';
import DNAField from './DNAField';
import DNAToggle from './DNAToggle';
import MagneticButton from '@/components/ui/MagneticButton';
import styles from '@/styles/hero.module.css';
import { motion } from 'framer-motion';
import { MessageSquare } from 'lucide-react';
import Link from 'next/link';

export default function Hero(){
  const [showCTA, setShowCTA] = useState(false);
  useEffect(()=>{ const t = setTimeout(()=> setShowCTA(true), 800); return ()=>clearTimeout(t); },[]);

  const title = 'Longevity LLM';

  return (
    <section className={styles.hero}>

      <div className={styles.heroInner}>
        <h1 className={styles.title} aria-label={title}>
          {title.split('').map((ch, i)=> (
            <motion.span key={i} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y:0 }} transition={{ delay: i * 0.03 }} className={styles.titleChar}>{ch}</motion.span>
          ))}
        </h1>
        <p className={styles.subtitle}>Aging protein intelligence by Elephant Labs</p>

        <div className="mt-6 flex items-center gap-4 justify-center">
          <Link href="/chat">
            <motion.button
              className="px-6 py-3 bg-blue-600 text-white rounded-lg font-medium flex items-center gap-2 transition-all"
               whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}>
              Open Chat</motion.button>
          </Link>
          <Link href="/proteins">
            <motion.button
              className="px-6 py-3 bg-transparent border border-slate-600 text-slate-300 rounded-lg font-medium flex items-center gap-2 transition-all hover:border-slate-400 hover:text-white cursor-pointer"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M7 2v4h10V2" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M8 6v9.5a4 4 0 0 0 4 4h0a4 4 0 0 0 4-4V6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              Browse Proteins</motion.button>
          </Link>
        </div>

        {showCTA && <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }} className="text-sm text-slate-300 mt-4">Start exploring — remember to sign in to save history.</motion.div>}
      </div>

      <div className={styles.rightSlot}>
        <DNAToggle />
      </div>
    </section>
  );
}
