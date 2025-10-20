"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Sidebar from '@/components/sidebar/Sidebar';
import styles from '@/styles/page.module.css';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    const { default: axios } = await import('axios');
    try {
      await axios.post('/api/auth/login', { email, password });
      router.push('/chat');
    } catch (err: any) {
      setError(err?.response?.data?.error || 'Login failed');
    }
  }

  return (
    <div className={styles.pageContainer}>
      <div className={styles.topStrip}><Sidebar /></div>
      <main className={styles.mainContainer}>
        <h2 style={{color:'#fff'}}>Login</h2>
        <form onSubmit={submit} style={{display:'flex',flexDirection:'column',gap:8,width:320}}>
          <input placeholder="Email" value={email} onChange={e=>setEmail(e.target.value)} />
          <input placeholder="Password" type="password" value={password} onChange={e=>setPassword(e.target.value)} />
          <button type="submit">Login</button>
          {error && <div style={{color:'salmon'}}>{error}</div>}
        </form>
      </main>
    </div>
  )
}
