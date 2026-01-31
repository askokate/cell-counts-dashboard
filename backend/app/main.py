import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Cell Counts Dashboard API", version="1.0.0")

# CORS_ORIGINS will be set on Render to your Vercel URL(s)
# For local dev it defaults to Vite localhost.
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

# --- CORS (Codespaces-friendly) ---
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://.*\.app\.github\.dev",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/v1/health")
def health():
    return {"status": "ok"}