import styles from '../styles/page.module.css'
import Hero from '@/components/hero/Hero'
import AppProviders, { PageMotion } from './providers/AppProviders'
import DNAField from '@/components/hero/DNAField'

export default function Home() {
  return (
    <AppProviders>
      <div className={styles.pageContainer}>
        <main className={styles.mainContainer}>
          <PageMotion>
            <Hero />
          </PageMotion>
          {/* fixed-right DNA background */}
          <DNAField anchor="right" />
        </main>
      </div>
    </AppProviders>
  );
}
