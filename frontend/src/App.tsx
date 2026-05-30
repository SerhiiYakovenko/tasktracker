/**
 * Root component. Wires routing and guards the board behind authentication.
 */
import { Navigate, Route, Routes } from "react-router-dom";
import type { JSX } from "react";

import { useAuth } from "./hooks/authContext";
import { AuthProvider } from "./hooks/useAuth";
import BoardPage from "./pages/BoardPage";
import LoginPage from "./pages/LoginPage";

/** Renders children only when authenticated; otherwise redirects to login. */
function RequireAuth({ children }: { children: JSX.Element }): JSX.Element {
  const { user, loading } = useAuth();

  if (loading) {
    return <div className="app-loading">Loading…</div>;
  }
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

/** Defines the route table. Separated so it can sit inside the AuthProvider. */
function AppRoutes(): JSX.Element {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/"
        element={
          <RequireAuth>
            <BoardPage />
          </RequireAuth>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default function App(): JSX.Element {
  return (
    <AuthProvider>
      <AppRoutes />
    </AuthProvider>
  );
}
