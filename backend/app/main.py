import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Cell Counts Dashboard API", version="1.0.0")

# CORS
cors_origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()]

if cors_origins:
    # Production (Render): explicit allowlist from env var
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    # Dev (Codespaces): allow Codespaces forwarded origins
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=r"https://.*\.app\.github\.dev",
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