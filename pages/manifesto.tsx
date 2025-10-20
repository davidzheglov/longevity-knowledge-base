import Sidebar from '@/components/sidebar/Sidebar';
import styles from '@/styles/page.module.css';

export default function Manifesto(){
  return (
    <div className={styles.pageContainer}>
      <div className={styles.topStrip}><Sidebar/></div>
      <main className={styles.mainContainer}>
        <h2 style={{color:'#fff'}}>Manifesto</h2>
        <p style={{color:'#cfcbe6'}}>Our principles ...</p>
      </main>
    </div>
  )
}
