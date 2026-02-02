# Database Schema (Relational Model)

## Model Representation

The database models a simple clinical/experimental hierarchy:

- A **project** contains many **subjects**
- A **subject** can have one or more **treatment courses**
- A **treatment course** can produce one or more **samples**
- Each **sample** has measured **cell counts** for many **cell populations**

### Relational logic

```
projects → subjects → treatment_courses → samples → cell_counts ← populations
```

**Meaning of the arrows:** “one-to-many” in the direction of the arrow.

- `projects → subjects` means **one project has many subjects** (and each subject belongs to one project)
- `subjects → treatment_courses` means **one subject can have many treatment courses**
- `treatment_courses → samples` means **one treatment course can have many samples**
- `samples → cell_counts` means **one sample has many cell-count rows** (one per population)
- `populations → cell_counts` (written as `cell_counts ← populations`) means **one population appears in many cell-count rows**

A more explicit way to say the same thing:

- `cell_counts` is the “fact table” that links **(sample, population) → count**.

---

## ER diagram (ASCII)

```
+-----------+      +-----------+      +------------------+      +---------+
| projects  | 1  ─<| subjects  | 1  ─<| treatment_courses| 1  ─<| samples |
+-----------+      +-----------+      +------------------+      +---------+
| PK id     |      | PK id     |      | PK id            |      | PK id   |
| name      |      | subject_code|     | FK subject_id    |      | sample_code
+-----------+      | FK project_id|    | treatment        |      | FK subject_id
                   | condition  |      | response         |      | FK treatment_course_id
                   | age, sex   |      +------------------+      | sample_type
                   +-----------+                                | time_from_treatment_start
                                                                +---------+
                                                                     1
                                                                     |
                                                                     | has many
                                                                     v
                                                            +----------------+
                                                            |   cell_counts  |
                                                            +----------------+
                                                            | FK sample_id   |───> samples.PK id
                                                            | FK population_id|──> populations.PK id
                                                            | count          |
                                                            +----------------+
                                                                     ^
                                                                     |
                                                            +----------------+
                                                            |  populations   |
                                                            +----------------+
                                                            | PK id          |
                                                            | name           |
                                                            +----------------+
```

---

## Tables, keys, and intent

### `projects`
Represents an independent study or cohort.

**Primary Key (PK):**
- `projects.id`

**Columns:**
- `id` (PK) – surrogate key
- `name` – project identifier (e.g., `prj1`)

**Rationale** : 
Projects are a natural top-level unit for analysis and allow future expansion to hundreds of studies without changing downstream tables.

---

### `subjects`
One row per biological subject **within a project**.

**Primary Key (PK):**
- `subjects.id`

**Foreign Keys (FK):**
- `subjects.project_id` → `projects.id`

**Columns:**
- `id` (PK)
- `subject_code` – subject identifier from source data
- `project_id` (FK)
- `condition` – disease/condition (e.g., melanoma)
- `age` (nullable)
- `sex`

**Rationale** : 
Scoping subjects to projects mirrors how studies work in practice and avoids assuming subject IDs are globally unique across studies.

---

### `treatment_courses`
Captures treatment assignment and response per subject.

**Primary Key (PK):**
- `treatment_courses.id`

**Foreign Keys (FK):**
- `treatment_courses.subject_id` → `subjects.id`

**Columns:**
- `id` (PK)
- `subject_id` (FK)
- `treatment`
- `response` (e.g., yes/no/NULL)

**Rationale** : 
Clinical response is an outcome associated with a treatment course, while samples are measurement timepoints collected during (or after) that course.

---

### `samples`
Represents individual biological samples collected over time.

**Primary Key (PK):**
- `samples.id`

**Foreign Keys (FK):**
- `samples.subject_id` → `subjects.id`
- `samples.treatment_course_id` → `treatment_courses.id`

**Columns:**
- `id` (PK)
- `sample_code`
- `subject_id` (FK)
- `treatment_course_id` (FK)
- `sample_type` (PBMC/WB)
- `time_from_treatment_start` (baseline = 0)

**Rationale** : 
It supports longitudinal analysis (multiple timepoints) and multiple sample types per subject without duplicating metadata.

---

### `populations`
Reference list of immune cell population names.

**Primary Key (PK):**
- `populations.id`

**Columns:**
- `id` (PK)
- `name` – population name

**Rationale** : 
This is a **dimension table**, as in a lookup/reference table that stores descriptive values (like population names) once, and other tables refer to it by ID.  
Here, that means you can add new populations without changing the schema (no new columns needed).

---

### `cell_counts`
Stores observed counts in long format: one row per (sample, population).

**Primary Key (PK):**
- (Recommended composite PK) `cell_counts(sample_id, population_id)`
  - This ensures each sample has at most one count per population.

**Foreign Keys (FK):**
- `cell_counts.sample_id` → `samples.id`
- `cell_counts.population_id` → `populations.id`

**Columns:**
- `sample_id` (FK)
- `population_id` (FK)
- `count`

**Rationale** : 
Long format keeps the schema stable as populations grow from dozens to hundreds. It also makes aggregation and filtering consistent in SQL.

---

## Supported Query Patterns

This schema is optimized for read-heavy analytics such as:

- per-sample frequency calculations (population count / total counts)
- filtering by condition, treatment, sample type, and timepoint
- responder vs non-responder comparisons
- subset summaries (counts by project/response/sex)

These queries stay straightforward because joins follow real-world relationships and there is minimal duplicated data.

---

## Scaling notes

If this expands to hundreds of projects and thousands of subjects:

- SQLite can be swapped for Postgres or DuckDB without schema changes
- indexes can be added on common filters (e.g., `subjects.condition`, `samples.sample_type`, `treatment_courses.treatment`)
- heavy computations can be cached as materialized views

---

## Other Considerations for design

- **Easy to reason about:** tables correspond to real concepts (project/subject/sample), so queries read like the domain problem you’re solving.
- **Easy to audit:** analytical results can be traced back through foreign keys to the exact subject/sample/population rows used, making it clear *which records contributed to a result* and making debugging or reviewer verification straightforward.
