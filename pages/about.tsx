import { motion } from 'framer-motion';
import styles from '../styles/page.module.css'
import AppProviders from './providers/AppProviders'
import Link from 'next/link';

export default function AboutPage() {
  return (
    <AppProviders>
      <div className={styles.pageContainer}>
        <main className={styles.mainContainer}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            style={{
              maxWidth: '800px',
              margin: '0 auto',
              padding: '40px 20px',
            }}
          >
            <h1 style={{
              fontSize: '48px',
              fontWeight: '700',
              marginBottom: '24px',
              color: '#fff',
              textAlign: 'center',
            }}>
              About Longevity LLM
            </h1>

            <div style={{
              background: 'rgba(15, 23, 42, 0.6)',
              backdropFilter: 'blur(12px)',
              border: '1px solid rgba(100, 116, 139, 0.3)',
              borderRadius: '16px',
              padding: '40px',
              marginBottom: '24px',
            }}>
              <h2 style={{
                fontSize: '24px',
                fontWeight: '600',
                marginBottom: '16px',
                color: '#fff',
              }}>
                🏆 A Hackathon Project
              </h2>
              <p style={{
                fontSize: '16px',
                lineHeight: '1.7',
                color: '#cbd5e1',
                marginBottom: '0',
              }}>
                Longevity LLM was created as a hackathon project for <strong>hackaging.ai</strong>, 
                bringing together cutting-edge AI technology with longevity science to create an 
                intelligent assistant for aging research.
              </p>
            </div>

            <div style={{
              background: 'rgba(15, 23, 42, 0.6)',
              backdropFilter: 'blur(12px)',
              border: '1px solid rgba(100, 116, 139, 0.3)',
              borderRadius: '16px',
              padding: '40px',
              marginBottom: '24px',
            }}>
              <h2 style={{
                fontSize: '24px',
                fontWeight: '600',
                marginBottom: '16px',
                color: '#fff',
              }}>
                👥 The Team
              </h2>
              <p style={{
                fontSize: '16px',
                lineHeight: '1.7',
                color: '#cbd5e1',
                marginBottom: '16px',
              }}>
                We are a diverse team of 5 passionate individuals dedicated to advancing longevity science:
              </p>
              <ul style={{
                fontSize: '16px',
                lineHeight: '1.9',
                color: '#cbd5e1',
                paddingLeft: '24px',
                listStyle: 'none',
              }}>
                <li><strong style={{ color: '#a78bfa' }}>
                    <a href="https://www.linkedin.com/in/maxim-kovalev-8bb952379/" >
                        Maxim Kovalev
                    </a>
                </strong> - biologist, data scientist; Skolkovo</li>
                <li><strong style={{ color: '#a78bfa' }}>
                    <a href='https://www.linkedin.com/in/ekaterina-leksina/'>
                    Ekaterina Leksina</a></strong> - frontend developer, UI/UX designer; Warwick University</li>
                <li><strong style={{ color: '#a78bfa' }}>
                    <a href='https://www.linkedin.com/in/dmitrii-galatenko-740799211/'>Dmitrii Galatenko</a></strong> - ML engineer, backend developer; Cambridge University</li>
                <li><strong style={{ color: '#a78bfa' }}>
                    <a href='https://www.linkedin.com/in/david-zheglov/'>David Zheglov</a></strong> - frontend and infrastructure developer; HKUST</li>
                <li><strong style={{ color: '#a78bfa' }}>
                    <a href='https://www.linkedin.com/in/timofey-fedoseev-826609231/'>Timofey Fedoseev</a></strong> - ML engineer, backend developer; ETH</li>
              </ul>
            </div>

            <div style={{
              background: 'rgba(15, 23, 42, 0.6)',
              backdropFilter: 'blur(12px)',
              border: '1px solid rgba(100, 116, 139, 0.3)',
              borderRadius: '16px',
              padding: '40px',
              marginBottom: '24px',
            }}>
              <h2 style={{
                fontSize: '24px',
                fontWeight: '600',
                marginBottom: '16px',
                color: '#fff',
              }}>
                🔬 Advanced Biological Resources
              </h2>
              <p style={{
                fontSize: '16px',
                lineHeight: '1.7',
                color: '#cbd5e1',
                marginBottom: '20px',
              }}>
                Our chat agent has access to specialized biological resources, including:
              </p>
              <ul style={{
                fontSize: '16px',
                lineHeight: '1.9',
                color: '#cbd5e1',
                paddingLeft: '24px',
              }}>
                <li><strong>Scientific databases</strong> - Comprehensive aging and longevity data</li>
                <li><strong>Aging clocks</strong> - Predictive models for biological age</li>
                <li><strong>Deterministic models</strong> - Mathematical frameworks for biophysical processes</li>
                <li><strong>Research papers</strong> - Latest findings in longevity science</li>
              </ul>
            </div>

            <div style={{
              background: 'rgba(15, 23, 42, 0.6)',
              backdropFilter: 'blur(12px)',
              border: '1px solid rgba(100, 116, 139, 0.3)',
              borderRadius: '16px',
              padding: '40px',
            }}>
              <h2 style={{
                fontSize: '24px',
                fontWeight: '600',
                marginBottom: '16px',
                color: '#fff',
              }}>
                🎯 Our Vision
              </h2>
              <p style={{
                fontSize: '16px',
                lineHeight: '1.7',
                color: '#cbd5e1',
                marginBottom: '20px',
              }}>
                Longevity is a tricky topic that requires careful consideration of scientific, 
                ethical, and practical dimensions. Our comprehensive vision for the field and 
                our approach to these challenges can be found in our{' '}
                <Link 
                  href="/manifesto" 
                  style={{
                    color: '#a78bfa',
                    textDecoration: 'none',
                    fontWeight: '600',
                    borderBottom: '2px solid rgba(167, 139, 250, 0.3)',
                  }}
                >
                  Manifesto
                </Link>.
              </p>
            </div>

            <div style={{
              textAlign: 'center',
              marginTop: '48px',
            }}>
              <Link href="/chat">
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
                  }}
                >
                  Start Exploring →
                </motion.button>
              </Link>
            </div>
          </motion.div>
        </main>
      </div>
    </AppProviders>
  );
}