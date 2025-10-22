"use client";
import React, { useEffect, useRef, useState } from 'react';
import Sidebar from '@/components/sidebar/Sidebar';
import ChatList from '@/components/chat/ChatList';
import ChatWindow from '@/components/chat/ChatWindow';
import Composer from '@/components/chat/Composer';
import ProfilePanel from '@/components/chat/ProfilePanel';
import DNAField from '@/components/hero/DNAField';
import styles from '@/components/chat/chat.module.css';
import { motion } from 'framer-motion';
import { toast } from 'sonner';

export default function ChatPage(){
  type ChatMessage = { id: number; role: 'user' | 'assistant'; content: string };
  type ChatSession = { id: string | number; title?: string; preview?: string; _optimistic?: boolean };

  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [active, setActive] = useState<ChatSession|null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const composerRef = useRef<any>(null);
  const [me, setMe] = useState<any>(null);

  useEffect(()=>{ fetch('/api/auth/me', { credentials: 'include' }).then(r=>r.json()).then(d=>{ if (d?.user) setMe(d.user); }).catch(()=>{}); },[]);

  // load sessions (persisted for logged-in users or sessionStorage for guests)
  useEffect(()=>{
    let mounted = true;
    async function load(){
      try{
        // if we have a logged-in user, fetch persisted chats from the server
        if (me && me.id){
          const res = await fetch('/api/chats', { credentials: 'include' });
          if (!mounted) return;
          if (res.ok){
            const data = await res.json();
            // Accept either an array or { chats: [] }
            const list: ChatSession[] = Array.isArray(data) ? data : (Array.isArray(data?.chats) ? data.chats : []);
            setSessions(list);
          } else {
            const raw = sessionStorage.getItem('visitor_chats');
            setSessions(raw ? (JSON.parse(raw) as ChatSession[]) : []);
          }
        } else {
          // guest: use sessionStorage-only list
          const raw = sessionStorage.getItem('visitor_chats');
          setSessions(raw ? (JSON.parse(raw) as ChatSession[]) : []);
        }
      }catch(err){
        const raw = sessionStorage.getItem('visitor_chats');
        if (!mounted) return;
        setSessions(raw ? (JSON.parse(raw) as ChatSession[]) : []);
      }
    }
    load();
    return ()=> { mounted = false; };
  },[me]);

  function createSession(){
    const tempId = `temp-${Date.now()}`;
    const s: ChatSession = { id: tempId, title: 'New Session', preview: '', _optimistic: true };
    const next: ChatSession[] = [s, ...sessions];
    setSessions(next);
    setActive(s);
    setMessages([]);
    toast.success('New session started');
    // focus composer
    setTimeout(()=> composerRef.current?.focus?.(), 220);

    // persist: if logged in, POST to server; otherwise save to sessionStorage
    if (me && me.id){
      fetch('/api/chats', { method: 'POST', headers: { 'Content-Type': 'application/json' }, credentials: 'include', body: JSON.stringify({ title: s.title }) }).then(async r=>{
        if (!r.ok) throw new Error('create failed');
        const data = await r.json();
        const created: ChatSession = (data && (data.id ? data : data.chat)) || s;
        setSessions((prev: ChatSession[]) => [created, ...prev.filter((x)=> x.id !== tempId)]);
        setActive(created);
      }).catch(()=>{
        // keep optimistic item if server failed
      });
    } else {
      sessionStorage.setItem('visitor_chats', JSON.stringify(next));
    }
  }

  async function deleteSession(id: string | number){
    if (me && me.id){
      try{
        await fetch(`/api/chats/${id}`, { method: 'DELETE', credentials: 'include' });
      }catch(e){}
  setSessions((s: ChatSession[]) => s.filter((x: ChatSession) => x.id !== id));
      if (active?.id === id) setActive(null);
    } else {
  const next: ChatSession[] = sessions.filter((x: ChatSession) => x.id !== id);
      setSessions(next);
      sessionStorage.setItem('visitor_chats', JSON.stringify(next));
      if (active?.id === id) setActive(null);
    }
  }

  async function onSend(text: string){
    if (!active) return;
    const userMsg: ChatMessage = { id: Date.now(), role: 'user', content: text };
    setMessages((m: ChatMessage[]) => [...m, userMsg]);
    try{
      const resp = await fetch('/api/agent/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, sessionId: String(active.id) })
      });
      if (!resp.ok){
        const err = await resp.json().catch(()=>({error:'failed'}));
        toast.error('Agent error: ' + (err?.error || resp.statusText));
        setMessages((m: ChatMessage[]) => [...m,{ id: Date.now()+1, role: 'assistant', content: 'Sorry, I had an issue processing that.' }]);
        return;
      }
      const data = await resp.json();
      const content = (data?.output as string) || 'No output';
      setMessages((m: ChatMessage[]) => [...m, { id: Date.now()+2, role: 'assistant', content }]);
      // update session preview/title optimistically
      setSessions((list: ChatSession[]) => list.map((s) => s.id===active.id ? ({...s, preview: content.slice(0,120)}) : s));
      if (!me || !me.id){
  try{ sessionStorage.setItem('visitor_chats', JSON.stringify(sessions.map((s: ChatSession) => s.id===active.id? ({...s, preview: content.slice(0,120)}) : s))); }catch(e){}
      }
    }catch(e:any){
      toast.error('Network error talking to agent');
      setMessages((m: ChatMessage[]) => [...m,{ id: Date.now()+3, role: 'assistant', content: 'Network error talking to agent.' }]);
    }
  }

  return (
    <div className="min-h-screen">
      <div className="bg-slate-900/30 border-b border-slate-800"><Sidebar/></div>
      <main className={styles.page}>
        <aside className={styles.left}>
          <div className="p-4">
            <div className={styles.breadcrumb}>Home / Chat</div>
            <ChatList sessions={sessions} activeId={active?.id||null} onSelect={(s:any)=>{ setActive(s); setMessages([]); }} onCreate={createSession} onNewFocus={()=> composerRef.current?.focus?.()} onDelete={deleteSession} />
          </div>
        </aside>

        <section className={styles.center}>
          <motion.div className={styles.topbar} initial={{ opacity:0, y:6 }} animate={{ opacity:1, y:0 }} transition={{ duration:0.2 }}>
            <h2 className="text-2xl font-bold">{active ? active.title : 'Welcome'}</h2>
          </motion.div>

          <div className={styles.messages}>
            <ChatWindow messages={messages} />
          </div>

          <div className={styles.composerWrap}>
            <Composer ref={composerRef as any} onSend={onSend} />
          </div>
        </section>

        <aside className={styles.right}>
          <div className="p-4">
            <ProfilePanel profile={{ name: me?.name || 'Guest', bio: me?.bio || 'Log in to see your profile', education: me?.education || '', avatarUrl: me?.avatarUrl || '' }} />

            {/* compact DNA decorative under the profile */}
            <div className="mt-6 flex justify-center">
              <DNAField anchor="inline" animationPath="/animations/dna3.json" width={120} height={120} />
            </div>
          </div>
        </aside>
      </main>
    </div>
  );
}
