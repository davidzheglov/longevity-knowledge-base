'use client';

import { useState } from 'react';
import styles from './sidebar.module.css';

export default function Sidebar() {
  const [isOpen, setIsOpen] = useState(false);

  const toggleSidebar = () => {
    setIsOpen(!isOpen);
  };

  return (
    <>
      <button className={styles.menuButton} onClick={toggleSidebar}>
        <div className={styles.hamburger}>
          <span></span>
          <span></span>
          <span></span>
        </div>
      </button>

      <div className={`${styles.sidebar} ${isOpen ? styles.open : ''}`}>
        <button className={styles.closeButton} onClick={toggleSidebar}>
          ×
        </button>
        <div className={styles.nav}>
          <p className={styles.menu}>Menu</p>
          <p className={styles.section}>About</p>
          <p className={styles.section}>Chat</p>
          <p className={styles.section}>Manifesto</p>
        </div>
      </div>

      {isOpen && <div className={styles.overlay} onClick={toggleSidebar}></div>}
    </>
  );
}