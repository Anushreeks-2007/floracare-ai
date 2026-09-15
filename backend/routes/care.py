from __future__ import annotations
import logging
from typing import Any, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from backend.utils.data_loader import get_flower_by_id
from backend.services.scoring import (
    compute_health_score,
    compute_compatibility_score,
    compute_sustainability_score,
    compute_watering_advice,
    compute_what_if
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/care", tags=["Plant Care & Scoring"])

class EnvironmentInput(BaseModel):
    flower_id: int
    temperature: Optional[float] = Field(None, ge=-30, le=55)
    humidity: Optional[float] = Field(None, ge=0, le=100)
    sunlight_hours: Optional[float] = Field(None, ge=0, le=24)
    soil_ph: Optional[float] = Field(None, ge=3, le=10)
    soil_type: Optional[str] = "loamy"
    watering_frequency: Optional[str] = "2 times per week"
    stress_indicators: Optional[list[str]] = []

class WhatIfRequest(BaseModel):
    flower_id: int
    base_env: dict[str, Any]
    modifications: dict[str, Any]

class SustainabilityRequest(BaseModel):
    flower_id: int
    environment: Optional[dict[str, Any]] = {}
    practices: Optional[dict[str, Any]] = {}

@router.post("/health-score")
async def get_health_score(data: EnvironmentInput):
    flower = get_flower_by_id(data.flower_id)
    if not flower:
        raise HTTPException(status_code=404, detail=f"Flower with ID {data.flower_id} not found.")

    env_dict = data.model_dump()
    stress_info = {"stress_detected": len(data.stress_indicators or []) > 0, "issues": data.stress_indicators or []}
    result = compute_health_score(flower, env_dict, stress_info)
    return result

@router.post("/compatibility")
async def get_compatibility(data: EnvironmentInput):
    flower = get_flower_by_id(data.flower_id)
    if not flower:
        raise HTTPException(status_code=404, detail=f"Flower with ID {data.flower_id} not found.")

    result = compute_compatibility_score(flower, data.model_dump())
    return result

@router.post("/action-plan")
async def get_action_plan(data: EnvironmentInput):
    """
    Generate 3-5 practical daily tasks:
    "What Should I Do Today?" based on species and conditions.
    """
    flower = get_flower_by_id(data.flower_id)
    if not flower:
        raise HTTPException(status_code=404, detail=f"Flower with ID {data.flower_id} not found.")

    env = data.model_dump()
    compat = compute_compatibility_score(flower, env)
    watering_adv = compute_watering_advice(flower, env)

    tasks = []

    # 1. Watering task
    water_rec = watering_adv.get("recommendation", "Check soil first")
    if water_rec == "Water today":
        tasks.append({
            "title": "Water your plant today",
            "category": "watering",
            "priority": "high",
            "icon": "💧",
            "action": f"Apply moderate water at soil level. {watering_adv.get('reason', '')}"
        })
    elif water_rec == "Wait":
        tasks.append({
            "title": "Skip watering today",
            "category": "watering",
            "priority": "medium",
            "icon": "⏳",
            "action": f"Soil/humidity conditions are sufficient. {watering_adv.get('reason', '')}"
        })
    else:
        tasks.append({
            "title": "Check top 2 inches of soil",
            "category": "soil",
            "priority": "medium",
            "icon": "🌱",
            "action": "Insert your finger into the soil. If top 2 inches feel dry, water moderately; otherwise wait."
        })

    # 2. Sunlight / position task
    sun_factor = compat.get("factors", {}).get("sunlight", {})
    if sun_factor.get("status") == "too_low":
        tasks.append({
            "title": "Move to a brighter location",
            "category": "sunlight",
            "priority": "high",
            "icon": "☀️",
            "action": f"{flower.get('common_name')} prefers {flower.get('sunlight', {}).get('requirement', 'more sunlight')}. Move closer to south/east facing window."
        })
    elif sun_factor.get("status") == "too_high":
        tasks.append({
            "title": "Provide soft shade / indirect light",
            "category": "sunlight",
            "priority": "medium",
            "icon": "⛅",
            "action": "Harsh midday sun can scorch petals. Filter light using a sheer curtain or move to partial shade."
        })
    else:
        tasks.append({
            "title": "Maintain current light exposure",
            "category": "sunlight",
            "priority": "low",
            "icon": "✨",
            "action": f"Current light levels match {flower.get('common_name')}'s ideal requirements."
        })

    # 3. Temperature / Humidity task
    temp_factor = compat.get("factors", {}).get("temperature", {})
    humid_factor = compat.get("factors", {}).get("humidity", {})
    if humid_factor.get("status") in ["too_low", "slight_issue"] and (data.humidity or 0) < 50:
        tasks.append({
            "title": "Increase ambient humidity",
            "category": "humidity",
            "priority": "medium",
            "icon": "💨",
            "action": "Mist around the foliage or place a pebble tray with water beneath the pot to boost humidity."
        })
    elif temp_factor.get("status") in ["too_low", "too_high"]:
        tasks.append({
            "title": "Protect from extreme temperature swings",
            "category": "temperature",
            "priority": "high",
            "icon": "🌡️",
            "action": f"Ideal range is {flower.get('temperature', {}).get('optimal_min')}–{flower.get('temperature', {}).get('optimal_max')}°C. Keep away from cold drafts or heat vents."
        })

    # 4. Leaf / Stress inspection
    if data.stress_indicators:
        tasks.append({
            "title": "Inspect affected foliage for stress",
            "category": "health",
            "priority": "high",
            "icon": "🔍",
            "action": f"Check areas showing: {', '.join(data.stress_indicators)}. Trim severely necrotic tips with sanitized shears."
        })
    else:
        tasks.append({
            "title": "Quick weekly leaf inspection",
            "category": "inspection",
            "priority": "low",
            "icon": "🌿",
            "action": "Check leaf undersides for aphids or spider mites and gently wipe away dust to enhance photosynthesis."
        })

    # 5. Nutrition / Care
    nutrition = flower.get("nutrition", {})
    tasks.append({
        "title": "Fertilization check",
        "category": "nutrition",
        "priority": "low",
        "icon": "🧪",
        "action": f"Feeding guideline: {nutrition.get('fertilize_when', 'every 2-4 weeks during active growth')}. {nutrition.get('precautions', '')}"
    })

    return {
        "flower_id": data.flower_id,
        "flower_name": flower.get("common_name"),
        "date_assessed": "Today",
        "total_tasks": len(tasks),
        "tasks": tasks[:5]
    }

@router.post("/watering-advisor")
async def get_watering_advice(data: EnvironmentInput):
    flower = get_flower_by_id(data.flower_id)
    if not flower:
        raise HTTPException(status_code=404, detail=f"Flower with ID {data.flower_id} not found.")

    return compute_watering_advice(flower, data.model_dump())

@router.post("/sustainability")
async def get_sustainability(data: SustainabilityRequest):
    flower = get_flower_by_id(data.flower_id)
    if not flower:
        raise HTTPException(status_code=404, detail=f"Flower with ID {data.flower_id} not found.")

    return compute_sustainability_score(flower, data.environment or {}, data.practices or {})

@router.post("/what-if")
async def get_what_if_simulation(data: WhatIfRequest):
    flower = get_flower_by_id(data.flower_id)
    if not flower:
        raise HTTPException(status_code=404, detail=f"Flower with ID {data.flower_id} not found.")

    return compute_what_if(flower, data.base_env, data.modifications)
