/**
 * Controlled login form. Owns the email/password fields and surfaces an
 * optional error message; submission is delegated to the parent.
 */
import { useState, type FormEvent, type JSX } from "react";

import styles from "../styles/Login.module.css";

interface LoginProps {
  onSubmit: (email: string, password: string) => void;
  error: string | null;
  submitting: boolean;
}

export default function Login({ onSubmit, error, submitting }: LoginProps): JSX.Element {
  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");

  const handleSubmit = (event: FormEvent<HTMLFormElement>): void => {
    event.preventDefault();
    onSubmit(email.trim(), password);
  };

  return (
    <form className={styles.form} onSubmit={handleSubmit} aria-label="Sign in">
      <h2 className={styles.heading}>Sign in</h2>

      <label className={styles.field}>
        <span className={styles.label}>Email</span>
        <input
          type="email"
          name="email"
          autoComplete="email"
          required
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          className={styles.input}
        />
      </label>

      <label className={styles.field}>
        <span className={styles.label}>Password</span>
        <input
          type="password"
          name="password"
          autoComplete="current-password"
          required
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          className={styles.input}
        />
      </label>

      {error !== null && (
        <p className={styles.error} role="alert">
          {error}
        </p>
      )}

      <button type="submit" className={styles.submit} disabled={submitting}>
        {submitting ? "Signing in…" : "Sign in"}
      </button>
    </form>
  );
}
