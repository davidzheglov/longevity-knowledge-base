"use client";
import React, { useEffect, useRef, useState } from 'react';
import { motion, useMotionValue, useSpring } from 'framer-motion';

type Props = { accentColor?: string; onSpeedChange?: (s:number)=>void; animationPath?: string; width?: string | number; height?: string | number };

export default function DNAField({ accentColor = '#7c3aed', onSpeedChange, animationPath = '/animations/dna.json', anchor = 'full', width, height }: Props & { anchor?: 'full'|'right'|'inline' }){
  const rotate = useMotionValue(0);
  const [speed, setSpeed] = useState(1);
  const smooth = useSpring(rotate, { stiffness: 120, damping: 18 });
  const ref = useRef<HTMLDivElement|null>(null);

  // Lottie dynamic load
  const [lottieData, setLottieData] = useState<any|null>(null);
  const lottieRef = useRef<any>(null);
  const [LottieComponent, setLottieComponent] = useState<any|null>(null);

  useEffect(()=>{ if (onSpeedChange) onSpeedChange(speed); },[speed]);

  useEffect(()=>{
    let raf: number;
    const tick = ()=>{ rotate.set(rotate.get() + 0.03 * speed); raf = requestAnimationFrame(tick); };
    raf = requestAnimationFrame(tick);
    return ()=> cancelAnimationFrame(raf);
  },[speed]);

  useEffect(()=>{
    // try to fetch lottie JSON if present in public/animations/dna.json
    let mounted = true;
    (async ()=>{
      try{
        const res = await fetch(animationPath);
        if (!res.ok) return;
        const data = await res.json();
        if (!mounted) return;
        setLottieData(data);
        // dynamic import lottie-react only when needed
        try{
          const mod = await import('lottie-react');
          setLottieComponent(()=> mod.default);
        }catch(e){
          console.warn('lottie-react not available', e);
        }
      }catch(e){
        // file missing or parse error — keep fallback
      }
    })();
    return ()=>{ mounted = false; };
  },[]);

  // when speed changes, apply to lottie if present
  useEffect(()=>{
    if (lottieRef.current && typeof lottieRef.current.setSpeed === 'function'){
      try{ lottieRef.current.setSpeed(speed); }catch(e){}
    }
  },[speed]);

  function onEnter(){ setSpeed(s=>Math.min(6, s + 2)); }
  function onLeave(){ setSpeed(1); }

  // Positioning variants: full-page background, right-side panel, or inline compact
  let wrapperStyle: React.CSSProperties | undefined;
  if (anchor === 'inline'){
    wrapperStyle = { position: 'relative', width: width || 140, height: height || 140, pointerEvents: 'none', zIndex: 0 };
  } else if (anchor === 'right'){
    wrapperStyle = { position:'absolute', right:0, top:0, height:'100%', width:'40vw', pointerEvents: 'none', zIndex: 0 };
  } else {
    wrapperStyle = { position:'absolute', inset:0, pointerEvents: 'none', zIndex: 0 };
  }

  return (
    <div ref={ref} style={wrapperStyle} onMouseEnter={onEnter} onMouseMove={(e)=>{
      // increase speed when cursor moves close to center
      if (!ref.current) return;
      const r = ref.current.getBoundingClientRect();
      const dx = Math.abs(e.clientX - (r.left + r.width/2));
      const dy = Math.abs(e.clientY - (r.top + r.height/2));
      const d = Math.sqrt(dx*dx + dy*dy);
      const norm = Math.max(0, 1 - d / (Math.max(r.width, r.height))); // 0..1
      setSpeed(1 + norm * 5);
    }} onMouseLeave={onLeave} className="absolute inset-0 -z-10 overflow-hidden">

      {LottieComponent && lottieData ? (
        // render Lottie animation
        <div style={{ width: '100%', height: '100%', opacity: anchor === 'inline' ? 0.9 : 0.9 }}>
          <LottieComponent lottieRef={lottieRef} animationData={lottieData} loop={true} autoplay={true} style={{ width: '100%', height: '100%' }} />
        </div>
      ) : (
        <motion.svg style={{ rotate: smooth }} viewBox="0 0 200 200" preserveAspectRatio="xMidYMid slice" className="w-full h-full opacity-30">
          <defs>
            <linearGradient id="g" x1="0" x2="1">
              <stop offset="0%" stopColor={accentColor} stopOpacity="0.9" />
              <stop offset="100%" stopColor="#06b6d4" stopOpacity="0.6" />
            </linearGradient>
          </defs>
          <g fill="none" stroke="url(#g)" strokeWidth="2">
            {/* Helix paths */}
            <path d="M10 10 C60 40, 140 40, 190 10" />
            <path d="M10 190 C60 160, 140 160, 190 190" />
            <path d="M20 30 C60 60, 140 60, 180 30" />
            <path d="M20 170 C60 140, 140 140, 180 170" />
          </g>
        </motion.svg>
      )}
    </div>
  );
}
