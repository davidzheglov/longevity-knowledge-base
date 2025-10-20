"use client";
import React, { useRef, useEffect, useState } from 'react';
import styles from './magnetic.module.css';
import { motion, useMotionValue, useTransform, useSpring } from 'framer-motion';

export default function MagneticButton({ children, icon, onClick, href, variant = 'primary', ...rest }:
  { children: React.ReactNode; icon?: React.ReactNode; onClick?: ()=>void; href?: string; variant?: 'primary'|'ghost'|'glass' } & any){
  const ref = useRef<HTMLButtonElement|null>(null);
  const [hover, setHover] = useState(false);
  const x = useMotionValue(0);
  const y = useMotionValue(0);
  const sx = useSpring(x, { stiffness: 170, damping: 20 });
  const sy = useSpring(y, { stiffness: 170, damping: 20 });

  useEffect(()=>{
    function onMove(e: MouseEvent){
      const el = ref.current; if (!el) return;
      const r = el.getBoundingClientRect();
      const dx = e.clientX - (r.left + r.width/2);
      const dy = e.clientY - (r.top + r.height/2);
      const dist = Math.sqrt(dx*dx + dy*dy);
      if (dist > 120) { x.set(0); y.set(0); return; }
      const strength = (1 - dist/120) * 8;
      x.set(dx / 10 * strength/8);
      y.set(dy / 10 * strength/8);
    }
    window.addEventListener('mousemove', onMove);
    return ()=> window.removeEventListener('mousemove', onMove);
  },[]);

  const content = (
    <motion.button
      ref={ref}
      onMouseEnter={()=>setHover(true)}
      onMouseLeave={()=>{ setHover(false); x.set(0); y.set(0); }}
      onClick={onClick}
      whileTap={{ scale: 0.98 }}
      style={{ translateX: sx, translateY: sy }}
      className={`${styles.btn} ${styles[variant]} ${hover? styles.glow : ''}`}
      aria-pressed={false}
      {...rest}
    >
      {icon ? <span className={styles.icon} aria-hidden>{icon}</span> : null}
      <span>{children}</span>
    </motion.button>
  );

  if (href){
    return <a href={href} aria-label={String(children)}>{content}</a> as any;
  }
  return content;
}

export const NavButton = (props:any)=> <MagneticButton {...props} variant={props.variant||'ghost'} />;

