# TaskTracker

A production-shaped task and project management board: the demo app for AI code review sessions.

TaskTracker pairs a typed FastAPI backend with a React + TypeScript single-page app. Organise work into projects, track tasks across a `todo → in_progress → done` board, set priorities, assignees and due dates, and secure everything behind JWT authentication. It runs on SQLite out of the box and is ready for Postgres in production. The `demo/add-search` branch includes intentional review findings for the sessions' AI reviewer.

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

## Where this repo is used

### O'Reilly live course: AI Code Review in Production

During the course you read the pull request on the `demo/add-search` branch and post what you find; then the reviewer, [PR-Agent](https://github.com/qodo-ai/pr-agent) running as a GitHub Action, is wired into this repository live with one workflow file and one secret, and its findings are compared with the room's. Nothing to install during the session.

**Homework: run the same reviewer on your own pull request.**

1. Fork this repository (or use any repository you own).
2. Create `.github/workflows/pr_agent.yml` with the workflow below.
3. Add one repository secret named `OPENAI_KEY` (Settings, Secrets and variables, Actions). The account needs billing enabled; a review costs cents.
4. Open a pull request, or mark a draft as ready for review. The Action posts `/describe` and `/review` comments in about a minute.
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
        uses: the-pr-agent/pr-agent@v0.35.0     # pinned release. Re-verify latest tag at re-arm time
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}                  # auto-provided by Actions
          OPENAI_KEY: ${{ secrets.OPENAI_KEY }}                      # OpenAI is PR-Agent default provider, nothing else needed
          config.reasoning_effort: "low"                            # "low" keeps the findings and is 2 to 3x faster (verified)
          github_action_config.auto_review: "true"      
          github_action_config.auto_describe: "true"
          github_action_config.auto_improve: "false"
```

Two gotchas from the session: the boolean toggles must be quoted strings, and the auto tools fire on `opened`, `reopened`, and `ready_for_review` only.

### TechLeadConf 2026 workshop: Part A, Marketplace Action

This repo was **Part A** of the *AI-Powered Code Review* hands-on workshop at TechLeadConf 2026 (recorded on GitNation). Part A demonstrates how to add AI-powered code review to your GitHub workflow using an off-the-shelf GitHub Marketplace Action ([Qodo PR-Agent](https://github.com/qodo-ai/pr-agent)).

When you open or update a pull request on the `main` branch, the PR-Agent Action runs automatically via GitHub Actions. It analyzes the diff and posts inline review comments with findings, suggestions, and quality improvements — all without needing to host your own server.

**Review target:** Check the `demo/add-search` branch. This branch adds task search and filtering to the TaskTracker board and intentionally includes review-worthy code patterns, architectural choices, and testing gaps. It is a teaching artifact designed to show what an AI reviewer catches.

To see the Action in action:

1. Examine the code on the `demo/add-search` branch.
2. Open a pull request from `demo/add-search` into `main`.
3. Watch the PR-Agent Action run in the **Checks** tab.
4. Review the inline comments posted by the AI reviewer.

### When you outgrow the Action: self-hosted (workshop Part B)

The companion repo, [tasktracker-selfhosted](https://github.com/SerhiiYakovenko/tasktracker-selfhosted), shows the next step: running a fork of PR-Agent as a self-hosted GitHub App with custom review logic and slash commands (e.g., `/check_standards`). It was Part B of the workshop and is the follow-up path recommended at the end of the O'Reilly course, for teams who want full control over their AI reviewer, custom integrations, and on-premise deployment.

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

CI runs all checks on every push and PR (`.github/workflows/ci.yml`).

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

**Used in:** [TechLeadConf 2026 workshop: AI-Powered Code Review](https://techleadconf.com/#workshop-ai-powered-code-review) (recorded on GitNation) | O'Reilly live course: *AI Code Review in Production* | [Self-hosted companion repo](https://github.com/SerhiiYakovenko/tasktracker-selfhosted)
