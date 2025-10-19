"use client";
import React, { useState } from 'react';

type Profile = { name?: string; avatarUrl?: string; bio?: string; education?: string };

export default function ProfilePanel({ profile }:{ profile:Profile }){
  const [edit, setEdit] = useState(false);
  const [form, setForm] = useState<Profile>(profile || {});
  const [saving, setSaving] = useState(false);

  async function onSave(){
    setSaving(true);
    try{
      await fetch('/api/profile', { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(form) });
      setEdit(false);
    }catch(e){ console.error(e) }
    setSaving(false);
  }

  async function onFile(e: React.ChangeEvent<HTMLInputElement>){
    const f = e.target.files && e.target.files[0];
    if (!f) return;
    const reader = new FileReader();
    reader.onload = async ()=>{
      const dataUrl = reader.result as string;
      // store avatar as data URL via profile PUT
      setForm((s)=>({ ...s, avatarUrl: dataUrl }));
    };
    reader.readAsDataURL(f);
  }

  return (
    <div className="w-80 p-4 rounded-xl bg-slate-800/40 backdrop-blur-md shadow-lg">
      <div className="flex items-center gap-4">
        <div className="w-16 h-16 rounded-full overflow-hidden bg-gradient-to-br from-primary to-accent flex items-center justify-center text-xl font-bold">
          {form?.avatarUrl ? <img src={form.avatarUrl} alt="avatar" className="w-16 h-16 object-cover"/> : (form.name ? form.name[0] : 'U') }
        </div>
        <div className="flex-1">
          {!edit ? (
            <>
              <div className="font-semibold">{form?.name || 'Unknown User'}</div>
              <div className="text-sm text-slate-300">{form?.education || 'No education info'}</div>
            </>
          ) : (
            <input className="w-full rounded bg-slate-900/40 p-1 text-slate-100" value={form.name||''} onChange={e=>setForm({...form, name: e.target.value})} />
          )}
        </div>
      </div>

      <div className="mt-3 text-sm text-slate-200">{!edit ? (form?.bio || 'This user has no bio yet. You can add something interesting here.') : (
        <textarea className="w-full rounded bg-slate-900/40 p-2 text-slate-100" value={form.bio||''} onChange={e=>setForm({...form, bio: e.target.value})} />
      )}</div>

      <div className="mt-3 flex items-center justify-between">
        {!edit ? (
          <div className="text-sm text-slate-400">Want to keep your history? Log in.</div>
        ) : (
          <input className="rounded bg-slate-900/40 p-1 text-slate-100" placeholder="Education" value={form.education||''} onChange={e=>setForm({...form, education: e.target.value})} />
        )}
      </div>

      <div className="mt-3 flex items-center justify-between gap-2">
        <label className="text-xs bg-slate-700/40 px-2 py-1 rounded cursor-pointer">
          Upload
          <input type="file" accept="image/*" onChange={onFile} className="hidden" />
        </label>
        <div className="flex items-center gap-2">
          {!edit ? (
            <button onClick={()=>setEdit(true)} className="text-sm bg-primary px-3 py-1 rounded-full">Edit</button>
          ) : (
            <>
              <button onClick={onSave} disabled={saving} className="text-sm bg-accent px-3 py-1 rounded-full">{saving? 'Saving...' : 'Save'}</button>
              <button onClick={()=>{ setEdit(false); setForm(profile); }} className="text-sm text-slate-400 px-3 py-1">Cancel</button>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
