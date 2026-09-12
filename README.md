# TaskTracker

The demo application for the O'Reilly live course **AI Code Review in Production**: a production-shaped task and project management board with a real CI pipeline, and one pull request that carries ten deliberately planted review findings.

TaskTracker pairs a typed FastAPI backend with a React + TypeScript single-page app. Organise work into projects, track tasks across a `todo → in_progress → done` board, set priorities, assignees and due dates, and secure everything behind JWT authentication. It runs on SQLite out of the box and is ready for Postgres in production.

## The course

During the live course you do three things with this repository, all from the browser:

1. **Review the prepared pull request** on the `demo/add-search` branch the way you would on a Monday morning, and post what you find. The branch adds task search and filtering and includes intentional review-worthy code, architectural choices and a testing gap.
2. **Watch the reviewer get wired in live.** [PR-Agent](https://github.com/the-pr-agent/pr-agent), running as a GitHub Action, is added to this repository with one workflow file and one secret, and its findings are compared with the room's.
3. **Write one review rule** for that pull request, and see one rule from the room run live.

Nothing to install during the session. Running the same reviewer on your own code is the homework below.

## Homework: run the reviewer on your own pull request

1. Fork this repository, or use any repository you own.
2. Create `.github/workflows/pr_agent.yml` with the workflow below.
3. Add one repository secret named `OPENAI_KEY` (Settings, then Secrets and variables, then Actions). The account needs billing enabled; a review costs cents.
4. Open a pull request. The Action posts `/describe` and `/review` comments in about a minute.
5. Type `/improve` or `/ask "your question"` as a PR comment for more. To teach it a rule, add an env line such as `pr_reviewer.extra_instructions: "Flag any hardcoded credential or token constant."` and comment `/review` again.

```yaml
# .github/workflows/pr_agent.yml
name: PR Agent

on:
  pull_request:
    types: [opened, reopened, ready_for_review]
  issue_comment:

permissions:
  issues: write
  pull-requests: write
  contents: write

jobs:
  pr_agent_job:
    if: ${{ github.event.sender.type != 'Bot' }}
    runs-on: ubuntu-latest
    name: Run PR Agent
    steps:
      - name: PR Agent
        uses: the-pr-agent/pr-agent@v0.45.0     # pin a release; check for newer
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}      # auto-provided by Actions
          OPENAI_KEY: ${{ secrets.OPENAI_KEY }}          # OpenAI is the default provider
          config.reasoning_effort: "low"                 # keeps the findings, 2 to 3x faster
          github_action_config.auto_review: "true"
          github_action_config.auto_describe: "true"
          github_action_config.auto_improve: "false"
```

Three gotchas, all learned the hard way:

- The boolean toggles must be quoted strings. Unquoted, they fail silently.
- The automatic tools fire on `opened`, `reopened` and `ready_for_review`. For a pull request that already existed **before** you added the workflow, GitHub evaluates the run against a merge commit that predates the workflow, so none of those events will start it. Click **Update branch** on the pull request first (or push any commit to it), then mark it ready for review. Or skip the automatic path and comment `/review`, which always runs the workflow from your default branch.
- Slash commands (`/review`, `/improve`, `/ask`) use the workflow on your default branch, so a rule you add to the workflow on `main` applies to every open pull request on the next command, with no rebase.

## When you outgrow the Action

The companion repository, [tasktracker-selfhosted](https://github.com/SerhiiYakovenko/tasktracker-selfhosted), is the same application reviewed by a self-hosted fork of PR-Agent running as a GitHub App, with custom review logic and slash commands such as `/check_standards`. It is the follow-up path the course ends on, for teams who want their own model, their own data boundary and their own rules engine.

## Features

- **Projects** — group work into projects scoped to their owner.
- **Task board** — Kanban-style columns (`todo`, `in_progress`, `done`) with one-call moves between columns.
- **Rich tasks** — title, description, priority (`low` / `medium` / `high`), assignee and due date.
- **Filtering & pagination** — list tasks by project, status or assignee with paginated responses.
- **JWT authentication** — register, log in and call the API with a bearer token; passwords hashed with bcrypt.
- **Typed end to end** — Pydantic v2 models on the backend mirrored by TypeScript types on the frontend.
- **Production-shaped** — service layer, dependency injection, centralized config, structured logging, CORS, Docker and CI.
- **Interactive API docs** — OpenAPI / Swagger UI served automatically by FastAPI at `/docs`.

## Tech stack

| Layer    | Technologies |
|----------|--------------|
| Frontend | React 18, TypeScript, Vite, React Router, CSS Modules, Vitest + Testing Library, ESLint |
| Backend  | Python 3.12, FastAPI, SQLAlchemy 2.x, Pydantic v2 + pydantic-settings, python-jose (JWT), passlib[bcrypt], uvicorn, pytest, ruff |
| Data     | SQLite by default; Postgres-ready via `DATABASE_URL` |
| Ops      | Docker, docker-compose, GitHub Actions CI |

## Run it locally

### Docker (quickest)

```bash
docker-compose up --build
```

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs

The backend runs an idempotent seed on startup. Sign in with the demo account:

- **Email:** `demo@tasktracker.dev`
- **Password:** `change-me`

### Local development

**Backend:**

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Optionally load demo data:

```bash
python -m app.seed
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

To build for production:

```bash
npm run build && npm run preview
```

## Project structure

```
tasktracker/
├── README.md
├── docker-compose.yml
├── .github/workflows/ci.yml      # CI: backend ruff+pytest, frontend eslint+build+vitest
├── backend/
│   ├── requirements.txt
│   ├── .env.example
│   ├── Dockerfile
│   └── app/
│       ├── main.py
│       ├── config.py
│       ├── database.py
│       ├── logging_config.py
│       ├── seed.py
│       ├── api/
│       │   ├── deps.py
│       │   └── routers/
│       ├── core/security.py
│       ├── models/
│       ├── schemas/
│       └── services/
│   └── tests/
└── frontend/
    ├── package.json
    ├── tsconfig.json
    ├── vite.config.ts
    ├── .eslintrc.cjs
    ├── index.html
    ├── Dockerfile
    └── src/
        ├── main.tsx
        ├── App.tsx
        ├── types.ts
        ├── api/client.ts
        ├── components/
        ├── pages/
        ├── hooks/
        ├── styles/
        └── __tests__/
```

## API

All endpoints are versioned under `/api/v1`, except the health check. Bearer token required except where noted.

| Method | Path | Description |
|--------|------|-------------|
| `GET`    | `/health`                  | Liveness check. |
| `POST`   | `/api/v1/auth/register`    | Register: `{email, password, full_name}` → `UserOut`. |
| `POST`   | `/api/v1/auth/login`       | Log in: `{email, password}` → `{access_token, token_type}`. |
| `GET`    | `/api/v1/users/me`         | Current user. |
| `GET`/`POST`/`PATCH`/`DELETE` | `/api/v1/projects[/{id}]` | Projects CRUD. |
| `GET`/`POST`/`PATCH`/`DELETE` | `/api/v1/tasks[/{id}]` | Tasks CRUD with filters. |
| `POST`   | `/api/v1/tasks/{id}/move`  | Move task: `{status}` → `TaskOut`. |

Full spec at `/docs` when backend is running.

## Testing

**Backend:** `cd backend && ruff check . && pytest`  
**Frontend:** `cd frontend && npm run lint && npm run build && npm run test`

CI runs all checks on every push and PR (`.github/workflows/ci.yml`). CI is red on the `demo/add-search` branch by design: three of the ten planted findings are the kind a linter catches.

## Configuration

Environment-driven via `pydantic-settings`. Copy the template:

```bash
cp backend/.env.example backend/.env
```

Key variables: `APP_NAME`, `ENVIRONMENT`, `LOG_LEVEL`, `DATABASE_URL`, `SECRET_KEY`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `BACKEND_CORS_ORIGINS`, `VITE_API_BASE_URL` (frontend build-time).

See `backend/.env.example` and `frontend/.env.example` for all options.

## License

MIT.

---

Built for the O'Reilly live course *AI Code Review in Production* (November 2026). The application and its planted pull request were first used in a hands-on workshop at TechLeadConf 2026.
