/**
 * Form for creating a new task within the active project. Collects title,
 * description, priority and an optional due date, then hands a typed payload
 * to the parent. Resets on a successful submit.
 */
import { useState, type FormEvent, type JSX } from "react";

import type { TaskCreate, TaskPriority } from "../types";
import styles from "../styles/TaskForm.module.css";

const PRIORITIES: readonly TaskPriority[] = ["low", "medium", "high"];

interface TaskFormProps {
  projectId: number;
  onCreate: (payload: TaskCreate) => Promise<void>;
}

export default function TaskForm({ projectId, onCreate }: TaskFormProps): JSX.Element {
  const [title, setTitle] = useState<string>("");
  const [description, setDescription] = useState<string>("");
  const [priority, setPriority] = useState<TaskPriority>("medium");
  const [dueDate, setDueDate] = useState<string>("");
  const [submitting, setSubmitting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const reset = (): void => {
    setTitle("");
    setDescription("");
    setPriority("medium");
    setDueDate("");
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>): Promise<void> => {
    event.preventDefault();
    const trimmedTitle = title.trim();
    if (trimmedTitle === "") {
      setError("Title is required.");
      return;
    }

    setSubmitting(true);
    setError(null);
    const payload: TaskCreate = {
      title: trimmedTitle,
      description: description.trim() === "" ? null : description.trim(),
      priority,
      project_id: projectId,
      due_date: dueDate === "" ? null : new Date(dueDate).toISOString(),
    };

    try {
      await onCreate(payload);
      reset();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not create the task.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form className={styles.form} onSubmit={handleSubmit} aria-label="Create task">
      <div className={styles.row}>
        <input
          type="text"
          name="title"
          placeholder="Task title"
          value={title}
          onChange={(event) => setTitle(event.target.value)}
          className={styles.titleInput}
          aria-label="Task title"
        />
        <select
          name="priority"
          value={priority}
          onChange={(event) => setPriority(event.target.value as TaskPriority)}
          className={styles.select}
          aria-label="Priority"
        >
          {PRIORITIES.map((value) => (
            <option key={value} value={value}>
              {value}
            </option>
          ))}
        </select>
        <input
          type="date"
          name="due_date"
          value={dueDate}
          onChange={(event) => setDueDate(event.target.value)}
          className={styles.date}
          aria-label="Due date"
        />
        <button type="submit" className={styles.submit} disabled={submitting}>
          {submitting ? "Adding…" : "Add task"}
        </button>
      </div>

      <textarea
        name="description"
        placeholder="Description (optional)"
        value={description}
        onChange={(event) => setDescription(event.target.value)}
        className={styles.description}
        rows={2}
        aria-label="Description"
      />

      {error !== null && (
        <p className={styles.error} role="alert">
          {error}
        </p>
      )}
    </form>
  );
}
