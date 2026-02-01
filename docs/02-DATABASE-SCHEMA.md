# Database Schema & Scaling Rationale

## Overview

This project uses a **normalized relational database** to store immune cell-count data, clinical metadata, and derived analytical results.

The schema is designed to:
- Accurately model clinical trial concepts
- Support analytical queries efficiently
- Scale to large numbers of projects, subjects, and samples
- Remain portable across database engines

SQLite is used for simplicity and reproducibility, but the schema is intentionally database-agnostic.

---

## Conceptual Model

The schema reflects the natural hierarchy of clinical data:

```
projects → subjects → treatment_courses → samples → cell_counts ← populations
```

Each table represents a real-world entity and avoids duplicated or denormalized data.

---

## Tables and Rationale

### `projects`
Represents independent studies or cohorts.

| Column | Type | Description |
|------|------|------------|
| id | INTEGER (PK) | Surrogate primary key |
| name | TEXT | Project identifier (e.g., prj1) |

**Why this exists**  
Separating projects allows the same subject identifiers to appear in multiple studies without collision.

---

### `subjects`
One row per biological subject within a project.

| Column | Type | Description |
|------|------|------------|
| id | INTEGER (PK) |
| subject_code | TEXT | Subject identifier from source data |
| project_id | INTEGER (FK) | References `projects.id` |
| condition | TEXT | Disease/condition (e.g., melanoma) |
| age | INTEGER | Nullable |
| sex | TEXT | M / F |

**Design choice**  
Subjects are scoped to projects, reflecting how clinical studies are conducted and avoiding global assumptions about subject identity.

---

### `treatment_courses`
Captures treatment assignment and response per subject.

| Column | Type | Description |
|------|------|------------|
| id | INTEGER (PK) |
| subject_id | INTEGER (FK) | References `subjects.id` |
| treatment | TEXT | Treatment name |
| response | TEXT | yes / no / NULL |

**Design choice**  
Response is associated with the treatment course, not the sample, since response is a clinical outcome rather than a measurement.

---

### `samples`
Represents individual biological samples collected over time.

| Column | Type | Description |
|------|------|------------|
| id | INTEGER (PK) |
| sample_code | TEXT | Unique sample identifier |
| subject_id | INTEGER (FK) | References `subjects.id` |
| treatment_course_id | INTEGER (FK) | References `treatment_courses.id` |
| sample_type | TEXT | PBMC / WB |
| time_from_treatment_start | INTEGER | Baseline = 0 |

**Why this matters**  
Separating samples enables longitudinal analysis and multiple sample types per subject.

---

### `populations`
Dimension table for immune cell populations.

| Column | Type | Description |
|------|------|------------|
| id | INTEGER (PK) |
| name | TEXT | Cell population name |

**Design choice**  
Populations are rows, not columns. This avoids schema changes when new populations are introduced.

---

### `cell_counts`
Long-format fact table storing observed counts.

| Column | Type | Description |
|------|------|------------|
| sample_id | INTEGER (FK) | References `samples.id` |
| population_id | INTEGER (FK) | References `populations.id` |
| count | INTEGER | Observed cell count |

**Why long format**  
Long-format storage enables:
- Flexible aggregation
- Efficient joins
- Arbitrary population expansion
- Cleaner statistical queries

---

## Analytical Query Strategy

The schema is optimized for **read-heavy analytical workloads**.

Common patterns include:
- Per-sample frequency calculations
- Subset filtering by condition, treatment, sample type, and timepoint
- Grouped summaries across projects or responses

These are expressed using SQL CTEs for clarity and correctness.

---

## Scaling Considerations

If the dataset grows to:
- **Hundreds of projects**
- **Thousands of subjects**
- **Millions of samples**

The system scales by:

- Migrating SQLite → Postgres or DuckDB
- Adding indexes on frequently filtered columns:
  - `subjects.condition`
  - `treatment_courses.treatment`
  - `samples.sample_type`
  - `samples.time_from_treatment_start`
- Introducing materialized views for heavy analytics

No schema redesign is required.

---

## Why This Schema Works

This schema:
- Matches real clinical data relationships
- Avoids denormalization and duplication
- Supports complex analytics without schema changes
- Remains easy to reason about and audit

It is intentionally designed to be **simple, explicit, and scalable**.