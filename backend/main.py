from __future__ import annotations
import os
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

#from backend.routes.predict import router as predict_router
from backend.routes.care import router as care_router
from backend.routes.flowers import router as flowers_router
from backend.routes.analytics import router as analytics_router
from backend.routes.journal import router as journal_router
from backend.utils.data_loader import get_flower_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("floracare-backend")

app = FastAPI(
    title="FloraCare AI API",
    description="Intelligent Flower Plant Health, Care & Sustainability System",
    version="1.0.0"
)

# Enable CORS for frontend Vite development server and production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure upload directory exists and mount static files
uploads_dir = os.path.join(os.path.dirname(__file__), "storage", "uploads")
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# Include Routers
#app.include_router(predict_router)
app.include_router(care_router)
app.include_router(flowers_router)
app.include_router(analytics_router)
app.include_router(journal_router)

@app.on_event("startup")
async def startup_event():
    try:
        db = get_flower_db()
        logger.info("🌿 FloraCare AI API initialized. %d flower species loaded.", len(db))
    except Exception as e:
        logger.error("Failed to load flower database on startup: %s", e)

@app.get("/")
async def root():
    return {
        "system": "FloraCare AI",
        "description": "Intelligent Flower Plant Health, Care & Sustainability System",
        "version": "1.0.0",
        "docs_url": "/docs",
        "endpoints": [
            "/api/predict",
            "/api/care/health-score",
            "/api/care/compatibility",
            "/api/care/action-plan",
            "/api/care/watering-advisor",
            "/api/care/sustainability",
            "/api/care/what-if",
            "/api/flowers",
            "/api/flowers/compare",
            "/api/flowers/recommender",
            "/api/analytics/summary",
            "/api/analytics/mining",
            "/api/profiles",
            "/api/journal/{profile_id}/compare",
            "/api/model/status",
            "/api/model/evaluation"
        ]
    }

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled server exception at %s: %s", request.url, exc)
    return JSONResponse(
        status_code=500,
        content={"error": "internal_error", "message": "An unexpected error occurred. Please try again."}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
