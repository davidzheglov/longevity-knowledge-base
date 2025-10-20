"use client";
import React from 'react';
import styles from '@/styles/spotlight.module.css';
import { motion } from 'framer-motion';

export type SpotlightItem = { symbol: string; name: string; tags: string[]; sparkline?: number[] };

export default function ProteinSpotlight({ items } : { items?: SpotlightItem[] }){
  const list = items ?? [
    { symbol: 'SIRT1', name:'Sirtuin 1', tags:['longevity','autophagy','DNA repair'], sparkline:[1,2,3,4,5,4,6] },
    { symbol: 'mTOR', name:'mTOR', tags:['growth','metabolism'], sparkline:[5,4,3,4,6,5,7] },
    { symbol: 'FOXO3', name:'FOXO3', tags:['longevity','stress'], sparkline:[2,3,2,5,4,6] },
    { symbol: 'KLOTHO', name:'Klotho', tags:['aging','longevity'], sparkline:[1,3,4,2,5,3] }
  ];

  return (
    <div className={styles.spotlightWrap}>
      <div className={styles.spotlightSnap}>
        {list.map((it,i)=> (
          <motion.article key={it.symbol} className={styles.card} whileHover={{ y: -8, scale: 1.02 }} onHoverStart={()=>{/* could call onSpeedChange to speed DNA */}}>
            <div className={styles.cardHeader}><strong>{it.symbol}</strong> <span className={styles.tagList}>{it.tags.join(' • ')}</span></div>
            <div className={styles.cardBody}>
              <div className={styles.name}>{it.name}</div>
              <div className={styles.sparkline}><Sparkline data={it.sparkline||[]} /></div>
            </div>
            <div className={styles.cardActions}>
              <button className={styles.action}>Open in Chat</button>
              <button className={styles.actionGhost}>See Studies</button>
            </div>
          </motion.article>
        ))}
      </div>
    </div>
  );
}

function Sparkline({ data }:{ data:number[] }){
  const max = Math.max(...data,1);
  const points = data.map((d,i)=> `${i*(100/(Math.max(1,data.length-1)))} ${100 - (d/max*100)}`).join(' ');
  return <svg viewBox='0 0 100 100' className={styles.sparkSVG}><polyline fill='none' stroke='white' strokeWidth={1.5} points={points} strokeOpacity={0.9} /></svg>;
}
