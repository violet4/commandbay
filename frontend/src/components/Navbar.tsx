import Link from 'next/link';
import styles from '@/styles/navbar.module.css'

export default function Navbar() {
    return (
        <nav className={styles.navbar}>
            <ul>
                <li><Link href="/">Home</Link></li>
                <li><Link href="/users">Users</Link></li>
                <li><Link href="/about">About</Link></li>
                <li><a href="/api/v1/docs">API Docs</a></li>
            </ul>
        </nav>
    );
}
