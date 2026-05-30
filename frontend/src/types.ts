/**
 * Domain types for the TaskTracker frontend.
 *
 * These mirror the backend Pydantic response models (UserOut / ProjectOut /
 * TaskOut) and request payloads exactly. Field names and enum values must stay
 * in sync with `backend/app/schemas`.
 */

/** Lifecycle state of a task. Matches the backend `TaskStatus` enum. */
export type TaskStatus = "todo" | "in_progress" | "done";

/** Relative importance of a task. Matches the backend `TaskPriority` enum. */
export type TaskPriority = "low" | "medium" | "high";

/** Public representation of a user (never includes the password hash). */
export interface User {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
  created_at: string;
}

/** A project that groups tasks and is owned by a single user. */
export interface Project {
  id: number;
  name: string;
  description: string | null;
  owner_id: number;
  created_at: string;
}

/** A unit of work belonging to a project. */
export interface Task {
  id: number;
  title: string;
  description: string | null;
  status: TaskStatus;
  priority: TaskPriority;
  project_id: number;
  assignee_id: number | null;
  due_date: string | null;
  created_at: string;
  updated_at: string;
}

/** Bearer token returned by the login endpoint. */
export interface Token {
  access_token: string;
  token_type: "bearer";
}

/** Credentials accepted by `POST /auth/login`. */
export interface LoginRequest {
  email: string;
  password: string;
}

/** Payload accepted by `POST /auth/register`. */
export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
}

/** Payload accepted by `POST /projects`. */
export interface ProjectCreate {
  name: string;
  description?: string | null;
}

/** Payload accepted by `POST /tasks`. */
export interface TaskCreate {
  title: string;
  description?: string | null;
  status?: TaskStatus;
  priority?: TaskPriority;
  project_id: number;
  assignee_id?: number | null;
  due_date?: string | null;
}

/** Partial payload accepted by `PATCH /tasks/{id}`. */
export interface TaskUpdate {
  title?: string;
  description?: string | null;
  status?: TaskStatus;
  priority?: TaskPriority;
  assignee_id?: number | null;
  due_date?: string | null;
}

/** Generic paginated envelope returned by list endpoints. */
export interface Page<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
}

/** Query parameters supported by `GET /tasks`. */
export interface TaskQuery {
  project_id?: number;
  status?: TaskStatus;
  assignee_id?: number;
  page?: number;
  size?: number;
}
