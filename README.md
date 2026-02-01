# Cell Counts Dashboard – Submission Package

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

### Backend

```bash
cd backend
eval "$(micromamba shell hook --shell bash)"
micromamba activate cell-counts-dashboard
make -C backend backend-dev
```

### Frontend

```bash
make -C frontend frontend-install
make -C frontend frontend-dev
```

Open port **5173** in Codespaces.

---

