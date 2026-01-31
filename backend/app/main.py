import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
from pathlib import Path
from collections import defaultdict
from statistics import median
from scipy.stats import mannwhitneyu

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

@app.get("/api/v1/part3/frequencies")
def part3_frequencies():
    """
    Part 3:
    Relative frequencies (%) per sample and population for
    melanoma + miraclib + PBMC samples, split by response (yes/no).
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    query = """
    WITH filtered_samples AS (
        SELECT
            s.id AS sample_id,
            s.sample_code AS sample,
            tc.response AS response
        FROM samples s
        JOIN subjects subj ON subj.id = s.subject_id
        JOIN treatment_courses tc ON tc.id = s.treatment_course_id
        WHERE
            LOWER(subj.condition) = 'melanoma'
            AND LOWER(tc.treatment) = 'miraclib'
            AND LOWER(s.sample_type) = 'pbmc'
            AND tc.response IN ('yes', 'no')
    ),
    totals AS (
        SELECT
            fs.sample_id,
            SUM(cc.count) AS total_count
        FROM filtered_samples fs
        JOIN cell_counts cc ON cc.sample_id = fs.sample_id
        GROUP BY fs.sample_id
    ),
    freqs AS (
        SELECT
            fs.sample AS sample,
            fs.response AS response,
            p.name AS population,
            ROUND(100.0 * cc.count / t.total_count, 2) AS percentage
        FROM filtered_samples fs
        JOIN totals t ON t.sample_id = fs.sample_id
        JOIN cell_counts cc ON cc.sample_id = fs.sample_id
        JOIN populations p ON p.id = cc.population_id
    )
    SELECT *
    FROM freqs
    ORDER BY population, response;
    """

    rows = cur.execute(query).fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.get("/api/v1/part3/stats")
def part3_stats():
    """
    Part 3:
    Statistical comparison (responders vs non-responders)
    of relative frequencies (%) per immune cell population.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    query = """
    WITH filtered_samples AS (
        SELECT
            s.id AS sample_id,
            tc.response AS response
        FROM samples s
        JOIN subjects subj ON subj.id = s.subject_id
        JOIN treatment_courses tc ON tc.id = s.treatment_course_id
        WHERE
            LOWER(subj.condition) = 'melanoma'
            AND LOWER(tc.treatment) = 'miraclib'
            AND LOWER(s.sample_type) = 'pbmc'
            AND tc.response IN ('yes', 'no')
    ),
    totals AS (
        SELECT
            fs.sample_id,
            SUM(cc.count) AS total_count
        FROM filtered_samples fs
        JOIN cell_counts cc ON cc.sample_id = fs.sample_id
        GROUP BY fs.sample_id
    )
    SELECT
        fs.response AS response,
        p.name AS population,
        100.0 * cc.count / t.total_count AS percentage
    FROM filtered_samples fs
    JOIN totals t ON t.sample_id = fs.sample_id
    JOIN cell_counts cc ON cc.sample_id = fs.sample_id
    JOIN populations p ON p.id = cc.population_id;
    """

    rows = cur.execute(query).fetchall()
    conn.close()

    values = defaultdict(lambda: {"yes": [], "no": []})
    for r in rows:
        values[r["population"]][r["response"]].append(float(r["percentage"]))

    results = []
    for pop, grp in values.items():
        yes_vals = grp["yes"]
        no_vals = grp["no"]

        stat, pval = mannwhitneyu(yes_vals, no_vals, alternative="two-sided")

        results.append({
            "population": pop,
            "n_yes": len(yes_vals),
            "n_no": len(no_vals),
            "median_yes": round(median(yes_vals), 3),
            "median_no": round(median(no_vals), 3),
            "u_statistic": round(float(stat), 3),
            "p_value": float(pval),
            "significant_p_lt_0_05": bool(pval < 0.05),
            # q_value and FDR significance will be added after sorting
        })

    results.sort(key=lambda r: r["p_value"])
    # Benjamini–Hochberg FDR correction (q-values)
    m = len(results)
    prev_q = 1.0
    for i, r in enumerate(results, start=1):
        p = r["p_value"]
        q = min(prev_q, p * m / i)  # enforce monotonicity
        r["q_value"] = float(q)
        r["significant_fdr_0_05"] = bool(q < 0.05)
        prev_q = q
    return results

@app.get("/api/v1/part4/summary")
def part4_summary(
    condition: str = "melanoma",
    treatment: str = "miraclib",
    sample_type: str = "PBMC",
    time0: int = 0,
):
    """
    Part 4: Data Subset Analysis

    Cohort:
      - indication = melanoma
      - sample_type = PBMC
      - treatment = miraclib
      - time_from_treatment_start = 0 (baseline)

    Returns:
      - samples by project
      - subjects by response (yes/no; excludes NULL/empty)
      - subjects by gender (excludes NULL/empty)
    """
    import sqlite3
    from .db import get_connection

    conn = get_connection(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        sql = """
        WITH baseline AS (
            SELECT
                sam.id AS sample_id,
                sam.sample_code AS sample,
                subj.id AS subject_id,
                proj.name AS project,
                tc.response AS response,
                subj.sex AS sex
            FROM samples sam
            JOIN subjects subj ON subj.id = sam.subject_id
            JOIN projects proj ON proj.id = subj.project_id
            JOIN treatment_courses tc ON tc.id = sam.treatment_course_id
            WHERE lower(subj.condition) = lower(:condition)
              AND sam.sample_type = :sample_type
              AND sam.time_from_treatment_start = :time0
              AND lower(tc.treatment) = lower(:treatment)
        ),
        totals AS (
            SELECT
                COUNT(*) AS n_samples,
                COUNT(DISTINCT subject_id) AS n_subjects
            FROM baseline
        ),
        counts AS (
            SELECT
                'samples_by_project' AS section,
                project AS key,
                COUNT(*) AS n
            FROM baseline
            GROUP BY project

            UNION ALL

            SELECT
                'subjects_by_response' AS section,
                COALESCE(response, 'unknown') AS key,
                COUNT(DISTINCT subject_id) AS n
            FROM baseline
            GROUP BY COALESCE(response, 'unknown')

            UNION ALL

            SELECT
                'subjects_by_sex' AS section,
                COALESCE(sex, 'unknown') AS key,
                COUNT(DISTINCT subject_id) AS n
            FROM baseline
            GROUP BY COALESCE(sex, 'unknown')
        )
        SELECT
            c.section,
            c.key,
            c.n,
            t.n_samples,
            t.n_subjects
        FROM counts c
        CROSS JOIN totals t
        ORDER BY c.section, c.key;
        """

        params = {
            "condition": condition,
            "treatment": treatment,
            "sample_type": sample_type,
            "time0": time0,
        }

        rows = conn.execute(sql, params).fetchall()

        # Build structured response
        out = {
            "filter": params,
            "totals": {"n_samples": 0, "n_subjects": 0},
            "samples_by_project": [],
            "subjects_by_response": [],
            "subjects_by_sex": [],
        }

        if rows:
            out["totals"]["n_samples"] = int(rows[0]["n_samples"])
            out["totals"]["n_subjects"] = int(rows[0]["n_subjects"])

        buckets = {
            "samples_by_project": "samples_by_project",
            "subjects_by_response": "subjects_by_response",
            "subjects_by_sex": "subjects_by_sex",
        }

        for r in rows:
            section = r["section"]
            out[buckets[section]].append(
                {"key": r["key"], "n": int(r["n"])}
            )

        return out
    finally:
        conn.close()