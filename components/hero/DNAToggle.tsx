"use client";
import React, { useState } from 'react';
import { motion } from 'framer-motion';
import DNAField from './DNAField';

export default function DNAToggle({ initial = '/animations/dna2.json', alt = '/animations/dna3.json' }:{ initial?:string; alt?:string }){
  const [src, setSrc] = useState(initial);
  const [shrunk, setShrunk] = useState(false);

  async function handleClick(){
    // shrink, swap, grow
    setShrunk(true);
    setTimeout(()=>{
      setSrc(prev => prev === initial ? alt : initial);
      setShrunk(false);
    }, 320);
  }

  return (
    <div className="relative w-56 h-56 pointer-events-auto">
      <motion.button aria-label="Toggle DNA" onClick={handleClick} className="absolute inset-0 p-0 border-0 bg-transparent flex items-center justify-center" style={{ cursor: 'pointer' }} whileTap={{ scale: 0.95 }}>
        <motion.div animate={{ scale: shrunk ? 0.6 : 1 }} transition={{ duration: 0.32 }} className="absolute inset-0">
          {/* render a DNAField that fetches the static animation file from the provided path */}
          <DNAField anchor="full" animationPath={src} />
        </motion.div>
      </motion.button>
    </div>
  );
}
