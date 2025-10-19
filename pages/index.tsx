import styles from '../styles/page.module.css'
import Sidebar from '@/components/sidebar/Sidebar'
import Link from 'next/link'


export default function Home() {
  return (
    <div className={styles.pageContainer}>
    <div className={styles.topStrip}>
      <Sidebar />
    </div>
    <main className={styles.mainContainer}>
      <div className={styles.card}>
        <h1 className={styles.title}>Longevity LLM</h1>
      </div>
      <p className={styles.subtitle}>By Elephant Labs</p>
      <Link href="/chat">
        <button className={styles.button}>Get Started</button>
      </Link>
    </main>
    </div>
  );
}
