/// <reference types="vite/client" />

/** Typed access to the Vite environment variables this app reads. */
interface ImportMetaEnv {
  /** Base URL of the TaskTracker API (e.g. http://localhost:8000). */
  readonly VITE_API_BASE_URL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

/** Allow importing CSS modules with typed default exports. */
declare module "*.module.css" {
  const classes: Readonly<Record<string, string>>;
  export default classes;
}
