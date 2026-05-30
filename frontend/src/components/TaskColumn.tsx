/**
 * A single status column on the board. Renders its tasks as cards and shows a
 * count badge plus an empty-state placeholder.
 */
import type { JSX } from "react";

import type { Task, TaskStatus } from "../types";
import TaskCard from "./TaskCard";
import styles from "../styles/TaskColumn.module.css";

interface TaskColumnProps {
  title: string;
  status: TaskStatus;
  tasks: Task[];
  onMove: (id: number, status: TaskStatus) => void;
  onDelete: (id: number) => void;
}

export default function TaskColumn({
  title,
  status,
  tasks,
  onMove,
  onDelete,
}: TaskColumnProps): JSX.Element {
  return (
    <section className={styles.column} aria-label={title} data-status={status}>
      <header className={styles.header}>
        <h3 className={styles.title}>{title}</h3>
        <span className={styles.count}>{tasks.length}</span>
      </header>

      <div className={styles.list}>
        {tasks.length === 0 ? (
          <p className={styles.empty}>No tasks</p>
        ) : (
          tasks.map((task) => (
            <TaskCard key={task.id} task={task} onMove={onMove} onDelete={onDelete} />
          ))
        )}
      </div>
    </section>
  );
}
