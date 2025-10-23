import styles from '../styles/page.module.css';
import AppProviders from './providers/AppProviders';
import { motion } from 'framer-motion';
import Link from 'next/link';

const clocks = [
  {
    name: 'Horvath',
    description: 'First multi-tissue DNA methylation clock (2013) using 353 CpG sites; accurately predicts chronological age across multiple tissues',
    color: 'rgba(15, 23, 42, 0.8)',
  },
  {
    name: 'Hannum',
    description: 'Blood-based clock using 71 CpG sites; highly accurate for chronological age prediction in whole blood samples',
    color: 'rgba(15, 23, 42, 0.8)',
  },
  {
    name: 'PhenoAge',
    description: 'Second-generation clock predicting time until mortality and disease risk rather than just chronological age; strongest predictor of health outcomes',
    color: 'rgba(15, 23, 42, 0.8)',
  },
  {
    name: 'GrimAge',
    description: 'Predicts lifespan and healthspan by incorporating plasma proteins and smoking history based on blood methylation; highly correlated with age-related diseases',
    color: 'rgba(15, 23, 42, 0.8)',
  },
  {
    name: 'Wyss-Coray',
    description: 'Plasma proteome clock capturing systemic aging signals from 11 major organ systems using protein biomarkers',
    color: 'rgba(15, 23, 42, 0.8)',
  },
  {
    name: 'Brunet',
    description: 'Cell type-specific clocks for brain aging, with separate models for neural stem and progenitor cells, astrocytes, oligodendrocytes, and microglia',
    color: 'rgba(15, 23, 42, 0.8)',
  },
  {
    name: 'DamAge',
    description: 'Measures detrimental age-related changes; distinguishes harmful aging alterations from adaptive responses',
    color: 'rgba(15, 23, 42, 0.8)',
  },
  {
    name: 'AdaptAge',
    description: 'Captures protective and compensatory changes during aging; complements DamAge to separate beneficial from harmful alterations',
    color: 'rgba(15, 23, 42, 0.8)',
  }
];

export default function AgingClocks() {
  return (
    <AppProviders>
      <div className={styles.pageContainer}>
        <main className={styles.mainContainer} style={{ paddingTop: '50px' }}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            style={{
              maxWidth: '1200px',
              margin: '0 auto',
              padding: '40px 20px',
            }}
          >
            <h1 style={{
              fontSize: '44px',
              fontWeight: '700',
              marginBottom: '16px',
              color: '#fff',
              textAlign: 'center',
            }}>
              Aging Clocks
            </h1>

            <p style={{
              fontSize: '18px',
              lineHeight: '1.6',
              color: '#cbd5e1',
              textAlign: 'center',
              marginBottom: '48px',
              maxWidth: '800px',
              margin: '0 auto 48px auto',
            }}>
              Explore the well-resarched biological clocks that measure aging at the molecular level. 
              These clocks quantify biological age using DNA methylation, proteins, and other biomarkers.
            </p>

            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
              gap: '24px',
              marginTop: '40px',
            }}>
              {clocks.map((clock, index) => (
                <motion.div
                  key={clock.name}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: index * 0.08 }}
                  style={{
                    background: clock.color,
                    backdropFilter: 'blur(12px)',
                    border: '1px solid rgba(100, 116, 139, 0.4)',
                    borderRadius: '16px',
                    padding: '28px',
                    height: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                  }}
                >
                  <h3 style={{
                    fontSize: '24px',
                    fontWeight: '700',
                    color: '#fff',
                    marginBottom: '16px',
                    margin: '0 0 16px 0',
                  }}>
                    {clock.name}
                  </h3>

                  <p style={{
                    fontSize: '16px',
                    lineHeight: '1.7',
                    color: '#cbd5e1',
                    margin: '0',
                    flex: 1,
                  }}>
                    {clock.description}
                  </p>
                </motion.div>
              ))}
            </div>

            <div style={{
              marginTop: '64px',
              padding: '32px',
              background: 'rgba(15, 23, 42, 0.6)',
              backdropFilter: 'blur(12px)',
              border: '1px solid rgba(100, 116, 139, 0.3)',
              borderRadius: '16px',
              textAlign: 'center',
            }}>
              <h2 style={{
                fontSize: '24px',
                fontWeight: '600',
                color: '#fff',
                marginBottom: '16px',
              }}>
                Want to learn more about aging clocks?
              </h2>
              <p style={{
                fontSize: '16px',
                lineHeight: '1.7',
                color: '#cbd5e1',
                marginBottom: '24px',
              }}>
                Chat with our AI to understand how these clocks work, their applications in longevity research, 
                and use them directly via the chat.
              </p>
              <Link href="/chat">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  style={{
                    background: 'linear-gradient(135deg, #6d28d9 0%, #8b5cf6 100%)',
                    border: 'none',
                    borderRadius: '12px',
                    padding: '14px 28px',
                    color: '#fff',
                    fontSize: '16px',
                    fontWeight: '600',
                    cursor: 'pointer',
                    boxShadow: '0 4px 16px rgba(109, 40, 217, 0.4)',
                  }}
                >
                  Start Chatting →
                </motion.button>
              </Link>
            </div>
          </motion.div>
        </main>
      </div>
    </AppProviders>
  );
}