
import styles from '@/styles/page.module.css';
import { motion } from 'framer-motion';
import Link from 'next/link';

export default function Manifesto(){
  return (
    <div className={styles.pageContainer}>
      <main className={styles.mainContainer}>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          style={{
            maxWidth: '900px',
            margin: '0 auto',
            padding: '40px 20px',
          }}
        >
          <h1 style={{
            fontSize: '48px',
            fontWeight: '700',
            marginBottom: '8px',
            color: '#fff',
            textAlign: 'center',
          }}>
            Our Manifesto
          </h1>

          <p style={{
            fontSize: '18px',
            lineHeight: '1.8',
            color: '#cbd5e1',
            textAlign: 'center',
            marginBottom: '48px',
          }}>
            What is aging and how we can fight it
          </p>

          <div style={{
            background: 'rgba(15, 23, 42, 0.6)',
            backdropFilter: 'blur(12px)',
            border: '1px solid rgba(100, 116, 139, 0.3)',
            borderRadius: '16px',
            padding: '30px 40px',
            marginBottom: '24px',
          }}>
            <h2 style={{
              fontSize: '28px',
              fontWeight: '600',
              marginBottom: '20px',
              color: '#fff',
            }}>
              Why We Must Fight Aging
            </h2>
            <p style={{
              fontSize: '16px',
              lineHeight: '1.8',
              color: '#cbd5e1',
              marginBottom: '20px',
            }}>
              Aging is not just a natural process—it is the root cause of most human suffering. Cancer, Alzheimer's, 
              heart disease, and countless other conditions share a common origin: the progressive breakdown of our 
              biological systems over time.
            </p>
            <p style={{
              fontSize: '16px',
              lineHeight: '1.8',
              color: '#cbd5e1',
            }}>
              Today, for the first time in history, we possess the knowledge, tools, and data to fight back. 
              The question is no longer whether we can defeat aging—but when we choose to act.
            </p>
          </div>

          <div style={{
            background: 'rgba(15, 23, 42, 0.6)',
            backdropFilter: 'blur(12px)',
            border: '1px solid rgba(100, 116, 139, 0.3)',
            borderRadius: '16px',
            padding: '30px 40px',
            marginBottom: '24px',
          }}>
            <h2 style={{
              fontSize: '28px',
              fontWeight: '600',
              marginBottom: '20px',
              color: '#fff',
            }}>
              Our Core Beliefs
            </h2>
            <div style={{
              display: 'flex',
              flexDirection: 'column',
              gap: '24px',
            }}>
              <div>
                <h3 style={{
                  fontSize: '20px',
                  fontWeight: '600',
                  color: '#a78bfa',
                  marginBottom: '12px',
                }}>
                  🧬 Aging is Treatable
                </h3>
                <p style={{
                  fontSize: '16px',
                  lineHeight: '1.8',
                  color: '#cbd5e1',
                }}>
                  Aging is not an immutable law of nature but a biological process driven by identifiable 
                  mechanisms—genomic instability, cellular senescence, mitochondrial dysfunction, and chronic 
                  inflammation. These can be understood, measured, and ultimately reversed.
                </p>
              </div>

              <div>
                <h3 style={{
                  fontSize: '20px',
                  fontWeight: '600',
                  color: '#a78bfa',
                  marginBottom: '12px',
                }}>
                  🔬 Science Must Be Data-Driven
                </h3>
                <p style={{
                  fontSize: '16px',
                  lineHeight: '1.8',
                  color: '#cbd5e1',
                }}>
                  We harness AI, multi-omics data, aging clocks, and biological databases to identify targets, 
                  develop therapies, and measure outcomes with unprecedented precision. Our approach integrates 
                  deterministic models with real-world evidence.
                </p>
              </div>

              <div>
                <h3 style={{
                  fontSize: '20px',
                  fontWeight: '600',
                  color: '#a78bfa',
                  marginBottom: '12px',
                }}>
                  💊 A Multimodal Approach
                </h3>
                <p style={{
                  fontSize: '16px',
                  lineHeight: '1.8',
                  color: '#cbd5e1',
                }}>
                  No single "magic pill" will cure aging. Victory requires a combination of strategies: eliminating 
                  senescent cells, restoring proteostasis, enhancing autophagy, targeting inflammation, and eventually 
                  replacing damaged tissues and organs.
                </p>
              </div>

              <div>
                <h3 style={{
                  fontSize: '20px',
                  fontWeight: '600',
                  color: '#a78bfa',
                  marginBottom: '12px',
                }}>
                  🌍 Focus on Chronic Disease First
                </h3>
                <p style={{
                  fontSize: '16px',
                  lineHeight: '1.8',
                  color: '#cbd5e1',
                }}>
                  We begin with conditions driven by chronic inflammation and fibrosis: atherosclerosis, type 2 
                  diabetes, Alzheimer's, autoimmune disorders. By restoring the body to a healthy, youthful state, 
                  we pave the way to defeat aging itself.
                </p>
              </div>
            </div>
          </div>

          <div style={{
            background: 'rgba(15, 23, 42, 0.6)',
            backdropFilter: 'blur(12px)',
            border: '1px solid rgba(100, 116, 139, 0.3)',
            borderRadius: '16px',
            padding: '30px 40px',
            marginBottom: '24px',
          }}>
            <h2 style={{
              fontSize: '28px',
              fontWeight: '600',
              marginBottom: '20px',
              color: '#fff',
            }}>
              The Path Forward
            </h2>
            <p style={{
              fontSize: '16px',
              lineHeight: '1.8',
              color: '#cbd5e1',
              marginBottom: '16px',
            }}>
              Our roadmap includes small molecules (metformin, NAD+ precursors, NLRP3 inhibitors), senolytics to 
              eliminate zombie cells, epigenetic reprogramming, cell therapies, and AI-driven precision medicine. 
              We stand on the shoulders of decades of research—from the Hallmarks of Aging to aging clocks to 
              CRISPR-based gene editing.
            </p>
            <p style={{
              fontSize: '16px',
              lineHeight: '1.8',
              color: '#cbd5e1',
            }}>
              Evolution has equipped some species with extraordinary longevity mechanisms. We don't need to reinvent 
              biology—we need to learn from it, combine it with radical technologies, and extend human healthspan 
              beyond evolutionary limits.
            </p>
          </div>

          <div style={{
            textAlign: 'center',
            marginTop: '48px',
          }}>
            <a 
              href="/manifesto.pdf" 
              target="_blank" 
              rel="noopener noreferrer"
              style={{ textDecoration: 'none' }}
            >
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                style={{
                  background: 'linear-gradient(135deg, #6d28d9 0%, #8b5cf6 100%)',
                  border: 'none',
                  borderRadius: '12px',
                  padding: '16px 32px',
                  color: '#fff',
                  fontSize: '18px',
                  fontWeight: '600',
                  cursor: 'pointer',
                  boxShadow: '0 4px 16px rgba(109, 40, 217, 0.4)',
                  marginBottom: '16px',
                }}
              >
                📄 Read Full Manifesto (PDF)
              </motion.button>
            </a>
            <p style={{
              fontSize: '14px',
              color: '#94a3b8',
              fontStyle: 'italic',
            }}>
              A comprehensive 20-page exploration of aging biology and our vision for the future
            </p>
          </div>

          <div style={{
            marginTop: '48px',
            padding: '24px',
            background: 'rgba(109, 40, 217, 0.1)',
            border: '1px solid rgba(109, 40, 217, 0.3)',
            borderRadius: '12px',
            textAlign: 'center',
          }}>
            <p style={{
              fontSize: '16px',
              lineHeight: '1.8',
              color: '#cbd5e1',
              margin: '0',
            }}>
              <em>"We must fight aging at all costs—and we can win."</em>
            </p>
            <p style={{
              fontSize: '14px',
              color: '#94a3b8',
              marginTop: '8px',
              marginBottom: '0',
            }}>
              — Elephant Labs Team
            </p>
          </div>
        </motion.div>
      </main>
    </div>
  )
}
