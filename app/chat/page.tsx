import styles from './chat.module.css'
import Sidebar from '../components/sidebar/Sidebar';

export default function Chat() {
  return (
    <div className={styles.pageContainer}>
      <div className={styles.topStrip}>
        <Sidebar />
      </div>
        <div className={styles.mainContainer}>
            <h1 className={styles.placeHolder}>Something Epic Is Coming</h1>
        </div>
    </div>
  );
}