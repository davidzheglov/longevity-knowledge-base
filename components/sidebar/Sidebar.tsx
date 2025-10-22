'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter, usePathname } from 'next/navigation';
import styles from './sidebar.module.css';

type User = { id: number; email: string } | null;

export default function Sidebar() {
  const [isOpen, setIsOpen] = useState(false);
  const [user, setUser] = useState<User>(null);
  const router = useRouter();
  const pathname = usePathname();

  const toggleSidebar = () => setIsOpen((v) => !v);
  const closeSidebar = () => setIsOpen(false);

  useEffect(() => {
    closeSidebar();
  }, [pathname]);

  useEffect(() => {
      // use axios to call /api/auth/me
      import('axios').then(({ default: axios }) => {
        axios.get('/api/auth/me', { headers: { 'Cache-Control': 'no-store' } })
          .then(r => setUser(r.data.user))
          .catch(() => setUser(null));
      });
    }, []);

  async function handleLogout() {
    const { default: axios } = await import('axios');
    await axios.post('/api/auth/logout');
    setUser(null);
    router.push('/');
  }

  return (
    <>
      <button
        className={styles.menuButton}
        onClick={toggleSidebar}
        aria-label="Open menu"
        aria-expanded={isOpen}
        aria-controls="sidebar"
      >
        <div className={styles.hamburger}>
          <span></span><span></span><span></span>
        </div>
      </button>

      <nav
        id="sidebar"
        className={`${styles.sidebar} ${isOpen ? styles.open : ''}`}
        aria-hidden={!isOpen}
      >
        <button className={styles.closeButton} onClick={toggleSidebar} aria-label="Close menu">
          ×
        </button>

        <div className={styles.nav}>
          <p className={styles.menu}>Menu</p>

          <Link className={styles.section} href="/" onClick={closeSidebar}>About</Link>
          <Link className={styles.section} href="/chat" onClick={closeSidebar}>Chat</Link>
          <Link className={styles.section} href="/manifesto" onClick={closeSidebar}>Manifesto</Link>

          <div className={styles.authBlock}>
            {user ? (
              <>
                <span className={styles.userEmail}>{user.email}</span>
                <button className={styles.logoutBtn} onClick={handleLogout}>Logout</button>
              </>
            ) : (
              <div className={styles.authButtons}>
                <Link className={styles.section} href="/login" onClick={closeSidebar}>Login</Link>
                <span className={styles.sep}>·</span>
                <Link className={styles.section} href="/signup" onClick={closeSidebar}>Sign up</Link>
              </div>
            )}
          </div>
        </div>
      </nav>

      {isOpen && <div className={styles.overlay} onClick={toggleSidebar} aria-hidden />}
    </>
  );
}
