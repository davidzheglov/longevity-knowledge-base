import { useRouter } from 'next/router';
import styles from '@/styles/page.module.css';
import AppProviders from '../providers/AppProviders';
import { motion } from 'framer-motion';
import Link from 'next/link';

export default function ProteinPage() {
  const router = useRouter();
  const proteinName = 'mTOR';

  const examples = [
    {
      prompt: "What is the role of this protein in aging?",
      reply: "This is a placeholder response. Our AI will provide detailed information about the protein's role in aging mechanisms, including cellular senescence, DNA repair, and metabolic regulation."
    },
    {
      prompt: "What are the therapeutic targets related to this protein?",
      reply: "This is a placeholder response. Our AI will explain current and potential therapeutic approaches targeting this protein, including small molecules, peptides, and lifestyle interventions."
    },
    {
      prompt: "How does this protein interact with other longevity pathways?",
      reply: "This is a placeholder response. Our AI will detail the protein's interactions with other key longevity regulators and signaling networks in aging biology."
    }
  ];

  return (
    <AppProviders>
      <div className={styles.pageContainer}>
        <main className={styles.mainContainer} style={{ paddingTop: '50px' }}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            style={{
              maxWidth: '900px',
              margin: '0 auto',
              padding: '36px 20px',
            }}
          >
            <h1 style={{
              fontSize: '44px',
              fontWeight: '700',
              marginBottom: '8px',
              color: '#fff',
              textAlign: 'center',
            }}>
              {proteinName}
            </h1>

            <p style={{
              fontSize: '18px',
              lineHeight: '1.8',
              color: '#cbd5e1',
              textAlign: 'center',
              marginBottom: '48px',
            }}>
              Explore research and insights about this longevity protein
            </p>

            <div style={{
              display: 'flex',
              flexDirection: 'column',
              gap: '24px',
            }}>
              {examples.map((example, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                  style={{
                    background: 'rgba(15, 23, 42, 0.6)',
                    backdropFilter: 'blur(12px)',
                    border: '1px solid rgba(100, 116, 139, 0.3)',
                    borderRadius: '16px',
                    padding: '20px 30px',
                  }}
                >
                  <div style={{ marginBottom: '20px' }}>
                    <div style={{
                      fontSize: '14px',
                      fontWeight: '600',
                      color: '#a78bfa',
                      marginBottom: '12px',
                      textTransform: 'uppercase',
                      letterSpacing: '0.05em',
                    }}>
                      Prompt
                    </div>
                    <p style={{
                      fontSize: '16px',
                      lineHeight: '1.8',
                      color: '#cbd5e1',
                      margin: 0,
                    }}>
                      {example.prompt}
                    </p>
                  </div>

                  <div>
                    <div style={{
                      fontSize: '14px',
                      fontWeight: '600',
                      color: '#60a5fa',
                      marginBottom: '12px',
                      textTransform: 'uppercase',
                      letterSpacing: '0.05em',
                    }}>
                      Reply
                    </div>
                    <p style={{
                      fontSize: '16px',
                      lineHeight: '1.8',
                      color: '#cbd5e1',
                      margin: 0,
                    }}>
                      {example.reply}
                    </p>
                  </div>
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
                fontSize: '20px',
                fontWeight: '600',
                color: '#fff',
                marginBottom: '16px',
              }}>
                Want to dive deeper?
              </h2>
              <p style={{
                fontSize: '14px',
                lineHeight: '1.7',
                color: '#cbd5e1',
                marginBottom: '24px',
              }}>
                Chat with our AI to get personalized insights about {proteinName} and its role in longevity science.
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
                    fontSize: '14px',
                    fontWeight: '600',
                    cursor: 'pointer',
                    boxShadow: '0 4px 16px rgba(109, 40, 217, 0.4)',
                  }}
                >
                  Start Chatting →
                </motion.button>
              </Link>
            </div>

            <div style={{
              marginTop: '32px',
              textAlign: 'center',
            }}>
              <Link 
                href="/proteins"
                style={{
                  color: '#a78bfa',
                  textDecoration: 'none',
                  fontSize: '16px',
                  fontWeight: '500',
                }}
              >
                ← Back to all proteins
              </Link>
            </div>
          </motion.div>
        </main>
      </div>
    </AppProviders>
  );
}