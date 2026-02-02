# System Design Narrative

## Overview

This project is an end-to-end analytical system designed to transform raw immune cell-count data into **auditable statistical insights** and present them through a clear, reviewer-friendly dashboard.

The system prioritizes reproducibility, analytical transparency, and deterministic outputs.

---

## Architecture

```
Raw CSV → Relational DB → Analytics API → Interactive Dashboard
```

---

## Data Layer

A normalized relational schema models projects, subjects, treatments, samples, and cell populations.  
The database is materialized once and treated as read-only during analysis.

---

## Analytics Layer

The backend is a stateless FastAPI service.  
All analytics are SQL-first and executed in the backend to ensure correctness and auditability.

---

## Presentation Layer

The React dashboard maps directly to analytical tasks.  
Tables precede plots, and interactivity is intentionally constrained to avoid ambiguous analysis states.

---

## Summary

The architecture favors clarity and correctness over unnecessary abstraction, while remaining scalable and easy to extend.