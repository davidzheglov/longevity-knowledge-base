import styles from '../styles/page.module.css'
import Sidebar from '@/components/sidebar/Sidebar'
import Hero from '@/components/hero/Hero'
import AppProviders, { PageMotion } from './providers/AppProviders'
import DNAField from '@/components/hero/DNAField'

export default function Home() {
  return (
    <AppProviders>
      <div className={styles.pageContainer}>
        <div className={styles.topStrip}>
          <Sidebar />
        </div>
        <main className={styles.mainContainer}>
          <PageMotion>
            <Hero />
            <p className={styles.subtitle}>By Elephant Labs</p>
          </PageMotion>
          {/* fixed-right DNA background */}
          <DNAField anchor="right" />
        </main>
      </div>
    </AppProviders>
  );
}
