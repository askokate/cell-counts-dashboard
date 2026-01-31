import argparse
import csv
from pathlib import Path
from typing import Dict, Tuple

from .db import get_connection, init_schema

POPULATION_COLUMNS = ["b_cell", "cd8_t_cell", "cd4_t_cell", "nk_cell", "monocyte"]


def _get_or_create_project(conn, name: str) -> int:
    conn.execute("INSERT OR IGNORE INTO projects(name) VALUES (?)", (name,))
    row = conn.execute("SELECT id FROM projects WHERE name = ?", (name,)).fetchone()
    return int(row["id"])


def _get_or_create_population(conn, name: str) -> int:
    conn.execute("INSERT OR IGNORE INTO populations(name) VALUES (?)", (name,))
    row = conn.execute("SELECT id FROM populations WHERE name = ?", (name,)).fetchone()
    return int(row["id"])


def load_csv_to_db(csv_path: str, db_path: str, replace_db: bool = False) -> None:
    """
    Initialize SQLite schema and load all rows from the input CSV.

    Expected columns:
      project, subject, condition, age, sex, treatment, response,
      sample, sample_type, time_from_treatment_start,
      plus population columns: b_cell, cd8_t_cell, cd4_t_cell, nk_cell, monocyte
    """
    db_file = Path(db_path)
    if replace_db and db_file.exists():
        db_file.unlink()

    conn = get_connection(db_path)
    try:
        init_schema(conn)

        # Pre-create population dimension table
        pop_name_to_id: Dict[str, int] = {p: _get_or_create_population(conn, p) for p in POPULATION_COLUMNS}

        # Caches to reduce DB lookups
        project_cache: Dict[str, int] = {}
        subject_cache: Dict[Tuple[str, int], int] = {}
        course_cache: Dict[Tuple[int, str], int] = {}
        sample_cache: Dict[str, int] = {}

        with open(csv_path, newline="") as f:
            reader = csv.DictReader(f)

            required_cols = {
                "project", "subject", "condition", "age", "sex",
                "treatment", "response", "sample", "sample_type",
                "time_from_treatment_start", *POPULATION_COLUMNS
            }
            missing = required_cols - set(reader.fieldnames or [])
            if missing:
                raise ValueError(f"CSV is missing required columns: {sorted(missing)}")


            for r in reader:
                project_name = r["project"].strip()
                subject_code = r["subject"].strip()
                condition = r["condition"].strip()
                sex = r["sex"].strip().upper()                

                treatment = r["treatment"].strip()
                response = r["response"].strip().lower()
                if sex not in ("M", "F"):
                    raise ValueError(f"Unexpected sex value: {sex!r} (sample={sample_code})")
                if response in ("responder", "responders", "r"):
                    response = "yes"
                if response in ("non-responder", "non_responder", "nonresponder", "nr"):
                    response = "no"
                # Allow missing response (store NULL). Only enforce if non-empty.
                if response == "":
                    response = None
                elif response not in ("yes", "no"):
                    raise ValueError(f"Unexpected response value: {response!r} (sample={sample_code})")


                sample_code = r["sample"].strip()
                sample_type = r["sample_type"].strip()
                time0 = int(r["time_from_treatment_start"])

                age = None
                if str(r.get("age", "")).strip() != "":
                    age = int(float(r["age"]))

                # projects
                if project_name not in project_cache:
                    project_cache[project_name] = _get_or_create_project(conn, project_name)
                project_id = project_cache[project_name]

                # subjects (unique per project)
                subj_key = (subject_code, project_id)
                if subj_key not in subject_cache:
                    conn.execute(
                        """
                        INSERT OR IGNORE INTO subjects(subject_code, project_id, condition, age, sex)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (subject_code, project_id, condition, age, sex),
                    )
                    row = conn.execute(
                        "SELECT id FROM subjects WHERE subject_code = ? AND project_id = ?",
                        (subject_code, project_id),
                    ).fetchone()
                    subject_cache[subj_key] = int(row["id"])
                subject_id = subject_cache[subj_key]

                # treatment course (unique per subject + treatment)
                course_key = (subject_id, treatment)
                if course_key not in course_cache:
                    conn.execute(
                        """
                        INSERT OR IGNORE INTO treatment_courses(subject_id, treatment, response)
                        VALUES (?, ?, ?)
                        """,
                        (subject_id, treatment, response),
                    )
                    row = conn.execute(
                        "SELECT id FROM treatment_courses WHERE subject_id = ? AND treatment = ?",
                        (subject_id, treatment),
                    ).fetchone()
                    course_cache[course_key] = int(row["id"])
                course_id = course_cache[course_key]

                # samples
                if sample_code not in sample_cache:
                    conn.execute(
                        """
                        INSERT OR IGNORE INTO samples(sample_code, subject_id, treatment_course_id, sample_type, time_from_treatment_start)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (sample_code, subject_id, course_id, sample_type, time0),
                    )
                    row = conn.execute(
                        "SELECT id FROM samples WHERE sample_code = ?",
                        (sample_code,),
                    ).fetchone()
                    sample_cache[sample_code] = int(row["id"])
                sample_id = sample_cache[sample_code]

                # counts (long format)
                for pop in POPULATION_COLUMNS:
                    cnt = int(float(r[pop]))
                    conn.execute(
                        """
                        INSERT OR REPLACE INTO cell_counts(sample_id, population_id, count)
                        VALUES (?, ?, ?)
                        """,
                        (sample_id, pop_name_to_id[pop], cnt),
                    )

            conn.commit()

    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize schema and load cell-count CSV into SQLite.")
    parser.add_argument("--csv", required=True, help="Path to cell-count.csv")
    parser.add_argument("--db", required=True, help="Path to SQLite db file (e.g., backend/data/app.db)")
    parser.add_argument("--replace", action="store_true", help="Delete existing DB file and rebuild")
    args = parser.parse_args()

    load_csv_to_db(csv_path=args.csv, db_path=args.db, replace_db=args.replace)
    print(f"Loaded {args.csv} -> {args.db}")


if __name__ == "__main__":
    main()