/**
 * Board page. Lets the user pick a project, shows its task board, and exposes
 * task creation. Composes the auth, projects and tasks hooks.
 */
import { useEffect, useState, type JSX } from "react";

import Header from "../components/Header";
import TaskBoard from "../components/TaskBoard";
import TaskForm from "../components/TaskForm";
import { useAuth } from "../hooks/authContext";
import { useProjects } from "../hooks/useProjects";
import { useTasks } from "../hooks/useTasks";
import type { TaskStatus } from "../types";
import styles from "../styles/BoardPage.module.css";

export default function BoardPage(): JSX.Element {
  // RequireAuth guarantees a user here.
  const { user, logout } = useAuth();
  const { projects, loading: projectsLoading, error: projectsError } = useProjects();
  const [selectedProjectId, setSelectedProjectId] = useState<number | null>(null);
  const [mutationError, setMutationError] = useState<string | null>(null);

  const {
    tasks,
    loading: tasksLoading,
    error: tasksError,
    createTask,
    moveTask,
    deleteTask,
  } = useTasks(selectedProjectId);

  // Select the first project once the list resolves.
  useEffect(() => {
    if (selectedProjectId === null && projects.length > 0) {
      setSelectedProjectId(projects[0].id);
    }
  }, [projects, selectedProjectId]);

  const handleMove = (id: number, status: TaskStatus): void => {
    setMutationError(null);
    moveTask(id, status).catch((err: unknown) => {
      setMutationError(err instanceof Error ? err.message : "Could not move the task.");
    });
  };

  const handleDelete = (id: number): void => {
    setMutationError(null);
    deleteTask(id).catch((err: unknown) => {
      setMutationError(err instanceof Error ? err.message : "Could not delete the task.");
    });
  };

  if (!user) {
    return <div className={styles.state}>Loading…</div>;
  }

  return (
    <div className={styles.page}>
      <Header user={user} onLogout={logout} />

      <main className={styles.main}>
        <div className={styles.toolbar}>
          <label className={styles.projectPicker}>
            <span className={styles.projectLabel}>Project</span>
            <select
              className={styles.projectSelect}
              value={selectedProjectId ?? ""}
              onChange={(event) =>
                setSelectedProjectId(event.target.value === "" ? null : Number(event.target.value))
              }
              disabled={projectsLoading || projects.length === 0}
              aria-label="Select project"
            >
              {projects.length === 0 && <option value="">No projects</option>}
              {projects.map((project) => (
                <option key={project.id} value={project.id}>
                  {project.name}
                </option>
              ))}
            </select>
          </label>
        </div>

        {projectsError !== null && (
          <p className={styles.error} role="alert">
            {projectsError}
          </p>
        )}

        {selectedProjectId !== null && (
          <TaskForm projectId={selectedProjectId} onCreate={createTask} />
        )}

        {tasksError !== null && (
          <p className={styles.error} role="alert">
            {tasksError}
          </p>
        )}

        {mutationError !== null && (
          <p className={styles.error} role="alert">
            {mutationError}
          </p>
        )}

        {tasksLoading ? (
          <div className={styles.state}>Loading tasks…</div>
        ) : selectedProjectId === null ? (
          <div className={styles.state}>
            {projectsLoading ? "Loading projects…" : "Create a project to get started."}
          </div>
        ) : (
          <TaskBoard tasks={tasks} onMove={handleMove} onDelete={handleDelete} />
        )}
      </main>
    </div>
  );
}
