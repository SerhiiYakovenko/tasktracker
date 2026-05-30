/**
 * The Kanban board: groups tasks into the todo / in_progress / done columns.
 */
import { useMemo, type JSX } from "react";

import type { Task, TaskStatus } from "../types";
import TaskColumn from "./TaskColumn";
import styles from "../styles/TaskBoard.module.css";

interface ColumnDefinition {
  status: TaskStatus;
  title: string;
}

/** Column layout, left to right. */
const COLUMNS: readonly ColumnDefinition[] = [
  { status: "todo", title: "To Do" },
  { status: "in_progress", title: "In Progress" },
  { status: "done", title: "Done" },
];

interface TaskBoardProps {
  tasks: Task[];
  onMove: (id: number, status: TaskStatus) => void;
  onDelete: (id: number) => void;
}

export default function TaskBoard({ tasks, onMove, onDelete }: TaskBoardProps): JSX.Element {
  const tasksByStatus = useMemo<Record<TaskStatus, Task[]>>(() => {
    const grouped: Record<TaskStatus, Task[]> = {
      todo: [],
      in_progress: [],
      done: [],
    };
    for (const task of tasks) {
      grouped[task.status].push(task);
    }
    return grouped;
  }, [tasks]);

  return (
    <div className={styles.board}>
      {COLUMNS.map((column) => (
        <TaskColumn
          key={column.status}
          title={column.title}
          status={column.status}
          tasks={tasksByStatus[column.status]}
          onMove={onMove}
          onDelete={onDelete}
        />
      ))}
    </div>
  );
}
