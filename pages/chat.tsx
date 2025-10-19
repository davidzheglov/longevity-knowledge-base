"use client";

import { useEffect, useState } from 'react';
import Sidebar from '@/components/sidebar/Sidebar';
import ChatList from '@/components/chat/ChatList';
import ChatWindow from '@/components/chat/ChatWindow';
import MessageInput from '@/components/chat/MessageInput';
import ProfilePanel from '@/components/chat/ProfilePanel';

type Chat = { id: number; title?: string };
type Message = { id: number; role: string; content: string };

export default function ChatPage(){
  const [chats, setChats] = useState<Chat[]>([]);
  const [activeChat, setActiveChat] = useState<Chat | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [profile, setProfile] = useState({ name: 'Alex Johnson', bio: 'Lifelong learner. Building cool apps.', education: 'MSc Computer Science', avatarUrl: '' });
  const [me, setMe] = useState<any>(null);
  const [thinking, setThinking] = useState(false);

  useEffect(()=>{ fetch('/api/auth/me').then(r=>r.json()).then(d=>{ if (d?.user){ setMe(d.user); fetch('/api/profile').then(r=>r.json()).then(p=> setProfile(p.user || profile)).catch(()=>{}); } }); fetch('/api/chats').then(r=>r.json()).then(setChats) },[]);

  useEffect(()=>{
    if (!activeChat) return;
    fetch(`/api/chats/${activeChat.id}/messages`).then(r=>r.json()).then(setMessages);
  },[activeChat]);

  async function createChat(){
    const res = await fetch('/api/chats',{ method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ title: 'New Chat' }) });
    const chat = await res.json();
    setChats((c)=>[chat,...c]);
    setActiveChat(chat);
    setMessages([]);
  }

  async function deleteChat(id:number){
    await fetch(`/api/chats/${id}`,{ method:'DELETE' });
    setChats((c)=>c.filter(x=>x.id!==id));
    if (activeChat?.id===id) setActiveChat(null);
  }

  async function send(){
    if (!activeChat || !input.trim()) return;
    const content = input;
    setInput('');
    const tempId = Date.now();
    const userMsg: Message = { id: tempId, role: 'user', content };
    setMessages((s)=>[...s,userMsg]);

    // If logged in, persist user message
    if (me){
      try{ await fetch(`/api/chats/${activeChat.id}/messages`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ role:'user', content }) }); }catch(e){ console.error(e) }
    }

    // show thinking indicator
    setThinking(true);

    // simulate assistant processing and reply
    setTimeout(async ()=>{
      const reply: Message = { id: Date.now()+1, role: 'assistant', content: 'Received your message' };
      setThinking(false);
      setMessages((s)=>[...s,reply]);

      // persist assistant reply when logged in
      if (me){
        try{ await fetch(`/api/chats/${activeChat.id}/messages`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ role:'assistant', content: reply.content }) }); }catch(e){ console.error(e) }
      }
    }, 900 + Math.random()*600);
  }

  return (
    <div className="min-h-screen">
      <div className="bg-slate-900/30 border-b border-slate-800"><Sidebar/></div>
      <main className="p-6 grid grid-cols-12 gap-6">
        <aside className="col-span-3">
          <ChatList chats={chats} activeId={activeChat?.id||null} onSelect={(c)=>setActiveChat(c)} onCreate={createChat} onDelete={deleteChat} />
        </aside>

        <section className="col-span-6 flex flex-col">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-bold">{activeChat ? (activeChat.title || `Chat ${activeChat.id}`) : 'Welcome'}</h2>
            <div className="text-sm text-slate-400">{activeChat ? `Chat ID: ${activeChat.id}` : ''}</div>
          </div>

          <div className="flex-1">
            {activeChat ? (
              <>
                <ChatWindow messages={messages.concat(thinking? [{ id: -1, role: 'assistant', content: '...' }]:[])} />
                {thinking && <div className="text-sm text-slate-400 mt-2">Assistant is thinking...</div>}
                <MessageInput value={input} onChange={setInput} onSend={send} />
              </>
            ) : (
              <div className="rounded-xl p-8 bg-slate-800/40 h-[60vh] flex items-center justify-center">Select or create a chat to start</div>
            )}
          </div>
        </section>

        <aside className="col-span-3">
          <ProfilePanel profile={profile} />
        </aside>
      </main>
    </div>
  )
}
