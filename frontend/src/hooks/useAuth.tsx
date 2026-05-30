/**
 * Authentication provider.
 *
 * Wraps the app, exposes the current user, and centralizes login/logout. On
 * mount it hydrates the session from a persisted token by calling /users/me.
 * The context object and the `useAuth` consumer hook live in `authContext.ts`.
 */
import {
  useCallback,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import { ApiError, authApi, clearToken, getToken, setToken, usersApi } from "../api/client";
import type { LoginRequest, User } from "../types";
import { AuthContext, type AuthContextValue } from "./authContext";

/** Provides authentication state to the component tree. */
export function AuthProvider({ children }: { children: ReactNode }): JSX.Element {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    let active = true;

    async function hydrate(): Promise<void> {
      if (!getToken()) {
        setLoading(false);
        return;
      }
      try {
        const me = await usersApi.me();
        if (active) {
          setUser(me);
        }
      } catch (error) {
        // A stale or invalid token: drop it and stay logged out.
        if (error instanceof ApiError && error.status === 401) {
          clearToken();
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    void hydrate();
    return () => {
      active = false;
    };
  }, []);

  const login = useCallback(async (credentials: LoginRequest): Promise<void> => {
    const token = await authApi.login(credentials);
    setToken(token.access_token);
    const me = await usersApi.me();
    setUser(me);
  }, []);

  const logout = useCallback((): void => {
    clearToken();
    setUser(null);
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({ user, loading, login, logout }),
    [user, loading, login, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
