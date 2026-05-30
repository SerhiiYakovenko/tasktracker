/**
 * Hook for loading and mutating the tasks of a single project.
 *
 * Owns the task list, loading/error state, and exposes create/move/delete
 * operations that keep the local cache in sync with the server response.
 */
import { useCallback, useEffect, useState } from "react";

import { ApiError, tasksApi } from "../api/client";
import type { Task, TaskCreate, TaskStatus } from "../types";

/** Maximum tasks fetched per board. The demo board is not paginated in the UI. */
const BOARD_PAGE_SIZE = 100;

interface UseTasksResult {
  tasks: Task[];
  loading: boolean;
  error: string | null;
  reload: () => Promise<void>;
  createTask: (payload: TaskCreate) => Promise<void>;
  moveTask: (id: number, status: TaskStatus) => Promise<void>;
  deleteTask: (id: number) => Promise<void>;
}

/** Normalize unknown errors into a user-facing message. */
function toMessage(error: unknown): string {
  if (error instanceof ApiError) {
    return error.message;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return "Something went wrong.";
}

/**
 * Manage the task collection for a given project.
 *
 * @param projectId The project whose tasks to load, or null while none chosen.
 */
export function useTasks(projectId: number | null): UseTasksResult {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const reload = useCallback(async (): Promise<void> => {
    if (projectId === null) {
      setTasks([]);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const page = await tasksApi.list({ project_id: projectId, size: BOARD_PAGE_SIZE });
      setTasks(page.items);
    } catch (err) {
      setError(toMessage(err));
    } finally {
      setLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    void reload();
  }, [reload]);

  const createTask = useCallback(async (payload: TaskCreate): Promise<void> => {
    const created = await tasksApi.create(payload);
    setTasks((current) => [...current, created]);
  }, []);

  const moveTask = useCallback(async (id: number, status: TaskStatus): Promise<void> => {
    const updated = await tasksApi.move(id, status);
    setTasks((current) => current.map((task) => (task.id === id ? updated : task)));
  }, []);

  const deleteTask = useCallback(async (id: number): Promise<void> => {
    await tasksApi.remove(id);
    setTasks((current) => current.filter((task) => task.id !== id));
  }, []);

  return { tasks, loading, error, reload, createTask, moveTask, deleteTask };
}
