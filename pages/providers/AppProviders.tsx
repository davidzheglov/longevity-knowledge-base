"use client";
import React from 'react';
import { ThemeProvider } from 'next-themes';
import { Toaster } from 'sonner';
import { AnimatePresence, motion, useReducedMotion } from 'framer-motion';
import { useRouter } from 'next/router';

export function AppProviders({ children }:{ children: React.ReactNode }){
  return (
    <ThemeProvider attribute="class" defaultTheme="system">
      <Toaster richColors position="top-right" />
      {children}
    </ThemeProvider>
  );
}

export function PageMotion({ children }:{ children: React.ReactNode }){
  const router = useRouter();
  const reduce = useReducedMotion();

  const variants = {
    initial: { opacity: 0, y: 8, scale: 0.995 },
    enter: { opacity: 1, y: 0, scale: 1 },
    exit: { opacity: 0, y: -6, scale: 0.995 }
  };

  const transition = reduce ? { duration: 0 } : { duration: 0.18, ease: 'easeInOut' } as any;

  return (
    <AnimatePresence mode="wait" initial={false}>
      <motion.div key={router.route} initial="initial" animate="enter" exit="exit" variants={variants} transition={transition} className="w-full">
        {children}
      </motion.div>
    </AnimatePresence>
  );
}

export default AppProviders;
