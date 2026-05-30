/**
 * Authentication context definition and consumer hook.
 *
 * Kept separate from the provider component so the provider module exports
 * only a component (React Fast Refresh friendly).
 */
import { createContext, useContext } from "react";

import type { LoginRequest, User } from "../types";

export interface AuthContextValue {
  /** The signed-in user, or null when unauthenticated. */
  user: User | null;
  /** True while the initial session hydration is in flight. */
  loading: boolean;
  /** Authenticate with credentials and load the user profile. */
  login: (credentials: LoginRequest) => Promise<void>;
  /** Clear the session and persisted token. */
  logout: () => void;
}

export const AuthContext = createContext<AuthContextValue | undefined>(undefined);

/** Access the authentication context. Throws if used outside the provider. */
export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider.");
  }
  return context;
}
