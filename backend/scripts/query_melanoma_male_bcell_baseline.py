"""
Question:
Considering Melanoma males, what is the average number of B cells
for responders at time=0?

Answer should be reported with two decimals (XXX.XX).

This script reproduces the calculation from the SQLite analytics DB.
NOTE: this does filter to keep only PBMC samples.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "app.db"


def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    sql = """
    WITH eligible_samples AS (
      SELECT s.id AS sample_id
      FROM samples s
      JOIN subjects subj        ON subj.id = s.subject_id
      JOIN treatment_courses tc ON tc.id = s.treatment_course_id
      WHERE
        subj.condition = 'melanoma'
        AND subj.sex = 'M'
        AND s.time_from_treatment_start = 0
        AND tc.response = 'yes'
    ),
    b_cell AS (
      SELECT id AS population_id
      FROM populations
      WHERE name = 'b_cell'
    )
    SELECT
      COUNT(*) AS n_samples,
      ROUND(AVG(cc.count), 2) AS avg_b_cells
    FROM eligible_samples es
    JOIN b_cell b
    JOIN cell_counts cc
      ON cc.sample_id = es.sample_id
    AND cc.population_id = b.population_id;
    """

    n_samples, avg_b = cur.execute(sql).fetchone()
    conn.close()

    print(f"n_samples = {n_samples}")
    print(f"avg_b_cells = {avg_b:.2f}")


if __name__ == "__main__":
    main()