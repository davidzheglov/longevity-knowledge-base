"use client";
import React, { useEffect, useState } from 'react';
import { motion, useReducedMotion } from 'framer-motion';
import styles from './bubble.module.css';

function renderContent(text: string){
  const parts = text.split(/(```[\s\S]*?```|`[^`]*`)/g).filter(Boolean);
  return parts.map((p,i)=>{
    if (p.startsWith('```') && p.endsWith('```')){
      const inner = p.slice(3,-3).trim();
      return <pre key={i} className={styles.code}><code>{inner}</code></pre>;
    }
    if (p.startsWith('`') && p.endsWith('`')){
      return <code key={i} style={{ background:'rgba(255,255,255,0.02)', padding:'0.12rem 0.28rem', borderRadius:6 }}>{p.slice(1,-1)}</code>;
    }
    return <span key={i}>{p}</span>;
  });
}

export default function ChatBubble({ role='assistant', content='', streaming=false }:{ role?: string; content?: string; streaming?: boolean }){
  const reduce = useReducedMotion();
  const [visible, setVisible] = useState('');

  useEffect(()=>{
    if (!streaming){ setVisible(content); return; }
    let i = 0; const t = setInterval(()=>{ i++; setVisible(content.slice(0,i)); if (i>=content.length) clearInterval(t); }, 12);
    return ()=> clearInterval(t);
  },[content, streaming]);

  return (
    <motion.article layout initial={{ opacity:0, y:6 }} animate={{ opacity:1, y:0 }} transition={{ duration: reduce? 0 : 0.18 }} className={`${styles.wrap}`}>
      <div className={styles.container}>
        {role === 'assistant' ? <div className={styles.leftDot} aria-hidden /> : null}
        <div>
          <div className={`${styles.bubble} ${role==='user'? styles.user: styles.assistant}`}>
            {renderContent(visible)}
          </div>
          <div className={styles.meta}>
            {streaming ? <span className={styles.streaming} aria-hidden /> : <span>{role}</span>}
            <div className={styles.actions}>
              <button className={styles.copyBtn} onClick={()=> navigator.clipboard.writeText(content)}>Copy</button>
            </div>
          </div>
        </div>
      </div>
    </motion.article>
  );
}
"use client";
import React, { useEffect, useState } from 'react';
import { motion, useReducedMotion } from 'framer-motion';
import styles from './bubble.module.css';

function renderContent(text: string){
  const parts = text.split(/(```[\s\S]*?```|`[^`]*`)/g).filter(Boolean);
  return parts.map((p,i)=>{
    if (p.startsWith('```') && p.endsWith('```')){
      const inner = p.slice(3,-3).trim();
      return <pre key={i} className={styles.code}><code>{inner}</code></pre>;
    }
    if (p.startsWith('`') && p.endsWith('`')){
      return <code key={i} style={{ background:'rgba(255,255,255,0.02)', padding:'0.12rem 0.28rem', borderRadius:6 }}>{p.slice(1,-1)}</code>;
    }
    return <span key={i}>{p}</span>;
  });
}

export default function ChatBubble({ role='assistant', content='', streaming=false }:{ role?: string; content?: string; streaming?: boolean }){
  const reduce = useReducedMotion();
  const [visible, setVisible] = useState('');

  useEffect(()=>{
    if (!streaming){ setVisible(content); return; }
    let i = 0; const t = setInterval(()=>{ i++; setVisible(content.slice(0,i)); if (i>=content.length) clearInterval(t); }, 12);
    return ()=> clearInterval(t);
  },[content, streaming]);

  return (
    <motion.article layout initial={{ opacity:0, y:6 }} animate={{ opacity:1, y:0 }} transition={{ duration: reduce? 0 : 0.18 }} className={`${styles.wrap}`}>
      <div className={styles.container}>
        {role === 'assistant' ? <div className={styles.leftDot} aria-hidden /> : null}
        <div>
          <div className={`${styles.bubble} ${role==='user'? styles.user: styles.assistant}`}>
            {renderContent(visible)}
          </div>
          <div className={styles.meta}>
            {streaming ? <span className={styles.streaming} aria-hidden /> : <span>{role}</span>}
            <div className={styles.actions}>
              <button className={styles.copyBtn} onClick={()=> navigator.clipboard.writeText(content)}>Copy</button>
            </div>
          </div>
        </div>
      </div>
    </motion.article>
  );
}
"use client";
import React, { useEffect, useState } from 'react';
import { motion, useReducedMotion } from 'framer-motion';
import styles from './bubble.module.css';

function renderContent(text: string){
  // very small renderer: preserve code fences and inline code
  const parts = text.split(/(```[\s\S]*?```|`[^`]*`)/g).filter(Boolean);
  return parts.map((p,i)=>{
    if (p.startsWith('```') && p.endsWith('```')){
      const inner = p.slice(3,-3).trim();
      return <pre key={i} className={styles.code}><code>{inner}</code></pre>;
    }
    if (p.startsWith('`') && p.endsWith('`')){
      return <code key={i} style={{ background:'rgba(255,255,255,0.02)', padding:'0.12rem 0.28rem', borderRadius:6 }}>{p.slice(1,-1)}</code>;
    }
    return <span key={i}>{p}</span>;
  });
}

export default function ChatBubble({ role='assistant', content='', streaming=false }:{ role?: string; content?: string; streaming?: boolean }){
  const reduce = useReducedMotion();
  const [visible, setVisible] = useState('');

  useEffect(()=>{
    if (!streaming){ setVisible(content); return; }
    let i = 0; const t = setInterval(()=>{ i++; setVisible(content.slice(0,i)); if (i>=content.length) clearInterval(t); }, 12);
    return ()=> clearInterval(t);
  },[content, streaming]);

  return (
    <motion.article layout initial={{ opacity:0, y:6 }} animate={{ opacity:1, y:0 }} transition={{ duration: reduce? 0 : 0.18 }} className={`${styles.wrap}`}>
      <div className={styles.container}>
        {role === 'assistant' ? <div className={styles.leftDot} aria-hidden /> : null}
        <div>
          <div className={`${styles.bubble} ${role==='user'? styles.user: styles.assistant}`}>
            {renderContent(visible)}
          </div>
          <div className={styles.meta}>
            {streaming ? <span className={styles.streaming} aria-hidden /> : <span>{role}</span>}
            <div className={styles.actions}>
              <button className={styles.copyBtn} onClick={()=> navigator.clipboard.writeText(content)}>Copy</button>
            </div>
          </div>
        </div>
      </div>
    </motion.article>
  );
}
"use client";
import React from 'react';
import { motion } from 'framer-motion';

export default function ChatBubble({ role='assistant', content }: { role?: string; content: string }){
  const isUser = role === 'user';
  return (
    <motion.article layout initial={{ opacity:0, y:6 }} animate={{ opacity:1, y:0 }} exit={{ opacity:0 }} className={`p-3 rounded-2xl ${isUser? 'self-end bg-gradient-to-tr from-primary to-accent text-white':'self-start bg-slate-700/60 text-slate-100'}`}>
      <div className="whitespace-pre-wrap">{content}</div>
    </motion.article>
  );
}
