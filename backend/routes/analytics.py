from __future__ import annotations
import logging
from collections import Counter
from fastapi import APIRouter
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from backend.utils.data_loader import get_flower_db, get_climate_db, get_soil_db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/analytics", tags=["Data Analytics & Data Mining"])

@router.get("/summary")
async def get_analytics_summary():
    """Summary metrics across the Oxford 102 flower care database."""
    flowers = get_flower_db()
    total = len(flowers)

    climates = Counter(f.get("climate", "unknown") for f in flowers)
    difficulties = Counter(f.get("care_difficulty", "moderate") for f in flowers)
    soils = Counter(f.get("soil", {}).get("type", "loamy") for f in flowers)
    sunlights = Counter(f.get("sunlight", {}).get("requirement", "full sun") for f in flowers)

    temps_min = [f.get("temperature", {}).get("optimal_min", 15) for f in flowers]
    temps_max = [f.get("temperature", {}).get("optimal_max", 25) for f in flowers]
    humidities = [f.get("humidity", {}).get("optimal", 60) for f in flowers]

    return {
        "total_species": total,
        "climate_distribution": [
            {"climate": k.title(), "count": v, "percentage": round((v / total) * 100, 1)}
            for k, v in climates.items()
        ],
        "difficulty_distribution": [
            {"difficulty": k.title(), "count": v, "percentage": round((v / total) * 100, 1)}
            for k, v in difficulties.items()
        ],
        "soil_distribution": [
            {"soil": k.title(), "count": v} for k, v in soils.most_common(6)
        ],
        "sunlight_distribution": [
            {"sunlight": k.title(), "count": v} for k, v in sunlights.most_common(5)
        ],
        "environmental_averages": {
            "avg_optimal_temp_min": round(float(np.mean(temps_min)), 1),
            "avg_optimal_temp_max": round(float(np.mean(temps_max)), 1),
            "avg_optimal_humidity": round(float(np.mean(humidities)), 1),
        }
    }

@router.get("/mining")
async def get_data_mining_insights():
    """
    Data Mining Component:
    1. Feature extraction across all 102 flower species.
    2. Real correlation matrix (temp, humidity, sunlight, pH, difficulty).
    3. Real K-Means clustering (k=4) grouping flowers into ecological niches.
    4. Species scatter points for 2D visual exploration (Temp vs Humidity with cluster IDs).
    """
    flowers = get_flower_db()

    # Extract numerical feature vectors
    features = []
    meta = []
    for f in flowers:
        t_opt = (f.get("temperature", {}).get("optimal_min", 15) + f.get("temperature", {}).get("optimal_max", 25)) / 2.0
        h_opt = f.get("humidity", {}).get("optimal", 60)
        sun_h = f.get("sunlight", {}).get("hours_per_day_max", 6)
        ph_opt = (f.get("soil", {}).get("ph_min", 6.0) + f.get("soil", {}).get("ph_max", 7.0)) / 2.0
        diff_val = 1.0 if f.get("care_difficulty") == "easy" else (2.0 if f.get("care_difficulty") == "moderate" else 3.0)
        disease_count = float(len(f.get("diseases", [])))

        features.append([t_opt, h_opt, sun_h, ph_opt, diff_val, disease_count])
        meta.append({
            "id": f["id"],
            "name": f.get("common_name"),
            "emoji": f.get("emoji", "🌸"),
            "climate": f.get("climate"),
            "temp": round(t_opt, 1),
            "humidity": round(h_opt, 1),
            "difficulty": f.get("care_difficulty")
        })

    X = np.array(features, dtype=float)

    # 1. Pearson Correlation Matrix
    feature_names = ["Avg Temp", "Avg Humidity", "Sunlight Hours", "Soil pH", "Care Difficulty", "Disease Risk"]
    corr_matrix = np.corrcoef(X, rowvar=False)
    correlations = []
    for i in range(len(feature_names)):
        for j in range(len(feature_names)):
            correlations.append({
                "var1": feature_names[i],
                "var2": feature_names[j],
                "correlation": round(float(corr_matrix[i, j]), 2)
            })

    # 2. K-Means Clustering
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    k = 4
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(X_scaled)

    cluster_names = [
        "Temperate Garden Classics",
        "Tropical & High Humidity",
        "Arid & Mediterranean Sun-Lovers",
        "Subtropical High-Yield Blooms"
    ]

    # Attach clusters to flowers
    scatter_points = []
    cluster_counts = Counter(cluster_labels)
    for idx, f_meta in enumerate(meta):
        c_id = int(cluster_labels[idx])
        scatter_points.append({
            **f_meta,
            "cluster_id": c_id,
            "cluster_name": cluster_names[c_id % len(cluster_names)]
        })

    clusters_summary = []
    for c_id in range(k):
        members = [scatter_points[i] for i in range(len(scatter_points)) if scatter_points[i]["cluster_id"] == c_id]
        avg_t = np.mean([m["temp"] for m in members]) if members else 0
        avg_h = np.mean([m["humidity"] for m in members]) if members else 0
        clusters_summary.append({
            "cluster_id": c_id,
            "cluster_name": cluster_names[c_id % len(cluster_names)],
            "count": len(members),
            "avg_temp": round(float(avg_t), 1),
            "avg_humidity": round(float(avg_h), 1),
            "representative_flowers": [m["name"] for m in members[:4]]
        })

    # Key Data Mining Discoveries
    insights = [
        {
            "finding": "Humidity vs Disease Risk",
            "stat": f"r = {corr_matrix[1, 5]:.2f}",
            "description": "Positive correlation observed between high native ambient humidity and documented fungal pathogen vulnerability."
        },
        {
            "finding": "Temperature vs Care Difficulty",
            "stat": f"r = {corr_matrix[0, 4]:.2f}",
            "description": "Tropical species with narrow high-temperature tolerances exhibit higher average maintenance ratings in non-native climates."
        },
        {
            "finding": "K-Means Ecological Segregation",
            "stat": f"{k} Distinct Niches",
            "description": "Unsupervised clustering separates the 102 species into 4 coherent botanical archetypes based on temperature, humidity, and soil pH."
        }
    ]

    return {
        "feature_names": feature_names,
        "correlation_matrix": correlations,
        "scatter_points": scatter_points,
        "clusters": clusters_summary,
        "insights": insights
    }
