"""
Optional: Run as FastAPI server instead of Streamlit.
Run: python scripts/run_api.py
Then: curl -X POST http://localhost:8000/recommend -H "Content-Type: application/json" -d '{...}'
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.config import API_HOST, API_PORT
from backend.schemas import ProfileRequest, RecommendationResponse
from backend.recommend import RecommendationPipeline

app = FastAPI(
    title="Career Recommender API",
    description="Intelligent career recommendation system with 50+ careers",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = RecommendationPipeline()


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "message": "Career Recommender API is running"}


@app.post("/recommend", response_model=RecommendationResponse)
async def recommend(profile: ProfileRequest):
    """Generate career recommendations based on user profile."""
    try:
        response = pipeline.recommend(profile, use_llm=True)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/careers")
async def list_careers():
    """List all available careers with categories."""
    from backend.config import CAREERS_FILE
    import json
    
    with open(CAREERS_FILE, "r") as f:
        careers = json.load(f)
    
    # Group by category
    by_category = {}
    for career in careers:
        cat = career.get("category", "Other")
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append({
            "id": career["career_id"],
            "title": career["title"],
            "difficulty": career.get("difficulty", 2),
            "trend": career.get("trend", "")
        })
    
    return {
        "total_careers": len(careers),
        "categories": by_category,
        "careers": [{"id": c["career_id"], "title": c["title"], "category": c.get("category")} for c in careers]
    }


@app.get("/career/{career_id}")
async def get_career(career_id: str):
    """Get details about a specific career."""
    from backend.config import CAREERS_FILE
    import json
    
    with open(CAREERS_FILE, "r") as f:
        careers = json.load(f)
    
    for career in careers:
        if career["career_id"] == career_id:
            return career
    
    raise HTTPException(status_code=404, detail=f"Career {career_id} not found")


@app.get("/stats")
async def get_stats():
    """Get system statistics."""
    from backend.config import CAREERS_FILE
    import json
    
    with open(CAREERS_FILE, "r") as f:
        careers = json.load(f)
    
    categories = set(c.get("category", "Other") for c in careers)
    
    return {
        "total_careers": len(careers),
        "total_categories": len(categories),
        "categories": list(categories),
        "trends": [c.get("trend", "") for c in careers if c.get("trend")]
    }


if __name__ == "__main__":
    import uvicorn
    print(f"\n🚀 Starting Career Recommender API at http://{API_HOST}:{API_PORT}")
    print(f"📚 OpenAPI docs available at http://{API_HOST}:{API_PORT}/docs")
    print(f"📊 ReDoc available at http://{API_HOST}:{API_PORT}/redoc\n")
    uvicorn.run(app, host=API_HOST, port=API_PORT)
