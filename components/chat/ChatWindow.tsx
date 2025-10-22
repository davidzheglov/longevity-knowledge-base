"use client";
import React, { useEffect, useRef } from 'react';
import { Virtuoso, VirtuosoHandle } from 'react-virtuoso';
import { motion, useReducedMotion } from 'framer-motion';

type Message = { id: number; role: string; content: string };

export default function ChatWindow({ messages } : { messages: Message[] }){
  const reduce = useReducedMotion();
  const virtuosoRef = useRef<VirtuosoHandle>(null);

  useEffect(() => {
    if (messages.length > 0 && virtuosoRef.current) {
      virtuosoRef.current.scrollToIndex({
        index: messages.length - 1,
        behavior: 'smooth',
        align: 'end'
      });
    }
  }, [messages.length]);

  const itemContent = (index: number) => {
    const m = messages[index];
    const isUser = m.role === 'user';
    const containerClasses = `max-w-[70%] p-3 rounded-2xl shadow-md ${isUser ? 'self-end bg-gradient-to-tr from-primary to-accent text-white' : 'self-start bg-slate-700/60 text-slate-100'}`;

    const motionProps = reduce ? {} : { initial: { opacity: 0, y: 6 }, animate: { opacity: 1, y: 0 }, exit: { opacity: 0, y: -6 }, transition: { duration: 0.18 } };

    return (
      <motion.div {...motionProps} key={m.id} className={containerClasses}>
        <div className="text-sm">{m.content}</div>
        <div className="text-xs text-slate-300 mt-1 opacity-80">{isUser ? 'You' : 'Assistant'}</div>
      </motion.div>
    );
  };

  // If there are few messages or react-virtuoso is not desired, the Virtuoso still performs well.
  return (
    <div className="p-6 rounded-xl bg-gradient-to-b from-slate-900/40 to-slate-900/20 shadow-inner h-[60vh] border border-white/30 custom-scrollbar">
      {messages.length === 0 ? (
        <div className="text-center text-slate-400 mt-8">No messages yet. Say hi 👋</div>
      ) : (
        <Virtuoso
          ref={virtuosoRef}
          data={messages}
          style={{ height: '100%' }}
          initialTopMostItemIndex={messages.length - 1}
          followOutput="smooth"
          itemContent={(index) => (
            <div className="flex w-full">{itemContent(index)}</div>
          )}
        />
      )}

      <style jsx>{`
        .custom-scrollbar :global(*::-webkit-scrollbar) {
          width: 14px;
        }
        
        .custom-scrollbar :global(*::-webkit-scrollbar-track) {
          background: rgba(15, 23, 42, 0.3);
          border-radius: 10px;
        }
        
        .custom-scrollbar :global(*::-webkit-scrollbar-thumb) {
          background: rgba(139, 92, 246, 0.5);
          border-radius: 10px;
        }
        
        .custom-scrollbar :global(*::-webkit-scrollbar-thumb:hover) {
          background: rgba(139, 92, 246, 0.7);
        }
        
        /* Firefox */
        .custom-scrollbar :global(*) {
          scrollbar-width: thin;
          scrollbar-color: rgba(139, 92, 246, 0.5) rgba(15, 23, 42, 0.3);
        }
      `}</style>

    </div>
  );
}
