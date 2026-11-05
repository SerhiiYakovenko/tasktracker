/**
 * Typed HTTP client for the TaskTracker backend.
 *
 * Centralizes the base URL, JWT bearer header, JSON (de)serialization and
 * error handling so that components and hooks never touch `fetch` directly.
 */
import type {
  LoginRequest,
  Page,
  Project,
  ProjectCreate,
  RegisterRequest,
  Task,
  TaskCreate,
  TaskQuery,
  TaskStatus,
  TaskUpdate,
  Token,
  User,
} from "../types";

/** Base URL of the API, read from Vite env with a sensible dev default. */
const API_BASE_URL: string =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

const API_PREFIX = "/api/v1";
const TOKEN_STORAGE_KEY = "tasktracker.token";

/**
 * Error raised for any non-2xx response. Carries the HTTP status so callers
 * can branch on it (e.g. clear the session on 401).
 */
export class ApiError extends Error {
  readonly status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

/** Read the persisted bearer token, if any. */
export function getToken(): string | null {
  return localStorage.getItem(TOKEN_STORAGE_KEY);
}

/** Persist the bearer token for subsequent authenticated requests. */
export function setToken(token: string): void {
  localStorage.setItem(TOKEN_STORAGE_KEY, token);
}

/** Remove the persisted bearer token (logout). */
export function clearToken(): void {
  localStorage.removeItem(TOKEN_STORAGE_KEY);
}

interface RequestOptions {
  method?: "GET" | "POST" | "PATCH" | "DELETE";
  body?: unknown;
  /** When false, the Authorization header is omitted (login/register). */
  auth?: boolean;
}

/** Extract a human-readable message from a FastAPI/JSON error body. */
function extractErrorMessage(status: number, payload: unknown): string {
  if (payload && typeof payload === "object" && "detail" in payload) {
    const detail = (payload as { detail: unknown }).detail;
    if (typeof detail === "string") {
      return detail;
    }
    // Pydantic 422 returns an array of validation errors.
    if (Array.isArray(detail)) {
      const messages = detail
        .map((item) =>
          item && typeof item === "object" && "msg" in item
            ? String((item as { msg: unknown }).msg)
            : null,
        )
        .filter((msg): msg is string => msg !== null);
      if (messages.length > 0) {
        return messages.join("; ");
      }
    }
  }
  return `Request failed with status ${status}`;
}

/** Build a query string from a partial record, skipping undefined values. */
function buildQuery(params: Record<string, string | number | undefined>): string {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined) {
      search.set(key, String(value));
    }
  }
  const query = search.toString();
  return query ? `?${query}` : "";
}

/**
 * Perform a typed JSON request against the API.
 *
 * @throws {ApiError} when the response status is not in the 2xx range.
 */
async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = "GET", body, auth = true } = options;
  const headers: Record<string, string> = { Accept: "application/json" };

  if (body !== undefined) {
    headers["Content-Type"] = "application/json";
  }
  if (auth) {
    const token = getToken();
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
  }

  const response = await fetch(`${API_BASE_URL}${API_PREFIX}${path}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  if (response.status === 204) {
    return undefined as T;
  }

  let payload: unknown = null;
  const text = await response.text();
  if (text) {
    payload = JSON.parse(text) as unknown;
  }

  if (!response.ok) {
    throw new ApiError(response.status, extractErrorMessage(response.status, payload));
  }

  return payload as T;
}

/** Auth endpoints. */
export const authApi = {
  register(payload: RegisterRequest): Promise<User> {
    return request<User>("/auth/register", { method: "POST", body: payload, auth: false });
  },
  login(payload: LoginRequest): Promise<Token> {
    return request<Token>("/auth/login", { method: "POST", body: payload, auth: false });
  },
};

/** User endpoints. */
export const usersApi = {
  me(): Promise<User> {
    return request<User>("/users/me");
  },
};

/** Project endpoints. */
export const projectsApi = {
  list(): Promise<Project[]> {
    return request<Project[]>("/projects");
  },
  create(payload: ProjectCreate): Promise<Project> {
    return request<Project>("/projects", { method: "POST", body: payload });
  },
  get(id: number): Promise<Project> {
    return request<Project>(`/projects/${id}`);
  },
};

/** Task endpoints. */
export const tasksApi = {
  list(query: TaskQuery = {}): Promise<Page<Task>> {
    return request<Page<Task>>(`/tasks${buildQuery({ ...query })}`);
  },
  create(payload: TaskCreate): Promise<Task> {
    return request<Task>("/tasks", { method: "POST", body: payload });
  },
  update(id: number, payload: TaskUpdate): Promise<Task> {
    return request<Task>(`/tasks/${id}`, { method: "PATCH", body: payload });
  },
  move(id: number, status: TaskStatus): Promise<Task> {
    return request<Task>(`/tasks/${id}/move`, { method: "POST", body: { status } });
  },
  remove(id: number): Promise<void> {
    return request<void>(`/tasks/${id}`, { method: "DELETE" });
  },
};

/** Search the current user's tasks by free-text query. */
export function searchTasks(q: string): Promise<any> {
  return request<any>(`/search${buildQuery({ q })}`);
}
