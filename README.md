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

The instructions below assume a **fresh GitHub Codespace**.

You will run the **backend and frontend in two separate terminals**.

---

## Backend Setup (Python / FastAPI)

### 1) Ensure micromamba is available

GitHub Codespaces typically includes `micromamba` by default.

Verify:

```bash
micromamba --version
```

If not available, install it:

```bash
curl -Ls https://micro.mamba.pm/install.sh | bash
```
Then reload the shell.

---

### 2) Create and activate the Python environment

From the repo root:

```bash
cd backend
micromamba env create -n cell-counts-dashboard -f environment.yml || true
micromamba activate cell-counts-dashboard
```

---

### 3) Install backend dependencies

```bash
pip install -U pip
pip install -r requirements.txt
```

---

### 4) (Optional) Rebuild the SQLite database from CSV

The repository includes a prebuilt database at `backend/data/app.db`.

To regenerate it from `data/cell-count.csv`:

```bash
python -m app.load_db   --csv ../data/cell-count.csv   --db data/app.db   --replace
```

---

### 5) Start the backend API

```bash
./start.sh
```

Verify:

```bash
curl http://localhost:8000/api/v1/health
```

Forward **port 8000** if you want to access the API from the browser.

---

## Frontend Setup (React / Vite)

Open a **second Codespaces terminal**.

### 6) Install frontend dependencies

From the repo root:

```bash
cd frontend
npm install
```

---

### 7) Start the frontend dashboard

```bash
npm run dev -- --host 0.0.0.0 --port 5173
```

Open/forward **port 5173** to view the dashboard.

---

## Running Tests (Optional)

From the repo root:

```bash
cd backend
micromamba activate cell-counts-dashboard
pytest -v
```

---

## Summary

This submission demonstrates:

- Clean separation of data, analytics, and presentation layers
- Relational modeling suitable for clinical datasets
- Reproducible, auditable analytical workflows
- A production-style interactive dashboard backed by tested APIs

The system prioritizes **clarity, correctness, and reviewability** over unnecessary abstraction.