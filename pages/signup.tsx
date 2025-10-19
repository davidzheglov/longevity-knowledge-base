"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Sidebar from '@/components/sidebar/Sidebar';
import styles from '@/styles/page.module.css';

export default function SignupPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [name, setName] = useState('');
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    if (password !== confirm) return setError('Passwords do not match');
    const { default: axios } = await import('axios');
    try {
      await axios.post('/api/auth/signup', { email, password, name });
      router.push('/chat');
    } catch (err: any) {
      setError(err?.response?.data?.error || 'Signup failed');
    }
  }

  return (
    <div className={styles.pageContainer}>
      <div className={styles.topStrip}><Sidebar /></div>
      <main className={styles.mainContainer}>
        <h2 style={{color:'#fff'}}>Sign up</h2>
        <form onSubmit={submit} style={{display:'flex',flexDirection:'column',gap:8,width:320}}>
          <input placeholder="Name (optional)" value={name} onChange={e=>setName(e.target.value)} />
          <input placeholder="Email" value={email} onChange={e=>setEmail(e.target.value)} />
          <input placeholder="Password" type="password" value={password} onChange={e=>setPassword(e.target.value)} />
          <input placeholder="Confirm password" type="password" value={confirm} onChange={e=>setConfirm(e.target.value)} />
          <button type="submit">Create account</button>
          {error && <div style={{color:'salmon'}}>{error}</div>}
        </form>
      </main>
    </div>
  )
}
