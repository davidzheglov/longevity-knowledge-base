"use client";
import React from 'react';
import { motion } from 'framer-motion';

export type Preset = 'fadeUp'|'scale'|'slide';

const presets: Record<Preset, any> = {
  fadeUp: { initial:{ opacity:0, y:8 }, animate:{ opacity:1, y:0 }, exit:{ opacity:0, y:-6 } },
  scale: { initial:{ opacity:0, scale:0.98 }, animate:{ opacity:1, scale:1 }, exit:{ opacity:0, scale:0.99 } },
  slide: { initial:{ x:20, opacity:0 }, animate:{ x:0, opacity:1 }, exit:{ x:-20, opacity:0 } }
};

export default function PageTransition({ preset='fadeUp', children } : { preset?: Preset; children: React.ReactNode }){
  const v = presets[preset];
  return <motion.div initial="initial" animate="animate" exit="exit" variants={{ initial:v.initial, animate:v.animate, exit:v.exit }} transition={{ duration:0.18 }}>{children}</motion.div>;
}
