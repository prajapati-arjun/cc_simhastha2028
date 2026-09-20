# Simhastha 2028 — Ujjain Digital Experience Platform

Sprint 1 (Phase 1: "Foundation") local development scaffold. This is a
**locally-runnable prototype via docker-compose only** — there is no live
cloud deployment and no integration with any real police/medical/CCTV/
government system (see `project-specs/simhastha-sprint1-setup.md`, settled
decisions #1 and #2, and `docs/PROTOTYPE_LIMITATIONS.md` once published).

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (includes
  the Docker Compose v2 CLI, invoked below as `docker compose`). No local
  Node.js or Python install is required — everything runs in containers.
- Ports `3000`, `8000`, `5432`, `6379` free on your machine.

## Repo layout

```
apps/api/     FastAPI backend (Python) — app code, Alembic migrations, tests
apps/web/     Next.js frontend (TypeScript, App Router, Tailwind CSS)
infra/        docker-compose.yml for the local dev stack
Docs/         PRD source material (reference only)
docs/         This sprint's prototype-limitations / roadmap docs
project-specs/   Settled sprint scope decisions
project-tasks/   Sprint task list
```

## 1. Clone and configure environment variables

```bash
git clone <repo-url> Claude_Community
cd Claude_Community
cp .env.example .env
```

`.env` at the repo root holds Postgres credentials, the API secret key, and
the frontend's API base URL. Every value already has a working default baked
into `infra/docker-compose.yml`, so the stack runs even if you skip this step
— copy `.env.example` only if you want to change credentials or ports
locally. Do not commit `.env` (it's already gitignored).

## 2. Start the stack

Run from the **repo root**, passing the root `.env` explicitly since the
compose file lives in `infra/`:

```bash
docker compose --env-file .env -f infra/docker-compose.yml up --build
```

(Add `-d` to run detached.) This builds and starts four containers:

| Service    | Image / build             | Port (host) | Purpose                          |
|------------|----------------------------|-------------|-----------------------------------|
| `postgres` | `postgis/postgis:16-3.4`   | 5432        | PostgreSQL + PostGIS database    |
| `redis`    | `redis:7-alpine`           | 6379        | Cache                              |
| `api`      | built from `apps/api`      | 8000        | FastAPI backend (`uvicorn --reload`) |
| `web`      | built from `apps/web`      | 3000        | Next.js frontend (`next dev`)     |

`api` waits for `postgres`/`redis` health checks before starting; `web`
starts after `api`. Both `api` and `web` bind-mount their app directory into
the container, so code changes hot-reload without rebuilding the image.

To stop the stack: `docker compose --env-file .env -f infra/docker-compose.yml down`
(add `-v` to also drop the Postgres/Redis data volumes).

## 3. Verify it's up

- API health check: <http://localhost:8000/health> → `{"status": "ok", ...}`
- API interactive docs (Swagger UI): <http://localhost:8000/docs>
- Web app: <http://localhost:3000> → Simhastha 2028 placeholder homepage

```bash
curl http://localhost:8000/health
```

## 4. Database migrations (Alembic)

The Alembic scaffold (`apps/api/alembic.ini`, `apps/api/migrations/`) is
wired to read `DATABASE_URL` from the environment, so it works against the
`postgres` container out of the box. No migration files exist yet in this
scaffold — Backend Architect authors them against the running stack:

```bash
# Author a new migration (Backend Architect, once models exist)
docker compose --env-file .env -f infra/docker-compose.yml exec api alembic revision -m "create <table>"

# Apply all pending migrations
docker compose --env-file .env -f infra/docker-compose.yml exec api alembic upgrade head
```

## 5. Seed data

> Placeholder — the seed script (9 named temples, sample ghats/events/
> emergency directory entries, one admin user) is owned by Backend Architect
> (task BE-02) and does not exist yet in this scaffold. Once added, it will
> be runnable as something like:
> `docker compose --env-file .env -f infra/docker-compose.yml exec api python -m app.db.seed`
> — update this section with the real command once BE-02 lands.

## 6. Running tests / lint

Backend tests (pytest, runs inside the `api` container against the live
scaffold — currently just the `/health` smoke test; Backend Architect adds
feature tests per API in BE-13):

```bash
docker compose --env-file .env -f infra/docker-compose.yml exec api pytest -v
```

Frontend build and lint (runs inside the `web` container):

```bash
docker compose --env-file .env -f infra/docker-compose.yml exec web npm run build
docker compose --env-file .env -f infra/docker-compose.yml exec web npm run lint
```

## Notes / scope reminders

- **No real cloud deployment.** docker-compose is the only deployment path
  for this sprint (spec decision #2). Do not add Kubernetes/Terraform/cloud
  provisioning configs this sprint.
- **Out of scope this sprint**: Kafka, OpenSearch, computer vision, AI/RAG
  stack (see PRD Table 4 vs. spec — these are Phase 2/3).
- This scaffold intentionally contains **no business logic, DB models, or
  page content** — `app/main.py` only exposes `GET /health`, and
  `app/page.tsx` is a placeholder. Backend Architect and Frontend Developer
  build the real APIs/pages on top of this shell.
- The `api` and `web` Dockerfiles are **dev-mode images** (`uvicorn --reload`,
  `next dev`), not production builds — appropriate for this sprint's "local
  dev-ready scaffold" goal, not for a production deploy.
