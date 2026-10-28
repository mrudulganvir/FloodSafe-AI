"""
FloodSafe AI — Backend Entry Point
===================================
This file creates the FastAPI application and wires everything together.

How to run:
    uvicorn app.main:app --reload --port 8000

'app.main' tells uvicorn: look inside the 'app' package, open 'main.py',
and use the variable named 'app' as the FastAPI application object.
'--reload' means: restart automatically when you save a file (great for development).
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create the FastAPI application instance.
# The 'title' and 'description' appear in the auto-generated API docs at /docs
app = FastAPI(
    title="FloodSafe AI",
    description=(
        "AI-Based Flood Evacuation Route Planning System. "
        "This is an educational simulation — not a real emergency navigation tool."
    ),
    version="1.0.0",
)

# --------------------------------------------------------------------------
# CORS (Cross-Origin Resource Sharing) configuration
# --------------------------------------------------------------------------
# When your React frontend (localhost:5173) sends a request to the backend
# (localhost:8000), the browser checks whether the backend allows it.
# Without CORSMiddleware the browser will block the request with a CORS error.
# In production you would restrict 'allow_origins' to your actual domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------------------------------
# Health-check endpoint
# --------------------------------------------------------------------------
# This is a simple "is the server alive?" endpoint.
# The @app.get decorator registers this function as the handler for GET /api/health
@app.get("/api/health", tags=["System"])
def health_check():
    """Returns a simple status message to confirm the server is running."""
    return {"status": "ok", "version": "1.0.0"}


# --------------------------------------------------------------------------
# Root redirect message (helpful for first-time visitors to localhost:8000)
# --------------------------------------------------------------------------
@app.get("/", tags=["System"])
def root():
    """Redirects visitors to the API documentation."""
    return {
        "message": "FloodSafe AI backend is running.",
        "docs": "Visit /docs for the interactive API documentation.",
    }


# --------------------------------------------------------------------------
# Routers registered for Milestone 4
# --------------------------------------------------------------------------
from app.api import scenarios, routes

app.include_router(scenarios.router, prefix="/api")
app.include_router(routes.router, prefix="/api")
