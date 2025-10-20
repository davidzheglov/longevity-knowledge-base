"use client";
import React from 'react';
import { Virtuoso } from 'react-virtuoso';
import { motion, useReducedMotion } from 'framer-motion';

type Message = { id: number; role: string; content: string };

export default function ChatWindow({ messages } : { messages: Message[] }){
  const reduce = useReducedMotion();

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
    <div className="p-6 rounded-xl bg-gradient-to-b from-slate-900/40 to-slate-900/20 shadow-inner h-[60vh]">
      {messages.length === 0 ? (
        <div className="text-center text-slate-400 mt-8">No messages yet. Say hi 👋</div>
      ) : (
        <Virtuoso
          data={messages}
          style={{ height: '100%' }}
          itemContent={(index) => (
            <div className="flex w-full">{itemContent(index)}</div>
          )}
        />
      )}
    </div>
  );
}
