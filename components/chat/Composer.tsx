"use client";
import React, { useEffect, useImperativeHandle, useRef, useState } from 'react';
import { motion, useSpring } from 'framer-motion';
import { MessageSquare } from 'lucide-react';
import MagneticButton from '@/components/ui/MagneticButton';
import ProteinChips from '@/components/chat/ProteinChips';
import styles from './chat.module.css';

type Props = { onSend: (text: string) => void; disabled?: boolean };
type RefHandle = { focus: () => void };

function useAutosize(textareaRef: React.RefObject<HTMLTextAreaElement | null>, value: string) {
  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = '0px';
    el.style.height = Math.min(320, el.scrollHeight) + 'px';
  }, [value, textareaRef]);
}

const Composer = React.forwardRef<RefHandle, Props>(function Composer({ onSend, disabled }: Props, ref) {
  const [text, setText] = useState('');
  const ta = useRef<HTMLTextAreaElement | null>(null);
  useAutosize(ta, text);

  useImperativeHandle(ref, () => ({ focus: () => ta.current?.focus() }));

  const tokenPercent = Math.min(1, text.length / 1000);
  const spring = useSpring(tokenPercent, { stiffness: 120, damping: 18 });

  function send() {
    if (!text.trim()) return;
    onSend(text);
    setText('');
  }

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
        e.preventDefault();
        send();
      }
    }
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [text]);

  const chips = [
    { key: 'SIRT1', prompt: 'Summarize SIRT1 human evidence' },
    { key: 'mTORC1', prompt: 'Summarize mTORC1 human evidence' },
    { key: 'AMPK', prompt: 'Summarize AMPK evidence' },
  ];

  return (
    <div className={styles.composerWrap ?? 'mt-4'}>
      <div className="mb-2 flex gap-2">
        {chips.map((c) => (
          <button
            key={c.key}
            className="px-2 py-1 rounded bg-slate-800/40 text-sm"
            onClick={() => setText((t) => t + (t ? '\n' : '') + c.prompt)}
            title={c.prompt}
          >
            {c.key}
          </button>
        ))}
      </div>

      <ProteinChips onInsert={(s: string) => setText((t) => t + (t ? '\n' : '') + s)} />

      <textarea
        ref={ta}
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Type a message..."
        className="w-full rounded p-3 bg-slate-800/60"
        onKeyDown={(e) => {
          if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
            e.preventDefault();
            send();
          }
        }}
      />

      <div className="mt-2 flex items-center justify-between">
        <div className="w-40 bg-slate-700/30 h-2 rounded overflow-hidden">
          <motion.div style={{ width: `${tokenPercent * 100}%` }} className="h-2 bg-accent" />
        </div>
        <div>
          <MagneticButton onClick={send} variant="primary" disabled={disabled} icon={<MessageSquare size={16} />}>
            Send
          </MagneticButton>
        </div>
      </div>
    </div>
  );
});

export default Composer;
