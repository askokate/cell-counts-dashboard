# System Design Narrative

## Overview

This project is an end-to-end analytics system that transforms raw immune cell-count data into reproducible statistical insights and presents them through a reviewer-friendly interactive dashboard.

Design priorities:
- Reproducibility over environment complexity
- Transparent, reviewable analytics
- Clear separation between data, analytics, and presentation

---

## System diagram (detailed ASCII)

```
                                   ┌──────────────────────────────────────────┐
                                   │                User / Reviewer           │
                                   │  - Opens dashboard in browser            │
                                   │  - Applies filters / views results       │
                                   └──────────────────────────┬───────────────┘
                                                              │ HTTPS
                                                              ▼
                          ┌──────────────────────────────────────────────────────────┐
                          │                 Frontend (React + Vite)                  │
                          │  Host: Vercel (static build + CDN)                       │
                          │  - Renders tables and boxplots                           │
                          │  - Minimal client-side math                              │
                          │  - Calls backend APIs for computed results               │
                          │  Runtime (local/dev): http://localhost:5173             │
                          └──────────────────────────┬───────────────────────────────┘
                                                     │ REST (JSON)
                                                     │ e.g., /api/v1/...
                                                     ▼
                 ┌──────────────────────────────────────────────────────────────────────┐
                 │                      Backend API (FastAPI)                            │
                 │  Host: Render (Python web service)                                    │
                 │  - Computes frequencies, summaries, and statistical tests             │
                 │  - Encapsulates analytical definitions in one place                   │
                 │  - Returns analysis-ready JSON                                        │
                 │  Runtime (local/dev): http://localhost:8000                           │
                 └──────────────────────────┬───────────────────────────────────────────┘
                                            │ SQL queries
                                            ▼
                           ┌──────────────────────────────────────────┐
                           │            Relational Database           │
                           │            SQLite (analytics DB)         │
                           │  File: backend/data/app.db               │
                           │  - Normalized schema (projects, subjects, │
                           │    treatments, samples, populations)      │
                           │  - Long-format cell_counts fact table     │
                           └──────────────────────────┬───────────────┘
                                                      │ one-time build
                                                      ▼
                           ┌──────────────────────────────────────────┐
                           │              Data Ingestion              │
                           │  Input: data/cell-count.csv              │
                           │  Loader: backend/app/load_db.py          │
                           │  - Parses CSV                            │
                           │  - Populates SQLite with keys/constraints│
                           │  - Re-runnable to reproduce DB           │
                           └──────────────────────────────────────────┘


External integration surface (how this would plug into “real” systems)
---------------------------------------------------------------------
Today:
- CSV is the input format (repository-provided).
- SQLite is local to the backend service for easy reproducibility.

In a production scenario, the same interfaces naturally extend to:
- Upstream sources: LIMS / ELN exports, S3 drops, data warehouse extracts
- Database: Postgres/DuckDB with the same schema
- Downstream: reporting jobs, alerts, batch analytics, or embedding into a larger portal
```

---

## Technology stack (what runs where)

**Frontend**
- React + TypeScript + Vite
- Deployed as static assets via CDN (Vercel)
- Talks to backend via JSON over HTTPS

**Backend**
- FastAPI (Python)
- Runs as a web service (Render)
- Implements analytical endpoints (frequencies, stats, subset summaries)

**Database**
- SQLite file database used as an analytics store
- Materialized from `cell-count.csv` via a loader script
- Schema is portable to Postgres/DuckDB when scaling

---

## Data & storage design

See `docs/02-DATABASE-SCHEMA.md` for the full schema and rationale.

---

## Dashboard design

The dashboard is interactive, but intentionally constrained:
- Filters map to concrete cohort definitions (condition, treatment, sample type, etc.)
- Tables are shown alongside plots for numerical transparency
- The UI focuses on presentation; computed values come from the API

This makes it easy for a reviewer to understand what is being shown and how the numbers were produced.
