"use client";
import React, { useState, useRef, useEffect } from 'react';
import styles from './navbar.module.css';
import MagneticButton from '@/components/ui/MagneticButton';
import { Layers, GitBranch, FileText, MessageSquare } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import CommandPalette, { openCommandPalette } from '@/components/CommandPalette';
import Link from 'next/link';

const proteins = [ 'SIRT1','mTOR','FOXO3','AMPK','IGF1', 'GLP-1' ];

export default function Navbar(){
  const [megaOpen, setMegaOpen] = useState(false);
  const proteinsRef = useRef<HTMLDivElement|null>(null);

  // Hover/focus open/close
  useEffect(()=>{
    const el = proteinsRef.current; if (!el) return;
    const onEnter = ()=> setMegaOpen(true);
    const onLeave = ()=> setMegaOpen(false);
    el.addEventListener('mouseenter', onEnter);
    el.addEventListener('mouseleave', onLeave);
    el.addEventListener('focusin', onEnter);
    el.addEventListener('focusout', onLeave);
    return ()=>{ el.removeEventListener('mouseenter', onEnter); el.removeEventListener('mouseleave', onLeave); el.removeEventListener('focusin', onEnter); el.removeEventListener('focusout', onLeave); };
  },[]);

  // keyboard: open palette on Cmd/Ctrl+K
  useEffect(()=>{
    function onKey(e: KeyboardEvent){ if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase()==='k'){ e.preventDefault(); openCommandPalette(); } }
    window.addEventListener('keydown', onKey);
    return ()=> window.removeEventListener('keydown', onKey);
  },[]);

  return (
    <>
      <nav className={styles.navbar}>
        <div className={styles.inner}>
          <Link href="/" className={styles.brand}>Elephant Labs</Link>

          <div className={styles.actions}>
            <MagneticButton variant="primary" href="/chat" icon={<MessageSquare size={14}/>}>Chat</MagneticButton>
            <div ref={proteinsRef} tabIndex={0} style={{ position:'relative' }}>
              <MagneticButton variant="ghost" href="/proteins" icon={<Layers size={14}/>}>Proteins</MagneticButton>
                {megaOpen && (
                  <motion.div className={styles.mega} initial={{ opacity:0, scale:0.96 }} animate={{ opacity:1, scale:1 }} exit={{ opacity:0, scale:0.96 }} transition={{ duration: 0.18 }}>
                    <div className={styles.megaGrid}>
                      {proteins.map(p=> (
                        <div key={p} className={styles.tile} tabIndex={0} role="button" onClick={()=> window.location.href = `/proteins/${p}`}> 
                          <div style={{ fontWeight:600 }}>{p}</div>
                          <div style={{ fontSize:12, color:'rgba(200,200,210,0.7)' }}>Explore knowledge for {p}</div>
                        </div>
                      ))}
                    </div>
                  </motion.div>
                )}
            </div>

            <MagneticButton variant="ghost" href="/manifesto" icon={<FileText size={14}/>}>Manifesto</MagneticButton>
            <MagneticButton variant="ghost" href="/about" icon={<GitBranch size={14}/>}>About</MagneticButton>
          </div>

          <div className={styles.spacer} />

          <div className={styles.cmd}>
            <MagneticButton variant="glass" onClick={()=> openCommandPalette()} icon={<GitBranch size={14}/>}>⌘K</MagneticButton>
          </div>
        </div>
      </nav>
      <CommandPalette />
    </>
  );
}
