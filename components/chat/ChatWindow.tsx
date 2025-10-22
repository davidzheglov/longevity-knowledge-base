"use client";
import React from 'react';
import { Virtuoso } from 'react-virtuoso';
import { motion, useReducedMotion } from 'framer-motion';

type Artifact = { id: string; label?: string; type?: string; path?: string; name?: string; size?: number; url?: string };
type Message = { id: number; role: string; content: string; artifacts?: Artifact[] };

function isImageType(t?: string) {
  const x = (t||'').toLowerCase();
  return ['png','jpg','jpeg','gif','webp','svg'].includes(x);
}

// Minimal Markdown-ish renderer: code fences, inline code, lists, links, paragraphs.
function renderMarkdown(text: string) {
  if (!text) return null;
  // Split into blocks preserving code fences
  const parts = text.split(/(```[\s\S]*?```)/g).filter(Boolean);
  return parts.map((part, idx) => {
    if (part.startsWith("```") && part.endsWith("```")){
      const inner = part.slice(3, -3).replace(/^\n+|\n+$/g, '');
      return (
        <pre key={idx} className="mt-2 mb-2 whitespace-pre overflow-auto rounded bg-black/30 p-3 text-xs">
          <code>{inner}</code>
        </pre>
      );
    }
    // Non-code: build lists and paragraphs
    const lines = part.split(/\r?\n/);
    const nodes: React.ReactNode[] = [];
    let ul: string[] = [];
    let ol: string[] = [];
    let quote: string[] = [];
    const flushUL = () => {
      if (ul.length) {
        nodes.push(
          <ul key={`ul-${idx}-${nodes.length}`} className="list-disc pl-5 my-2">
            {ul.map((li, i) => <li key={i}>{renderInline(li)}</li>)}
          </ul>
        );
        ul = [];
      }
    };
    const flushOL = () => {
      if (ol.length) {
        nodes.push(
          <ol key={`ol-${idx}-${nodes.length}`} className="list-decimal pl-5 my-2">
            {ol.map((li, i) => <li key={i}>{renderInline(li)}</li>)}
          </ol>
        );
        ol = [];
      }
    };
    const flushQuote = () => {
      if (quote.length) {
        nodes.push(
          <blockquote key={`q-${idx}-${nodes.length}`} className="border-l-2 border-white/20 pl-3 my-2 text-slate-200/90">
            {quote.map((l, i) => <p key={i} className="my-1">{renderInline(l)}</p>)}
          </blockquote>
        );
        quote = [];
      }
    };
    function renderInline(s: string){
      // inline code
      const chunks = s.split(/(`[^`]*`)/g).filter(Boolean);
      return chunks.map((c, i) => {
        if (c.startsWith('`') && c.endsWith('`')) {
          return <code key={i} className="bg-white/5 rounded px-1 py-0.5 text-[0.9em]">{c.slice(1,-1)}</code>;
        }
        // links [text](url)
        const linkParts = c.split(/(\[[^\]]+\]\((https?:[^)]+)\))/g).filter(Boolean);
        return linkParts.map((lp, j) => {
          const m = lp.match(/^\[([^\]]+)\]\((https?:[^)]+)\)$/);
          if (m){
            return <a key={`${i}-${j}`} href={m[2]} target="_blank" rel="noreferrer" className="underline text-indigo-300 hover:text-indigo-200">{m[1]}</a>;
          }
          // bold and italics
          const bolded = lp.split(/(\*\*[^*]+\*\*)/g).filter(Boolean).map((bp,k)=>{
            if (/^\*\*[^*]+\*\*$/.test(bp)) return <strong key={k}>{bp.slice(2,-2)}</strong>;
            return bp.split(/(\*[^*]+\*)/g).filter(Boolean).map((ip,kk)=>{
              if (/^\*[^*]+\*$/.test(ip)) return <em key={kk}>{ip.slice(1,-1)}</em>;
              return <React.Fragment key={`${k}-${kk}`}>{ip}</React.Fragment>;
            });
          });
          return <React.Fragment key={`${i}-${j}`}>{bolded}</React.Fragment>;
        });
      });
    }
    for (const line of lines){
      // Horizontal rule
      if (/^\s*(?:-{3,}|_{3,}|\*{3,})\s*$/.test(line)){
        flushUL(); flushOL(); flushQuote();
        nodes.push(<hr key={`hr-${idx}-${nodes.length}`} className="border-white/10 my-3"/>);
        continue;
      }
      // Headings
      const h = line.match(/^\s*(#{1,6})\s+(.*)$/);
      if (h){
        flushUL(); flushOL(); flushQuote();
        const level = Math.min(6, h[1].length);
        const text = h[2];
        const common = "font-semibold mt-3 mb-1";
        if (level <= 2) return nodes.push(<h2 key={`h-${idx}-${nodes.length}`} className={`${common} text-lg`}>{renderInline(text)}</h2>), null;
        if (level === 3) { nodes.push(<h3 key={`h-${idx}-${nodes.length}`} className={`${common} text-base`}>{renderInline(text)}</h3>); continue; }
        nodes.push(<div key={`h-${idx}-${nodes.length}`} className={`${common}`}>{renderInline(text)}</div>);
        continue;
      }
      // Blockquote line
      const q = line.match(/^\s*>\s?(.*)$/);
      if (q){ quote.push(q[1]); continue; }

      // Ordered list item
      if (/^\s*\d+\.\s+/.test(line)){
        flushUL(); flushQuote();
        ol.push(line.replace(/^\s*\d+\.\s+/, ''));
        continue;
      }
      // Unordered list item
      if (/^\s*[-*+•]\s+/.test(line)){
        flushOL(); flushQuote();
        ul.push(line.replace(/^\s*[-*+•]\s+/, ''));
        continue;
      }
      // Blank line
      if (line.trim() === ''){
        flushUL(); flushOL(); flushQuote();
        nodes.push(<div key={`br-${idx}-${nodes.length}`} className="h-2" />);
        continue;
      }
      // Plain paragraph line
      flushUL(); flushOL(); flushQuote();
      nodes.push(<p key={`p-${idx}-${nodes.length}`} className="my-1 leading-relaxed break-words">{renderInline(line)}</p>);
    }
    flushUL(); flushOL(); flushQuote();
    return <div key={idx}>{nodes}</div>;
  });
}

export default function ChatWindow({ messages } : { messages: Message[] }){
  const reduce = useReducedMotion();

  const itemContent = (index: number) => {
    const m = messages[index];
    const isUser = m.role === 'user';
    const containerClasses = `max-w-[70%] p-3 rounded-2xl shadow-md ${isUser ? 'self-end bg-gradient-to-tr from-primary to-accent text-white' : 'self-start bg-slate-700/60 text-slate-100'}`;

    const motionProps = reduce ? {} : { initial: { opacity: 0, y: 6 }, animate: { opacity: 1, y: 0 }, exit: { opacity: 0, y: -6 }, transition: { duration: 0.18 } };

    return (
      <motion.div {...motionProps} key={m.id} className={containerClasses}>
        <div className="text-sm whitespace-pre-wrap">
          {isUser ? m.content : renderMarkdown(m.content)}
        </div>
        {(!isUser && m.artifacts && m.artifacts.length > 0) && (
          <div className="mt-3 flex flex-wrap gap-3">
            {m.artifacts.map((a) => (
              <div key={a.id} className="bg-black/20 rounded-lg p-2 border border-white/10 max-w-xs">
                {isImageType(a.type) && a.url ? (
                  <a href={a.url} target="_blank" rel="noreferrer" title={a.name || a.label}>
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img src={a.url} alt={a.name || a.label || 'artifact'} className="max-w-[240px] max-h-[160px] rounded"/>
                  </a>
                ) : (
                  <a href={a.url || '#'} target="_blank" rel="noreferrer" className="underline">
                    {a.name || a.label || a.id}
                  </a>
                )}
                <div className="text-[10px] text-slate-300 mt-1 opacity-80">
                  {(a.type || '').toUpperCase()} {typeof a.size === 'number' ? `• ${(a.size/1024).toFixed(1)} KB` : ''}
                </div>
              </div>
            ))}
          </div>
        )}
        <div className="text-xs text-slate-300 mt-1 opacity-80">{isUser ? 'You' : 'Assistant'}</div>
      </motion.div>
    );
  };

  // If there are few messages or react-virtuoso is not desired, the Virtuoso still performs well.
  return (
    <div className="p-6 rounded-xl bg-gradient-to-b from-slate-900/40 to-slate-900/20 shadow-inner h-[60vh] border border-white/30">
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
