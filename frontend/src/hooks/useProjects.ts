/**
 * Hook for loading the signed-in user's projects.
 *
 * Loads the project list once on mount and tracks loading/error state. The
 * board uses the result to populate its project selector.
 */
import { useCallback, useEffect, useState } from "react";

import { ApiError, projectsApi } from "../api/client";
import type { Project } from "../types";

interface UseProjectsResult {
  projects: Project[];
  loading: boolean;
  error: string | null;
  reload: () => Promise<void>;
}

/** Normalize unknown errors into a user-facing message. */
function toMessage(error: unknown): string {
  if (error instanceof ApiError || error instanceof Error) {
    return error.message;
  }
  return "Could not load projects.";
}

export function useProjects(): UseProjectsResult {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const reload = useCallback(async (): Promise<void> => {
    setLoading(true);
    setError(null);
    try {
      const result = await projectsApi.list();
      setProjects(result);
    } catch (err) {
      setError(toMessage(err));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void reload();
  }, [reload]);

  return { projects, loading, error, reload };
}
