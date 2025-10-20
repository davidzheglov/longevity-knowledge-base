"use client";
import React from 'react';
import DNAField from '@/components/hero/DNAField';

export default function SideDNA(){
  return (
    <div style={{ width: 120, height: 120, pointerEvents: 'none' }}>
      <DNAField anchor="inline" animationPath="/animations/dna3.json" width={120} height={120} />
    </div>
  );
}
