# Production deployment guide

Minimal setup for **Vercel** (React/Vite frontend), **Render** (FastAPI backend), and **Neon** (PostgreSQL).

---

## Prerequisites

- Git repository connected to Vercel and Render
- [Neon](https://neon.tech) project with a PostgreSQL connection string
- ML artifacts committed or available on the server:
  - `app/ml/lgbm_model.pkl` (required for `/rankings` and `/portfolio`)
  - `app/ml/lstm_global.pt` (optional; LSTM uses momentum fallback if missing)

---

## 1. Neon database

1. Create a project in Neon and copy the **pooled** connection string.
2. Ensure the URL includes SSL, e.g. `?sslmode=require`.
3. Run schema initialization locally once (with `DATABASE_URL` set):

   ```bash
   python init_db.py
   ```

4. In Render, set `DATABASE_URL` to the Neon string (see below).

The API normalizes `postgres://` → `postgresql+psycopg2://` and uses connection pooling with `pool_pre_ping` for serverless Postgres.

**Health checks**

- `GET /health` — liveness (no DB)
- `GET /health/ready` — readiness (includes DB probe, returns 503 if DB down)

---

## 2. Render backend

### Dashboard setup

| Setting | Value |
|--------|--------|
| **Root directory** | `.` (repo root) |
| **Build command** | `pip install -r requirements.txt` |
| **Start command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| **Health check path** | `/health` |

### Environment variables

| Variable | Example |
|----------|---------|
| `DATABASE_URL` | `postgresql://...@...neon.tech/neondb?sslmode=require` |
| `ENVIRONMENT` | `production` |
| `LOG_LEVEL` | `INFO` |
| `CORS_ORIGINS` | `https://your-app.vercel.app,http://localhost:5173` |

Use your real Vercel URL(s), comma-separated, **no trailing slashes**.

Alternatively, deploy with the included `render.yaml` blueprint.

### Local production test

```bash
pip install -r requirements.txt
export DATABASE_URL="postgresql://..."
export ENVIRONMENT=production
export CORS_ORIGINS=http://localhost:4173
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## 3. Vercel frontend

### Dashboard setup

| Setting | Value |
|--------|--------|
| **Root directory** | `frontend` |
| **Framework preset** | Vite |
| **Build command** | `npm run build` |
| **Output directory** | `dist` |

### Environment variables

| Variable | Value |
|----------|--------|
| `VITE_API_BASE_URL` | `https://your-service.onrender.com` (Render API URL, no trailing slash) |

Set for **Production** (and Preview if desired).

`frontend/vercel.json` rewrites all routes to `index.html` for React Router.

### Local production build test

```bash
cd frontend
cp .env.example .env.local
# Edit VITE_API_BASE_URL
npm ci
npm run build
npm run preview
```

Open `http://localhost:4173` and confirm API calls hit your backend.

---

## 4. Commands reference

| Context | Command |
|---------|---------|
| Frontend dev | `cd frontend && npm run dev` |
| Frontend build | `cd frontend && npm run build` |
| Backend dev | `uvicorn app.main:app --reload --port 8000` |
| Backend prod | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |

---

## 5. Known deployment blockers

| Issue | Mitigation |
|-------|------------|
| Missing `lgbm_model.pkl` | `/rankings` and `/portfolio` return errors; add model file to repo or build step |
| Missing `DATABASE_URL` | DB routes fail; `/health` still OK, `/health/ready` returns 503 |
| CORS errors | Set `CORS_ORIGINS` on Render to exact Vercel origin (https, no path) |
| Cold start + `/portfolio` slow | First request ranks many symbols; consider smaller `top_k` or paid Render plan |
| `VITE_API_BASE_URL` unset on Vercel | Production build logs error; API calls fail until env is set |
| Torch install size on Render | May lengthen builds; required for LSTM path |
| yfinance rate limits | External market data; retries may be needed under load |

---

## 6. Security checklist

- Never commit `.env` (use `.env.example` as template)
- Set `ENVIRONMENT=production` on Render
- Restrict `CORS_ORIGINS` to your frontend domain(s)
- Use Neon **pooled** connection string for web services
- Rotate database credentials if exposed

---

## 7. Post-deploy verification

1. `curl https://YOUR-RENDER-URL/health`
2. `curl https://YOUR-RENDER-URL/health/ready`
3. Open Vercel app → Dashboard loads portfolio/rankings
4. Browser devtools → Network tab shows API calls to Render URL (not localhost)
