import styles from '../styles/page.module.css';
import AppProviders, { PageMotion } from './providers/AppProviders';
import { motion } from 'framer-motion';
import Link from 'next/link';

const proteins = [
  {
    name: 'SIRT1',
    description: 'A key longevity regulator involved in DNA repair, metabolism, and stress resistance',
    icon: '🧬',
    color: 'rgba(59, 130, 246, 0.2)',
    borderColor: 'rgba(59, 130, 246, 0.4)',
  },
  {
    name: 'mTOR',
    description: 'Master regulator of cell growth, metabolism, and autophagy; inhibition extends lifespan',
    icon: '⚡',
    color: 'rgba(139, 92, 246, 0.2)',
    borderColor: 'rgba(139, 92, 246, 0.4)',
  },
  {
    name: 'FOXO3',
    description: 'Transcription factor controlling stress resistance, DNA repair, and cellular homeostasis',
    icon: '🛡️',
    color: 'rgba(236, 72, 153, 0.2)',
    borderColor: 'rgba(236, 72, 153, 0.4)',
  },
  {
    name: 'AMPK',
    description: 'Energy sensor that activates autophagy and enhances metabolic health',
    icon: '🔋',
    color: 'rgba(34, 197, 94, 0.2)',
    borderColor: 'rgba(34, 197, 94, 0.4)',
  },
  {
    name: 'IGF1',
    description: 'Growth factor involved in aging; reduced signaling associated with longevity',
    icon: '📈',
    color: 'rgba(249, 115, 22, 0.2)',
    borderColor: 'rgba(249, 115, 22, 0.4)',
  },
];

export default function Proteins() {
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
              Longevity Proteins
            </h1>

            <p style={{
              fontSize: '18px',
              lineHeight: '1.6',
              color: '#cbd5e1',
              textAlign: 'center',
              marginBottom: '48px',
              maxWidth: '700px',
              margin: '0 auto 48px auto',
            }}>
              Explore key proteins that regulate aging, metabolism, and cellular health. 
              Our AI has access to comprehensive data on these critical longevity pathways.
            </p>

            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
              gap: '24px',
              marginTop: '40px',
            }}>
              {proteins.map((protein, index) => (
                <Link 
                  href={`/proteins/${protein.name}`} 
                  key={protein.name}
                  style={{ textDecoration: 'none' }}
                >
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, delay: index * 0.1 }}
                    whileHover={{ scale: 1.03, y: -5 }}
                    whileTap={{ scale: 0.98 }}
                    style={{
                      background: protein.color,
                      backdropFilter: 'blur(12px)',
                      border: `1px solid ${protein.borderColor}`,
                      borderRadius: '16px',
                      padding: '20px 24px',
                      cursor: 'pointer',
                      transition: 'all 0.3s ease',
                      height: '100%',
                      display: 'flex',
                      flexDirection: 'column',
                    }}
                  >

                    <h3 style={{
                      fontSize: '24px',
                      fontWeight: '700',
                      color: '#fff',
                      marginBottom: '12px',
                      margin: '0 0 12px 0',
                    }}>
                      {protein.name}
                    </h3>

                    <p style={{
                      fontSize: '16px',
                      lineHeight: '1.6',
                      color: '#cbd5e1',
                      margin: '0',
                      flex: 1,
                    }}>
                      {protein.description}
                    </p>

                    <div style={{
                      marginTop: '20px',
                      fontSize: '14px',
                      color: '#a78bfa',
                      fontWeight: '600',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px',
                    }}>
                      Learn more
                      <span style={{ fontSize: '18px' }}>→</span>
                    </div>
                  </motion.div>
                </Link>
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
                Want to learn more?
              </h2>
              <p style={{
                fontSize: '16px',
                lineHeight: '1.7',
                color: '#cbd5e1',
                marginBottom: '24px',
              }}>
                Chat with our AI to explore these proteins in depth, including their roles in aging, 
                therapeutic targets, and the latest research findings.
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