/**
 * Login page. Renders the credentials form, performs authentication, and
 * redirects to the board on success (or away if already signed in).
 */
import { useState, type JSX } from "react";
import { Navigate, useNavigate } from "react-router-dom";

import { ApiError } from "../api/client";
import Login from "../components/Login";
import { useAuth } from "../hooks/authContext";
import styles from "../styles/LoginPage.module.css";

export default function LoginPage(): JSX.Element {
  const { user, loading, login } = useAuth();
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState<boolean>(false);

  if (!loading && user) {
    return <Navigate to="/" replace />;
  }

  const handleSubmit = async (email: string, password: string): Promise<void> => {
    setSubmitting(true);
    setError(null);
    try {
      await login({ email, password });
      navigate("/", { replace: true });
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        setError("Invalid email or password.");
      } else if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Sign in failed. Please try again.");
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main className={styles.page}>
      <div className={styles.panel}>
        <div className={styles.intro}>
          <span className={styles.logo} aria-hidden="true">
            ▣
          </span>
          <h1 className={styles.product}>TaskTracker</h1>
          <p className={styles.tagline}>Lightweight task boards for small teams.</p>
        </div>
        <Login
          onSubmit={(email, password) => void handleSubmit(email, password)}
          error={error}
          submitting={submitting}
        />
      </div>
    </main>
  );
}
