/**
 * Top application bar: product name, signed-in user, and a logout button.
 */
import type { JSX } from "react";

import type { User } from "../types";
import styles from "../styles/Header.module.css";

interface HeaderProps {
  user: User;
  onLogout: () => void;
}

export default function Header({ user, onLogout }: HeaderProps): JSX.Element {
  return (
    <header className={styles.header}>
      <div className={styles.brand}>
        <span className={styles.logo} aria-hidden="true">
          ▣
        </span>
        <h1 className={styles.title}>TaskTracker</h1>
      </div>
      <div className={styles.user}>
        <span className={styles.userName}>{user.full_name}</span>
        <button type="button" className={styles.logout} onClick={onLogout}>
          Log out
        </button>
      </div>
    </header>
  );
}
