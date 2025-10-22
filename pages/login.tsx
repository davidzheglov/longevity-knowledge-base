"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import styles from '@/styles/page.module.css';
import { motion } from 'framer-motion';

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
      <main className={styles.mainContainer}>
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center', 
          minHeight: '70vh',
          width: '100%'
        }}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            style={{
              background: 'rgba(15, 23, 42, 0.8)',
              backdropFilter: 'blur(12px)',
              border: '1px solid rgba(100, 116, 139, 0.3)',
              borderRadius: '16px',
              padding: '48px 40px',
              width: '100%',
              maxWidth: '420px',
              boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4)',
            }}
          >
            <motion.h2
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2 }}
              style={{
                color: '#fff',
                fontSize: '32px',
                fontWeight: '600',
                marginBottom: '8px',
                textAlign: 'center',
                margin: '0 0 8px 0',
              }}
            >
              Welcome Back
            </motion.h2>
            
            <p style={{
              color: '#94a3b8',
              fontSize: '14px',
              marginBottom: '32px',
              textAlign: 'center',
              margin: '0 0 32px 0',
            }}>
              Sign in to access Longevity LLM
            </p>

            <form onSubmit={submit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              <div>
                <label style={{
                  display: 'block',
                  color: '#cbd5e1',
                  fontSize: '14px',
                  fontWeight: '500',
                  marginBottom: '8px',
                }}>
                  Email
                </label>
                <input
                  type="email"
                  placeholder="you@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  style={{
                    width: '100%',
                    background: 'rgba(30, 41, 59, 0.6)',
                    border: '1px solid rgba(100, 116, 139, 0.4)',
                    borderRadius: '8px',
                    padding: '12px 16px',
                    color: '#fff',
                    fontSize: '15px',
                    outline: 'none',
                    transition: 'all 0.2s ease',
                    boxSizing: 'border-box',
                  }}
                  onFocus={(e) => {
                    e.target.style.borderColor = '#3b82f6';
                    e.target.style.background = 'rgba(30, 41, 59, 0.9)';
                  }}
                  onBlur={(e) => {
                    e.target.style.borderColor = 'rgba(100, 116, 139, 0.4)';
                    e.target.style.background = 'rgba(30, 41, 59, 0.6)';
                  }}
                />
              </div>

              <div>
                <label style={{
                  display: 'block',
                  color: '#cbd5e1',
                  fontSize: '14px',
                  fontWeight: '500',
                  marginBottom: '8px',
                }}>
                  Password
                </label>
                <input
                  type="password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  style={{
                    width: '100%',
                    background: 'rgba(30, 41, 59, 0.6)',
                    border: '1px solid rgba(100, 116, 139, 0.4)',
                    borderRadius: '8px',
                    padding: '12px 16px',
                    color: '#fff',
                    fontSize: '15px',
                    outline: 'none',
                    transition: 'all 0.2s ease',
                    boxSizing: 'border-box',
                  }}
                  onFocus={(e) => {
                    e.target.style.borderColor = '#3b82f6';
                    e.target.style.background = 'rgba(30, 41, 59, 0.9)';
                  }}
                  onBlur={(e) => {
                    e.target.style.borderColor = 'rgba(100, 116, 139, 0.4)';
                    e.target.style.background = 'rgba(30, 41, 59, 0.6)';
                  }}
                />
              </div>

              {error && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  style={{
                    background: 'rgba(239, 68, 68, 0.15)',
                    border: '1px solid rgba(239, 68, 68, 0.4)',
                    borderRadius: '8px',
                    padding: '12px 16px',
                    color: '#fca5a5',
                    fontSize: '14px',
                  }}
                >
                  {error}
                </motion.div>
              )}

              <motion.button
                type="submit"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                style={{
                  width: '100%',
                  background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
                  border: 'none',
                  borderRadius: '8px',
                  padding: '14px',
                  color: '#fff',
                  fontSize: '16px',
                  fontWeight: '600',
                  cursor: 'pointer',
                  marginTop: '8px',
                  boxShadow: '0 4px 12px rgba(59, 130, 246, 0.4)',
                }}
              >
                Sign In
              </motion.button>
            </form>

            <div style={{
              marginTop: '24px',
              textAlign: 'center',
              fontSize: '14px',
              color: '#94a3b8',
            }}>
              Don't have an account?{' '}
              <a
                href="/signup"
                style={{
                  color: '#3b82f6',
                  textDecoration: 'none',
                  fontWeight: '500',
                }}
              >
                Sign up
              </a>
            </div>
          </motion.div>
        </div>
      </main>
    </div>
  )
}
