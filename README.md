# Cell Counts Dashboard

This repository contains a complete, reproducible **end-to-end analytics application** that ingests immune cell-count data, stores it in a relational database, exposes analytical APIs, and presents results in an interactive web dashboard.

The project is designed to be run and reviewed using **GitHub Codespaces**.

---

## Contents of the Submission

This repository includes:

- **Python backend** (FastAPI) with all accompanying source files
- **Relational SQLite database** (materialized from input CSV)
- **Input data** (`cell-count.csv`)
- **Frontend dashboard** (React + TypeScript)
- **Automated tests** for backend logic
- **Documentation** explaining architecture, schema, and design decisions

---

## Live Links

- **Interactive dashboard**: https://cell-counts-dashboard.vercel.app  
- **Live API (health check)**: https://cell-counts-dashboard.onrender.com/api/v1/health

> Note: Free-tier hosting may cause brief cold-start delays.

---

## Repository Structure

```
cell-counts-dashboard/
├── backend/
├── frontend/
├── data/
├── docs/
├── Makefile
├── requirements.txt
└── README.md
```

---

## How to Run the Project (GitHub Codespaces)

This repo is designed to run in a fresh Codespace using the provided `Makefile` targets.

> You’ll run the backend and frontend in two separate terminals.

### 0) Quick reference (Make targets)

From the repo root:

```bash
make help
```

### 1) Backend setup (Python env + dependencies)

In **Terminal 1** (repo root):

```bash
make env-create
```

This creates (or reuses) the `cell-counts-dashboard` micromamba environment and installs backend Python dependencies from `requirements.txt`.

### 2) (Optional) Rebuild the SQLite database from the CSV

The repo includes a materialized DB at `backend/data/app.db`.
If you want to regenerate it from `data/cell-count.csv`:

```bash
make load-db
```

### 3) Start the backend API (FastAPI)

In **Terminal 1**:

```bash
make backend-dev
```

Verify:

```bash
curl -s http://localhost:8000/api/v1/health
```

Open/forward **port 8000** if you want to hit the API from the browser.

### 4) Start the frontend dashboard (Vite + React)

In **Terminal 2** (repo root):

```bash
make frontend-install
make frontend-dev
```

Open/forward **port 5173** to view the dashboard.

### 5) Run tests (optional)

```bash
make test
```

---

## Summary

This submission demonstrates:

- Clean separation of data, analytics, and presentation layers
- Relational modeling suitable for clinical datasets
- Reproducible, auditable analytical workflows
- A production-style interactive dashboard backed by tested APIs

The system prioritizes **clarity, correctness, and reviewability** over unnecessary abstraction.