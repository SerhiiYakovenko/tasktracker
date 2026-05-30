/**
 * A single task rendered as a board card. Shows title, optional description,
 * priority, due date, and controls to move the task between columns or delete
 * it. All mutations are delegated to the parent via callbacks.
 */
import type { JSX } from "react";

import type { Task, TaskStatus } from "../types";
import styles from "../styles/TaskCard.module.css";

/** Human-readable labels for each status, used in the move menu. */
const STATUS_LABELS: Record<TaskStatus, string> = {
  todo: "To Do",
  in_progress: "In Progress",
  done: "Done",
};

const STATUS_ORDER: readonly TaskStatus[] = ["todo", "in_progress", "done"];

interface TaskCardProps {
  task: Task;
  onMove: (id: number, status: TaskStatus) => void;
  onDelete: (id: number) => void;
}

/** Format an ISO date string as a short local date, or null when absent. */
function formatDueDate(value: string | null): string | null {
  if (value === null) {
    return null;
  }
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return null;
  }
  return parsed.toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export default function TaskCard({ task, onMove, onDelete }: TaskCardProps): JSX.Element {
  const dueLabel = formatDueDate(task.due_date);
  const otherStatuses = STATUS_ORDER.filter((status) => status !== task.status);

  return (
    <article className={styles.card} data-testid={`task-${task.id}`}>
      <div className={styles.header}>
        <h4 className={styles.title}>{task.title}</h4>
        <span
          className={`${styles.priority} ${styles[`priority_${task.priority}`]}`}
          aria-label={`Priority: ${task.priority}`}
        >
          {task.priority}
        </span>
      </div>

      {task.description !== null && task.description !== "" && (
        <p className={styles.description}>{task.description}</p>
      )}

      <div className={styles.meta}>
        {dueLabel !== null && (
          <span className={styles.due}>Due {dueLabel}</span>
        )}
      </div>

      <div className={styles.actions}>
        {otherStatuses.map((status) => (
          <button
            key={status}
            type="button"
            className={styles.moveButton}
            onClick={() => onMove(task.id, status)}
          >
            → {STATUS_LABELS[status]}
          </button>
        ))}
        <button
          type="button"
          className={styles.deleteButton}
          onClick={() => onDelete(task.id)}
          aria-label={`Delete ${task.title}`}
        >
          Delete
        </button>
      </div>
    </article>
  );
}
