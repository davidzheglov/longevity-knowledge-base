import "@/styles/globals.css";
import type { AppProps } from "next/app";
import { useEffect } from "react";
import { useRouter } from "next/router";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import Navbar from '@/components/nav/Navbar';
import { ThemeProvider } from "next-themes";
import { Inter } from 'next/font/google';

// Use Google-hosted Inter variable font via next/font
const inter = Inter({ subsets: ['latin'], variable: '--font-inter', display: 'swap', weight: ['100','200','300','400','500','600','700','800','900'] });

export default function App({ Component, pageProps }: AppProps) {
  const router = useRouter();
  const shouldReduce = useReducedMotion();

  // No DOM side-effects required; next/font provides a `variable` CSS custom property
  // and `className` that can be used on the root element for consistent typography.

  // Basic motion variants for route transitions. Keep durations short and prefer transform/opacity
  const variants = {
    initial: { opacity: 0, y: 6, scale: 0.995 },
    enter: { opacity: 1, y: 0, scale: 1 },
    exit: { opacity: 0, y: -6, scale: 0.995 }
  };

  // Transition config — honor reduced motion preference
  const transition = shouldReduce ? { duration: 0 } : { duration: 0.18, ease: 'easeInOut' };

  return (
    <ThemeProvider attribute="class" defaultTheme="system">
      {/* AnimatePresence handles mounting/unmounting page transitions. mode="wait" ensures one transition at a time. */}
      <AnimatePresence mode="wait" initial={false}>
        {/* Top navbar */}
        <Navbar />

        <motion.div
          key={router.route}
          initial="initial"
          animate="enter"
          exit="exit"
          variants={variants}
          transition={transition as any}
          className={`${inter.variable} min-h-screen bg-slate-900 text-slate-100 font-sans`}
        >
          {/* main app content */}
          <Component {...pageProps} />
        </motion.div>
      </AnimatePresence>
    </ThemeProvider>
  );
}

/*
Usage notes / tips:
- This file adds global route transitions using Framer Motion's AnimatePresence. Each page will fade/slide slightly.
- The transition honors the user's "prefers-reduced-motion" via `useReducedMotion`.
- We wrap the app with `next-themes` ThemeProvider (attribute="class") so you can use dark/light themes via CSS classes.
- The font import uses `next/font/local` for a variable font — add the font file under `public/fonts/` or change the path.

Install the required packages before running the app if you haven't already:
  npm install framer-motion next-themes

Optional (recommended):
  npm install @radix-ui/react-* shadcn/ui lucide-react react-virtuoso

Accessibility:
- Transitions are short (≈180ms) and use transform+opacity for performant animations.
- Users who prefer reduced motion will see no transitions.

*/
