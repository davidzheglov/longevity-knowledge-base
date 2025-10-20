"use client";
import React, { useEffect, useState } from 'react';
import MagneticButton from '@/components/ui/MagneticButton';

type Profile = { id?: string; email?: string; name?: string; avatarUrl?: string; bio?: string; education?: string };

export default function ProfilePanel({ profile: initialProfile, onUpdated }:{ profile?: Profile; onUpdated?: (p:Profile)=>void }){
  const [loading, setLoading] = useState(true);
  const [profile, setProfile] = useState<Profile | null>(initialProfile || null);
  const [edit, setEdit] = useState(false);
  const [form, setForm] = useState<Profile>({} as Profile);
  const [saving, setSaving] = useState(false);

  useEffect(()=>{
    let mounted = true;
    async function load(){
      try{
        const meRes = await fetch('/api/auth/me', { credentials: 'include' });
        const meJson = await meRes.json();
        if (meJson?.user){
          const pRes = await fetch('/api/profile', { credentials: 'include' });
          const pJson = await pRes.json();
          if (!mounted) return;
          setProfile(pJson.user || { id: meJson.user.id, name: meJson.user.name, email: meJson.user.email });
          setForm(pJson.user || { id: meJson.user.id, name: meJson.user.name, email: meJson.user.email });
        } else {
          if (!mounted) return;
          setProfile(null);
        }
      }catch(e){ setProfile(null); }
      if (mounted) setLoading(false);
    }
    load();
    return ()=> { mounted = false; };
  },[]);

  async function onSave(){
    setSaving(true);
    try{
      const res = await fetch('/api/profile', { method: 'PUT', credentials: 'include', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(form) });
      if (res.ok){
        const j = await res.json();
        setProfile(j.user || form);
        onUpdated && onUpdated(j.user || form);
        setEdit(false);
      }
    }catch(e){ console.error(e) }
    setSaving(false);
  }

  async function onLogout(){
    try{
      await fetch('/api/auth/logout', { method: 'POST', credentials: 'include' });
      setProfile(null);
      onUpdated && onUpdated(null as any);
      window.location.href = '/';
    }catch(e){ console.error(e) }
  }

  async function onDeleteAccount(){
    if (!profile?.email) return;
    const confirm = window.prompt(`Type your email (${profile.email}) to confirm deletion`);
    if (confirm !== profile.email) return;
    try{
      await fetch('/api/auth/delete', { method: 'POST', credentials: 'include' });
      // logged-out state
      setProfile(null);
      onUpdated && onUpdated(null as any);
    }catch(e){ console.error(e) }
  }

  function onFile(e: React.ChangeEvent<HTMLInputElement>){
    const f = e.target.files && e.target.files[0];
    if (!f) return;
    const reader = new FileReader();
    reader.onload = ()=>{ const dataUrl = reader.result as string; setForm(s=> ({ ...s, avatarUrl: dataUrl })); };
    reader.readAsDataURL(f);
  }

  if (loading) return <div className="w-80 p-4 rounded-xl bg-slate-800/40">Loading…</div>;

  if (!profile) {
    return (
      <div className="w-80 p-6 rounded-xl bg-slate-800/40 text-center">
        <div className="mb-3 font-semibold">Not signed in</div>
        <div className="text-sm text-slate-400 mb-4">Log in to save your chats and profile.</div>
        <MagneticButton onClick={()=> window.location.href = '/login'} variant="primary">Log in</MagneticButton>
      </div>
    );
  }

  return (
    <div className="w-80 p-4 rounded-xl bg-slate-800/40 backdrop-blur-md shadow-lg">
      <div className="flex items-center gap-4">
        <div className="w-16 h-16 rounded-full overflow-hidden bg-gradient-to-br from-primary to-accent flex items-center justify-center text-xl font-bold">
          {profile.avatarUrl ? <img src={profile.avatarUrl} alt="avatar" className="w-16 h-16 object-cover"/> : (profile.name ? profile.name[0] : 'U') }
        </div>
        <div className="flex-1">
          {!edit ? (
            <>
              <div className="font-semibold">{profile.name || 'Unknown User'}</div>
              <div className="text-sm text-slate-300">{profile.education || 'No education info'}</div>
            </>
          ) : (
            <input className="w-full rounded bg-slate-900/40 p-1 text-slate-100" value={form.name||''} onChange={e=>setForm({...form, name: e.target.value})} />
          )}
        </div>
      </div>

      <div className="mt-3 text-sm text-slate-200">{!edit ? (profile.bio || 'This user has no bio yet.') : (
        <textarea className="w-full rounded bg-slate-900/40 p-2 text-slate-100" value={form.bio||''} onChange={e=>setForm({...form, bio: e.target.value})} />
      )}</div>

      <div className="mt-3 flex items-center justify-between">
        {!edit ? (
          <div className="text-sm text-slate-400">Manage your account and chat history here.</div>
        ) : (
          <input className="rounded bg-slate-900/40 p-1 text-slate-100" placeholder="Education" value={form.education||''} onChange={e=>setForm({...form, education: e.target.value})} />
        )}
      </div>

      <div className="mt-3 flex items-center justify-between gap-2">
        {!edit ? (
          <button 
            onClick={onLogout}
            className="text-xs bg-slate-700/40 px-2 py-1 rounded cursor-pointer hover:bg-slate-600/40 transition-colors"
          >
            Logout
          </button>
        ) : (
          <label className="text-xs bg-slate-700/40 px-2 py-1 rounded cursor-pointer hover:bg-slate-600/40 transition-colors">
            Change Avatar
            <input type="file" accept="image/*" onChange={onFile} className="hidden" />
          </label>
        )}
        <div className="flex items-center gap-2">
          {!edit ? (
            <MagneticButton onClick={()=>{ setEdit(true); setForm(profile); }} variant="primary">Edit</MagneticButton>
          ) : (
            <>
              <MagneticButton onClick={onSave} variant="primary" disabled={saving}>{saving? 'Saving...' : 'Save'}</MagneticButton>
              <button onClick={()=>{ setEdit(false); setForm(profile); }} className="text-sm text-slate-400 px-3 py-1">Cancel</button>
            </>
          )}
        </div>
      </div>

      <div className="mt-3 text-center">
        <button onClick={onDeleteAccount} className="text-xs text-rose-400">Delete account</button>
      </div>
    </div>
  );
}
