import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
from pathlib import Path

app = FastAPI(title="Cell Counts Dashboard API", version="1.0.0")
DB_PATH = str(Path(__file__).resolve().parents[1] / "data" / "app.db")

# CORS
cors_origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,  # Production allowlist (e.g., Vercel). Can be empty.
    allow_origin_regex=r"https://.*\.app\.github\.dev",  # Codespaces dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Cell Counts Dashboard API. See /api/v1/health"}

@app.get("/api/v1/health")
def health():
    return {"status": "ok"}

@app.get("/api/v1/frequency")
def frequency(limit: int = 200):
    """
    Part 2: Frequency of each cell population per sample.

    Returns rows with:
      sample, total_count, population, count, percentage
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    query = """
    WITH totals AS (
        SELECT
            s.id AS sample_id,
            s.sample_code AS sample,
            SUM(cc.count) AS total_count
        FROM samples s
        JOIN cell_counts cc ON cc.sample_id = s.id
        GROUP BY s.id, s.sample_code
    ),
    freqs AS (
        SELECT
            t.sample AS sample,
            t.total_count AS total_count,
            p.name AS population,
            cc.count AS count,
            ROUND(100.0 * cc.count / t.total_count, 2) AS percentage
        FROM totals t
        JOIN cell_counts cc ON cc.sample_id = t.sample_id
        JOIN populations p ON p.id = cc.population_id
    )
    SELECT *
    FROM freqs
    ORDER BY sample, population
    LIMIT ?;
    """

    rows = cur.execute(query, (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]