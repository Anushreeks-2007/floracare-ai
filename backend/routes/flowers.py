from __future__ import annotations
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from backend.utils.data_loader import get_flower_db, get_flower_by_id, get_all_flowers, get_flower_by_name
from backend.services.scoring import compute_compatibility_score

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/flowers", tags=["Flowers Catalog & Recommender"])

class RecommenderRequest(BaseModel):
    temperature: float = 22.0
    humidity: float = 60.0
    sunlight_hours: float = 6.0
    soil_type: str = "loamy"
    soil_ph: float = 6.5
    watering_frequency: str = "2 times per week"
    climate: Optional[str] = "temperate"
    skill_level: Optional[str] = "beginner"

@router.get("")
async def list_flowers(
    q: Optional[str] = Query(None, description="Search term (name, label, scientific)"),
    climate: Optional[str] = Query(None, description="Filter by climate zone"),
    difficulty: Optional[str] = Query(None, description="Filter by care difficulty (easy, moderate, hard)")
):
    """List all flower entries with optional search and filters."""
    flowers = get_flower_db()

    if q:
        q_lower = q.lower()
        flowers = [
            f for f in flowers
            if q_lower in f.get("common_name", "").lower()
            or q_lower in f.get("oxford_label", "").lower()
            or q_lower in f.get("scientific_name", "").lower()
        ]

    if climate:
        c_lower = climate.lower()
        flowers = [f for f in flowers if f.get("climate", "").lower() == c_lower]

    if difficulty:
        d_lower = difficulty.lower()
        flowers = [f for f in flowers if f.get("care_difficulty", "").lower() == d_lower]

    return {
        "count": len(flowers),
        "results": [
            {
                "id": f["id"],
                "oxford_label": f.get("oxford_label"),
                "common_name": f.get("common_name"),
                "scientific_name": f.get("scientific_name"),
                "emoji": f.get("emoji", "🌸"),
                "climate": f.get("climate"),
                "care_difficulty": f.get("care_difficulty"),
                "sunlight": f.get("sunlight", {}).get("requirement"),
                "watering": f.get("watering", {}).get("frequency"),
                "temp_optimal": f"{f.get('temperature', {}).get('optimal_min')}–{f.get('temperature', {}).get('optimal_max')}°C"
            }
            for f in flowers
        ]
    }

@router.get("/compare")
async def compare_flowers(
    id1: int = Query(..., description="First flower ID"),
    id2: int = Query(..., description="Second flower ID")
):
    """Side-by-side comparison between any two flower species."""
    f1 = get_flower_by_id(id1)
    f2 = get_flower_by_id(id2)

    if not f1 or not f2:
        raise HTTPException(status_code=404, detail="One or both flower IDs could not be found.")

    def extract_metrics(f):
        t = f.get("temperature", {})
        h = f.get("humidity", {})
        s = f.get("sunlight", {})
        so = f.get("soil", {})
        w = f.get("watering", {})
        diff_score = 1 if f.get("care_difficulty") == "easy" else (2 if f.get("care_difficulty") == "moderate" else 3)
        return {
            "id": f.get("id"),
            "name": f.get("common_name"),
            "scientific_name": f.get("scientific_name"),
            "emoji": f.get("emoji", "🌸"),
            "climate": f.get("climate"),
            "care_difficulty": f.get("care_difficulty"),
            "difficulty_rating": diff_score,
            "temp_range": f"{t.get('optimal_min')}°C to {t.get('optimal_max')}°C",
            "temp_min": t.get("optimal_min"),
            "temp_max": t.get("optimal_max"),
            "humidity_optimal": h.get("optimal", 60),
            "humidity_range": f"{h.get('min')}% to {h.get('max')}%",
            "sunlight_req": s.get("requirement"),
            "sunlight_hours": s.get("hours_per_day_max", 6),
            "soil_type": so.get("type"),
            "soil_ph": f"{so.get('ph_min')} - {so.get('ph_max')}",
            "watering_frequency": w.get("frequency"),
            "diseases_count": len(f.get("diseases", [])),
            "pests_count": len(f.get("pests", [])),
            "eco_water_efficiency": f.get("sustainability_notes", {}).get("water_efficiency", "moderate")
        }

    m1 = extract_metrics(f1)
    m2 = extract_metrics(f2)

    return {
        "plant1": f1,
        "plant2": f2,
        "comparison": {
            "p1_summary": m1,
            "p2_summary": m2,
            "radar_data": [
                {"subject": "Temperature Tolerance", "p1": min(100, int(m1["temp_max"] * 2.5)), "p2": min(100, int(m2["temp_max"] * 2.5))},
                {"subject": "Humidity Need", "p1": m1["humidity_optimal"], "p2": m2["humidity_optimal"]},
                {"subject": "Sunlight Demand", "p1": int(m1["sunlight_hours"] * 12), "p2": int(m2["sunlight_hours"] * 12)},
                {"subject": "Watering Ease", "p1": 85 if "1" in m1["watering_frequency"] else 65, "p2": 85 if "1" in m2["watering_frequency"] else 65},
                {"subject": "Low Maintenance", "p1": 90 if m1["care_difficulty"] == "easy" else (65 if m1["care_difficulty"] == "moderate" else 40),
                                      "p2": 90 if m2["care_difficulty"] == "easy" else (65 if m2["care_difficulty"] == "moderate" else 40)}
            ]
        }
    }

@router.get("/{flower_id}")
async def get_flower_detail(flower_id: int):
    flower = get_flower_by_id(flower_id)
    if not flower:
        raise HTTPException(status_code=404, detail=f"Flower with ID {flower_id} not found.")
    return flower

@router.post("/recommender")
async def recommend_flowers(req: RecommenderRequest):
    """
    "Which Flower Should I Grow?"
    Matches all 102 flower species against user environment, ranks top 5,
    and returns compatibility score + detailed plain-English explanation.
    """
    flowers = get_flower_db()
    env = req.model_dump()

    scored = []
    for f in flowers:
        comp = compute_compatibility_score(f, env)
        score = comp.get("overall_score", 0)

        # Bonus for matching skill level
        diff = f.get("care_difficulty", "moderate")
        if req.skill_level == "beginner" and diff == "easy":
            score = min(100, score + 4)
        elif req.skill_level == "expert" and diff == "hard":
            score = min(100, score + 3)

        # Generate specific explanation
        reasons = []
        t = f.get("temperature", {})
        if t.get("optimal_min", 0) <= req.temperature <= t.get("optimal_max", 40):
            reasons.append(f"Temperature ({req.temperature}°C) is directly inside its optimal {t.get('optimal_min')}–{t.get('optimal_max')}°C zone.")
        h = f.get("humidity", {})
        if h.get("min", 0) <= req.humidity <= h.get("max", 100):
            reasons.append(f"Ambient humidity ({req.humidity}%) aligns with its native range.")
        if req.soil_type and req.soil_type.lower() in f.get("soil", {}).get("type", "").lower():
            reasons.append(f"Your {req.soil_type} soil is the preferred substrate for this species.")

        if not reasons:
            reasons.append("Adaptable species with good environmental resilience.")

        scored.append({
            "id": f["id"],
            "name": f.get("common_name"),
            "scientific_name": f.get("scientific_name"),
            "emoji": f.get("emoji", "🌸"),
            "match_score": score,
            "care_difficulty": f.get("care_difficulty"),
            "climate": f.get("climate"),
            "sunlight_req": f.get("sunlight", {}).get("requirement"),
            "soil_type": f.get("soil", {}).get("type"),
            "watering_frequency": f.get("watering", {}).get("frequency"),
            "reasons": reasons,
            "explanation": " ".join(reasons)
        })

    # Sort descending by match score
    scored.sort(key=lambda x: x["match_score"], reverse=True)

    return {
        "user_environment": env,
        "total_evaluated": len(scored),
        "top_recommendations": scored[:6]
    }
