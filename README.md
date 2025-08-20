# dota-fantasy

Monorepo for dota-fantasy: ingest OpenDota, compute patch-aware stats, ML predictions, and a Draft Lab UI.

Quick start (dev):

- Bring up services:

```sh
make up
```

- Visit API: http://localhost:8000/healthz
- Visit Web: http://localhost:5173/

Repo layout:

- backend: FastAPI, SQLAlchemy, Alembic, jobs, ML
- frontend: React + Vite + TS + Tailwind
- devops: Docker Compose

See tickets F1..F10 in the request for details.