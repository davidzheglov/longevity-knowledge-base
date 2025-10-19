import Sidebar from '@/components/sidebar/Sidebar';
import styles from '@/styles/page.module.css';

export default function ChatPage(){
  return (
    <div className={styles.pageContainer}>
      <div className={styles.topStrip}><Sidebar/></div>
      <main className={styles.mainContainer}>
        <h2 style={{color:'#fff'}}>Chat</h2>
        <p style={{color:'#cfcbe6'}}>Chat UI will go here.</p>
      </main>
    </div>
  )
}
