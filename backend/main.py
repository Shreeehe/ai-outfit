# main.py - FastAPI Application Entry Point
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

# Import routers
from routers import clothes, classify, outfits, weather, stats

# Create FastAPI app
app = FastAPI(
    title="AI Outfit API",
    description="Backend API for AI Outfit - Intelligent Wardrobe Management",
    version="1.0.0"
)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve wardrobe images statically
IMAGES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "wardrobe_images")
os.makedirs(IMAGES_DIR, exist_ok=True)
app.mount("/images", StaticFiles(directory=IMAGES_DIR), name="images")

# Register routers
app.include_router(clothes.router)
app.include_router(classify.router)
app.include_router(outfits.router)
app.include_router(weather.router)
app.include_router(stats.router)

@app.get("/")
def root():
    return {
        "message": "AI Outfit API",
        "docs": "/docs",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Run with: uvicorn main:app --reload --port 8000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
