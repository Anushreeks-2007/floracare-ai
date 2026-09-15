"""
FloraCare AI – Data Loader
Loads and caches flower_care_db.json, soil_db.json, climate_db.json.
"""
from __future__ import annotations

import json
import logging
import os
from functools import lru_cache
from typing import Any

logger = logging.getLogger(__name__)

# Path to data directory (two levels up from this file)
DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data",
)

FLOWER_DB_PATH  = os.path.join(DATA_DIR, "flower_care_db.json")
SOIL_DB_PATH    = os.path.join(DATA_DIR, "soil_db.json")
CLIMATE_DB_PATH = os.path.join(DATA_DIR, "climate_db.json")


def _load_json(path: str, description: str) -> Any:
    if not os.path.isfile(path):
        raise FileNotFoundError(
            f"{description} not found at '{path}'. "
            f"Please ensure the data files are present in the data/ directory."
        )
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def get_flower_db() -> list[dict]:
    """Return the complete flower care database as a list."""
    raw = _load_json(FLOWER_DB_PATH, "Flower care database")
    if not isinstance(raw, list):
        raise ValueError("flower_care_db.json should contain a JSON array.")
    logger.info("Loaded flower DB: %d entries", len(raw))
    return raw


@lru_cache(maxsize=1)
def get_soil_db() -> dict:
    """Return the soil database dict (with 'soil_types' key)."""
    raw = _load_json(SOIL_DB_PATH, "Soil database")
    return raw


@lru_cache(maxsize=1)
def get_climate_db() -> dict:
    """Return the climate database dict (with 'climate_zones' key)."""
    raw = _load_json(CLIMATE_DB_PATH, "Climate database")
    return raw


def get_flower_by_id(flower_id: int) -> dict | None:
    """
    Return the flower entry for a given 1-based Oxford class ID.
    Returns None if not found.
    """
    flowers = get_flower_db()
    for flower in flowers:
        if flower.get("id") == flower_id:
            return flower
    return None


def get_flower_by_label(label: str) -> dict | None:
    """Return flower entry matching oxford_label (case-insensitive)."""
    flowers = get_flower_db()
    label_lower = label.lower()
    for flower in flowers:
        if flower.get("oxford_label", "").lower() == label_lower:
            return flower
    return None


def get_flower_by_name(name: str) -> list[dict]:
    """Fuzzy search flowers by common_name or oxford_label (case-insensitive partial match)."""
    flowers = get_flower_db()
    name_lower = name.lower()
    return [
        f for f in flowers
        if name_lower in f.get("common_name", "").lower()
        or name_lower in f.get("oxford_label", "").lower()
        or name_lower in f.get("scientific_name", "").lower()
    ]


def get_all_flowers() -> list[dict]:
    """Return summary info for all flowers (id, names, emoji, care_difficulty)."""
    flowers = get_flower_db()
    return [
        {
            "id": f["id"],
            "oxford_label": f.get("oxford_label", ""),
            "common_name": f.get("common_name", ""),
            "scientific_name": f.get("scientific_name", ""),
            "emoji": f.get("emoji", "🌸"),
            "care_difficulty": f.get("care_difficulty", "moderate"),
            "climate": f.get("climate", ""),
            "growing_season": f.get("growing_season", ""),
        }
        for f in flowers
    ]


def get_soil_info(soil_type: str) -> dict | None:
    """Return soil info for a given soil type ID."""
    soil_db = get_soil_db()
    for soil in soil_db.get("soil_types", []):
        if soil.get("id", "").lower() == soil_type.lower():
            return soil
    return None


def get_climate_info(climate_id: str) -> dict | None:
    """Return climate zone info for a given climate ID."""
    climate_db = get_climate_db()
    for zone in climate_db.get("climate_zones", []):
        if zone.get("id", "").lower() == climate_id.lower():
            return zone
    return None


def reload_all() -> None:
    """Clear caches and reload all databases (useful after data updates)."""
    get_flower_db.cache_clear()
    get_soil_db.cache_clear()
    get_climate_db.cache_clear()
    logger.info("Data caches cleared.")
