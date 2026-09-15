from __future__ import annotations
import logging
import os
import json
import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, status
from pydantic import BaseModel
from PIL import Image
import numpy as np

from backend.utils.data_loader import get_flower_by_id

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["Profiles & Growth Journal"])

PROFILES_FILE = "backend/storage/profiles.json"
UPLOADS_DIR = "backend/storage/uploads"

def _load_profiles() -> list[dict]:
    if not os.path.exists(PROFILES_FILE):
        return []
    try:
        with open(PROFILES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def _save_profiles(profiles: list[dict]) -> None:
    os.makedirs(os.path.dirname(PROFILES_FILE), exist_ok=True)
    with open(PROFILES_FILE, "w", encoding="utf-8") as f:
        json.dump(profiles, f, indent=2)

class ProfileCreate(BaseModel):
    flower_id: int
    nickname: Optional[str] = None
    location: Optional[str] = "Living Room Window"
    notes: Optional[str] = None
    watering_day: Optional[str] = "Wednesday"

@router.get("/profiles")
async def get_all_profiles():
    return _load_profiles()

@router.post("/profiles")
async def create_profile(data: ProfileCreate):
    flower = get_flower_by_id(data.flower_id)
    if not flower:
        raise HTTPException(status_code=404, detail="Flower not found.")

    profiles = _load_profiles()
    profile_id = str(uuid.uuid4())[:8]

    new_profile = {
        "id": profile_id,
        "flower_id": data.flower_id,
        "flower_name": flower.get("common_name"),
        "scientific_name": flower.get("scientific_name"),
        "emoji": flower.get("emoji", "🌸"),
        "nickname": data.nickname or flower.get("common_name"),
        "location": data.location,
        "notes": data.notes or "Healthy seedling/plant",
        "watering_day": data.watering_day,
        "care_difficulty": flower.get("care_difficulty"),
        "climate": flower.get("climate"),
        "sunlight": flower.get("sunlight", {}).get("requirement"),
        "watering_freq": flower.get("watering", {}).get("frequency"),
        "created_at": datetime.utcnow().strftime("%Y-%m-%d"),
        "journal_entries": []
    }

    profiles.append(new_profile)
    _save_profiles(profiles)
    return new_profile

@router.delete("/profiles/{profile_id}")
async def delete_profile(profile_id: str):
    profiles = _load_profiles()
    filtered = [p for p in profiles if p["id"] != profile_id]
    if len(filtered) == len(profiles):
        raise HTTPException(status_code=404, detail="Profile not found.")
    _save_profiles(filtered)
    return {"success": True, "message": "Profile deleted."}

@router.post("/journal/{profile_id}/entry")
async def add_journal_entry(
    profile_id: str,
    notes: str = Form(""),
    day_label: str = Form("New Observation"),
    file: Optional[UploadFile] = File(None)
):
    profiles = _load_profiles()
    profile = next((p for p in profiles if p["id"] == profile_id), None)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found.")

    img_filename = None
    cv_metrics = {"greenness_index": 0.5, "coverage_pct": 50, "vitality": "healthy"}

    if file:
        os.makedirs(UPLOADS_DIR, exist_ok=True)
        img_id = f"{profile_id}_{uuid.uuid4().hex[:6]}_{file.filename}"
        img_path = os.path.join(UPLOADS_DIR, img_id)
        content = await file.read()
        with open(img_path, "wb") as out:
            out.write(content)
        img_filename = f"/uploads/{img_id}"

        # Run real CV analysis on journal image
        try:
            pil_img = Image.open(img_path).convert("RGB").resize((128, 128))
            arr = np.array(pil_img, dtype=float) / 255.0
            r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
            # Excess Green Index (2G - R - B)
            exg = 2.0 * g - r - b
            green_pixels = np.count_nonzero(exg > 0.05)
            coverage = round((green_pixels / (128 * 128)) * 100, 1)
            mean_green = round(float(np.mean(g[exg > 0.05])) if green_pixels > 0 else 0.4, 2)
            cv_metrics = {
                "greenness_index": mean_green,
                "coverage_pct": coverage,
                "vitality": "thriving" if coverage > 30 and mean_green > 0.45 else "moderate"
            }
        except Exception as e:
            logger.warning(f"Failed to compute CV metrics: {e}")

    entry = {
        "id": str(uuid.uuid4())[:6],
        "date": datetime.utcnow().strftime("%Y-%m-%d"),
        "day_label": day_label,
        "notes": notes,
        "image_url": img_filename,
        "cv_metrics": cv_metrics
    }

    profile.setdefault("journal_entries", []).append(entry)
    _save_profiles(profiles)
    return {"success": True, "entry": entry}

@router.get("/journal/{profile_id}/compare")
async def compare_journal_entries(profile_id: str):
    """
    Compare chronological journal photos using Computer Vision metrics:
    Tracks vegetation coverage changes, green vitality index, and health progression.
    """
    profiles = _load_profiles()
    profile = next((p for p in profiles if p["id"] == profile_id), None)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found.")

    entries = profile.get("journal_entries", [])
    if len(entries) < 2:
        return {
            "has_comparison": False,
            "message": "At least two journal entries with photos are needed to analyze growth progression.",
            "entries_count": len(entries)
        }

    first = entries[0]
    latest = entries[-1]

    cov_start = first.get("cv_metrics", {}).get("coverage_pct", 40)
    cov_end = latest.get("cv_metrics", {}).get("coverage_pct", 50)
    cov_diff = round(cov_end - cov_start, 1)

    green_start = first.get("cv_metrics", {}).get("greenness_index", 0.5)
    green_end = latest.get("cv_metrics", {}).get("greenness_index", 0.5)
    green_diff = round(green_end - green_start, 2)

    status_trend = (
        "Significant positive growth and canopy expansion observed."
        if cov_diff > 5
        else (
            "Slight reduction in foliage density detected — check watering and light exposure."
            if cov_diff < -5
            else "Stable plant density with consistent foliage pigmentation."
        )
    )

    return {
        "has_comparison": True,
        "plant_name": profile.get("nickname"),
        "start_date": first.get("date"),
        "latest_date": latest.get("date"),
        "foliage_growth_change": f"{cov_diff:+}%",
        "chlorophyll_vitality_change": f"{green_diff:+}",
        "trend_summary": status_trend,
        "first_entry": first,
        "latest_entry": latest,
        "timeline": entries
    }
