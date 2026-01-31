import sqlite3
from pathlib import Path


def get_connection(db_path: str) -> sqlite3.Connection:
    """
    Open a SQLite connection with sensible defaults for analytics.
    """
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    # Performance + safety
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")

    return conn


def init_schema(conn: sqlite3.Connection) -> None:
    """
    Create database schema for cell count analytics.
    Safe to call multiple times.
    """
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_code TEXT NOT NULL,
            project_id INTEGER NOT NULL,
            condition TEXT NOT NULL,
            age INTEGER,
            sex TEXT CHECK (sex IN ('M','F')),

            UNIQUE(subject_code, project_id),
            FOREIGN KEY (project_id) REFERENCES projects(id)
        );

        CREATE TABLE IF NOT EXISTS treatment_courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER NOT NULL,
            treatment TEXT NOT NULL,
            response TEXT CHECK (response IN ('yes','no')),

            UNIQUE(subject_id, treatment),
            FOREIGN KEY (subject_id) REFERENCES subjects(id)
        );

        CREATE TABLE IF NOT EXISTS samples (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sample_code TEXT NOT NULL UNIQUE,
            subject_id INTEGER NOT NULL,
            treatment_course_id INTEGER NOT NULL,
            sample_type TEXT NOT NULL,
            time_from_treatment_start INTEGER NOT NULL,

            FOREIGN KEY (subject_id) REFERENCES subjects(id),
            FOREIGN KEY (treatment_course_id) REFERENCES treatment_courses(id)
        );

        CREATE TABLE IF NOT EXISTS populations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS cell_counts (
            sample_id INTEGER NOT NULL,
            population_id INTEGER NOT NULL,
            count INTEGER NOT NULL CHECK (count >= 0),

            PRIMARY KEY (sample_id, population_id),
            FOREIGN KEY (sample_id) REFERENCES samples(id) ON DELETE CASCADE,
            FOREIGN KEY (population_id) REFERENCES populations(id)
        );

        CREATE INDEX IF NOT EXISTS idx_subjects_condition ON subjects(condition);
        CREATE INDEX IF NOT EXISTS idx_subjects_sex ON subjects(sex);
        CREATE INDEX IF NOT EXISTS idx_courses_treatment ON treatment_courses(treatment);
        CREATE INDEX IF NOT EXISTS idx_courses_response ON treatment_courses(response);
        CREATE INDEX IF NOT EXISTS idx_samples_type_time ON samples(sample_type, time_from_treatment_start);
        """
    )
    conn.commit()