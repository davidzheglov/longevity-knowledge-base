"use client";
import React, { useEffect, useRef, useState } from 'react';
import Sidebar from '@/components/sidebar/Sidebar';
import ChatList from '@/components/chat/ChatList';
import ChatWindow from '@/components/chat/ChatWindow';
import Composer from '@/components/chat/Composer';
import ProfilePanel from '@/components/chat/ProfilePanel';
import ArtifactsPanel, { Artifact as ArtifactType } from '@/components/chat/ArtifactsPanel';
import DNAField from '@/components/hero/DNAField';
import styles from '@/components/chat/chat.module.css';
import { motion } from 'framer-motion';
import { toast } from 'sonner';
import SearchModeSelect from '@/components/chat/SearchModeSelect';

export default function ChatPage(){
  type Artifact = ArtifactType;
  type ChatMessage = { id: number; role: 'user' | 'assistant'; content: string; artifacts?: ArtifactType[]; tools?: string[]; thinking?: boolean };
  type ChatSession = { id: string | number; title?: string; preview?: string; _optimistic?: boolean };

  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [active, setActive] = useState<ChatSession|null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const composerRef = useRef<any>(null);
  const [me, setMe] = useState<any>(null);
  const [meResolved, setMeResolved] = useState<boolean>(false);

  useEffect(()=>{ (async ()=>{
    try{
      const r = await fetch('/api/auth/me', { credentials: 'include' });
      const d = await r.json().catch(()=> ({}));
      if (d?.user) setMe(d.user);
    }catch(e){} finally { setMeResolved(true); }
  })(); },[]);

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

  function sessionKeyFor(s: ChatSession){
    return `chat-${String(s.id)}`;
  }

  async function loadMessagesForSession(s: ChatSession){
    // Load from DB for authenticated users; from sessionStorage for guests
    const sid = s.id;
    if (me && me.id && typeof sid === 'number'){
      try{
        const r = await fetch(`/api/chats/${sid}/messages`, { credentials: 'include' });
        if (!r.ok) throw new Error('Failed to load messages');
        const list = await r.json();
        const mapped: ChatMessage[] = (Array.isArray(list)? list:[]).map((m:any)=>{
          let artifacts: Artifact[] | undefined = undefined;
          let tools: string[] | undefined = undefined;
          try{
            if (m?.metadata){
              const meta = JSON.parse(m.metadata);
              if (Array.isArray(meta?.artifacts)) artifacts = meta.artifacts;
              if (Array.isArray(meta?.tools)) tools = meta.tools;
            }
          }catch(e){}
          return { id: m.id, role: (m.role==='assistant'?'assistant':'user'), content: m.content || '', artifacts, tools } as ChatMessage;
        });
        setMessages(mapped);
        return;
      }catch(e){ /* fallback to empty */ }
    } else {
      try{
        const raw = sessionStorage.getItem(`visitor_messages_${sessionKeyFor(s)}`);
        const arr = raw ? JSON.parse(raw) as ChatMessage[] : [];
        setMessages(arr);
        return;
      }catch(e){ setMessages([]); }
    }
    setMessages([]);
  }

  async function createSession(): Promise<ChatSession>{
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
      try{
        const r = await fetch('/api/chats', { method: 'POST', headers: { 'Content-Type': 'application/json' }, credentials: 'include', body: JSON.stringify({ title: s.title }) });
        if (r.ok){
          const data = await r.json();
          const created: ChatSession = (data && (data.id ? data : data.chat)) || s;
          setSessions((prev: ChatSession[]) => [created, ...prev.filter((x)=> x.id !== tempId)]);
          setActive(created);
          await loadMessagesForSession(created);
          return created;
        }
      }catch(e){/* ignore, keep optimistic */}
    } else {
      try{ sessionStorage.setItem('visitor_chats', JSON.stringify(next)); }catch(e){}
      try{ sessionStorage.setItem(`visitor_messages_${sessionKeyFor(s)}`, JSON.stringify([])); }catch(e){}
    }
    return s;
  }

  function guessTitleFrom(text: string): string{
    const clean = (text || '').replace(/\s+/g, ' ').trim();
    if (!clean) return 'New Session';
    const words = clean.split(' ').slice(0, 10);
    let title = words.join(' ');
    if (title.length > 64) title = title.slice(0, 61) + '…';
    // capitalize first letter
    title = title.charAt(0).toUpperCase() + title.slice(1);
    return title;
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
      try{ sessionStorage.removeItem(`visitor_messages_chat-${String(id)}`);}catch(e){}
      if (active?.id === id) setActive(null);
    }
  }

  async function onSend(text: string){
    try { console.log('[chat] onSend start', { len: text?.length, active: active?.id }); } catch {}
    // If no active session, create one first
    let session = active;
    if (!session){
      // Try to resolve auth before first send to avoid temp sessions for logged-in users
      if (!meResolved){
        try{
          const r = await fetch('/api/auth/me', { credentials: 'include' });
          const d = await r.json().catch(()=> ({}));
          if (d?.user) setMe(d.user);
        }catch(e){} finally { setMeResolved(true); }
      }
      session = await createSession();
      try { console.log('[chat] created session', session); } catch {}
    }
  const userMsgId = Date.now();
  const userMsg: ChatMessage = { id: userMsgId, role: 'user', content: text };
  const pendingId = userMsgId + 1;
  setMessages((m: ChatMessage[]) => [...m, userMsg, { id: pendingId, role: 'assistant', content: '', thinking: true }]);

    // Persist user message if authenticated; else cache for guest
    const sid = (session as ChatSession).id;
    if (me && me.id && typeof sid === 'number'){
      fetch(`/api/chats/${sid}/messages`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, credentials: 'include', body: JSON.stringify({ role: 'user', content: text, metadata: JSON.stringify({}) }) }).catch(()=>{});
    } else {
      try{
        const key = `visitor_messages_${sessionKeyFor(session as ChatSession)}`;
        const raw = sessionStorage.getItem(key);
        const arr = raw ? JSON.parse(raw) : [];
        arr.push(userMsg);
        sessionStorage.setItem(key, JSON.stringify(arr));
      }catch(e){}
    }

    // If this is the first message of the session, set a reasonable title
    if (!session?.preview || session?._optimistic || session?.title === 'New Session'){
      const newTitle = guessTitleFrom(text);
      const sid = session!.id;
      setSessions((list: ChatSession[]) => list.map((s) => s.id===sid ? ({...s, title: newTitle}) : s));
      if (me && me.id && typeof sid === 'number'){
        // fire-and-forget
        fetch(`/api/chats/${sid}`, { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, credentials: 'include', body: JSON.stringify({ title: newTitle }) }).catch(()=>{});
      } else {
        // store guest list
        try{ sessionStorage.setItem('visitor_chats', JSON.stringify(sessions.map((s: ChatSession) => s.id===sid? ({...s, title: newTitle}) : s))); }catch(e){}
      }
    }
    try{
      const agentSessionId = sessionKeyFor(session as ChatSession);
      const resp = await fetch('/api/agent/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, sessionId: agentSessionId })
      });
      try { console.log('[chat] /api/agent/chat status', resp.status); } catch {}
      if (!resp.ok){
        const err = await resp.json().catch(()=>({error:'failed'}));
        toast.error('Agent error: ' + (err?.error || resp.statusText));
        setMessages((m: ChatMessage[]) => m.map((mm)=> mm.id===pendingId? ({ ...mm, thinking:false, content:'Sorry, I had an issue processing that.' }) : mm));
        return;
      }
  const data = await resp.json();
  try { console.log('[chat] agent data', { hasOutput: typeof data?.output === 'string', artifacts: Array.isArray(data?.artifacts) ? data.artifacts.length : 0 }); } catch {}
  const content = (data?.output as string) || 'No output';
  const artifacts: Artifact[] = Array.isArray(data?.artifacts) ? data.artifacts : [];
  const tools: string[] = Array.isArray(data?.tools_used) ? data.tools_used : [];
  setMessages((m: ChatMessage[]) => m.map((mm)=> mm.id===pendingId ? ({ ...mm, thinking:false, content, artifacts, tools }) : mm));
      // Persist assistant message if authenticated; else cache for guest
      if (me && me.id && typeof sid === 'number'){
        const metadata = { artifacts, tools };
        fetch(`/api/chats/${sid}/messages`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, credentials: 'include', body: JSON.stringify({ role: 'assistant', content, metadata: JSON.stringify(metadata) }) }).catch(()=>{});
      } else {
        try{
          const key = `visitor_messages_${sessionKeyFor(session as ChatSession)}`;
          const raw = sessionStorage.getItem(key);
          const arr: ChatMessage[] = raw ? JSON.parse(raw) : [];
          arr.push({ id: pendingId, role: 'assistant', content, artifacts, tools });
          sessionStorage.setItem(key, JSON.stringify(arr));
        }catch(e){}
      }
      // update session preview/title optimistically
      const sid2 = (session as ChatSession).id;
      setSessions((list: ChatSession[]) => list.map((s) => s.id===sid2 ? ({...s, preview: content.slice(0,120)}) : s));
      if (!me || !me.id){
        try{ sessionStorage.setItem('visitor_chats', JSON.stringify(sessions.map((s: ChatSession) => s.id===sid2? ({...s, preview: content.slice(0,120)}) : s))); }catch(e){}
      }
    }catch(e:any){
      try { console.error('[chat] network error', e); } catch {}
      toast.error('Network error talking to agent');
      setMessages((m: ChatMessage[]) => m.map((mm)=> mm.id===pendingId ? ({ ...mm, thinking:false, content:'Network error talking to agent.' }) : mm));
    }
  }

  return (
    <div className="min-h-screen">
      <div className="bg-slate-900/30 border-b border-slate-800"><Sidebar/></div>
      <main className={styles.page}>
        <aside className={styles.left}>
          <div className="p-4">
            <div className={styles.breadcrumb}>Home / Chat</div>
            <ChatList sessions={sessions} activeId={active?.id||null} onSelect={async (s:any)=>{ setActive(s); await loadMessagesForSession(s); }} onCreate={createSession} onNewFocus={()=> composerRef.current?.focus?.()} onDelete={deleteSession} />
          </div>
        </aside>

        <section className={styles.center}>
          <motion.div className={styles.topbar} initial={{ opacity:0, y:6 }} animate={{ opacity:1, y:0 }} transition={{ duration:0.2 }}>
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold">{active ? active.title : 'Welcome'}</h2>
              <SearchModeSelect onChange={(v)=> console.log('search mode', v)} />
            </div>
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

            {/* Session-wide artifacts list */}
            {(() => {
              const all: Artifact[] = [];
              for (const m of messages){
                if (m.role === 'assistant' && Array.isArray(m.artifacts)){
                  for (const a of m.artifacts){
                    if (a && !all.find((x)=> x.id === a.id)) all.push(a);
                  }
                }
              }
              return <ArtifactsPanel artifacts={all} />;
            })()}
          </div>
        </aside>
      </main>
    </div>
  );
}
