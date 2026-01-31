#!/usr/bin/env bash
set -e

# Render sets PORT. Locally default to 8000.
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}