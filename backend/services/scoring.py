"""
FloraCare AI – Scoring Engine
Computes health, compatibility, sustainability, and watering scores.

All scores are clearly labelled as AI-generated estimates.
They are NOT scientific diagnoses or medical recommendations.
"""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

# ── Helper: range scoring ───────────────────────────────────────────────────────

def _range_score(value: float | None, ideal_min: float, ideal_max: float,
                 abs_min: float | None = None, abs_max: float | None = None) -> float:
    """
    Score a value against an ideal range.
    Returns 1.0 if within ideal range, degrades linearly outside it.
    """
    if value is None:
        return 0.5   # neutral when unknown

    if ideal_min <= value <= ideal_max:
        return 1.0

    # How far outside the ideal range?
    if value < ideal_min:
        span = ideal_min - (abs_min if abs_min is not None else ideal_min - 20)
        if span <= 0:
            return 0.3
        overshoot = ideal_min - value
        score = max(0.0, 1.0 - (overshoot / span) * 0.7)
    else:
        span = (abs_max if abs_max is not None else ideal_max + 20) - ideal_max
        if span <= 0:
            return 0.3
        overshoot = value - ideal_max
        score = max(0.0, 1.0 - (overshoot / span) * 0.7)

    return round(score, 3)


def _status_label(score: float) -> str:
    if score >= 0.85:
        return "ideal"
    elif score >= 0.60:
        return "slight_issue"
    else:
        return "unsuitable"


def _icon_for_status(status: str) -> str:
    return {"ideal": "✅", "slight_issue": "⚠️", "unsuitable": "❌"}.get(status, "ℹ️")


# ── Watering frequency mapping ──────────────────────────────────────────────────
WATERING_DAYS_MAP = {
    "daily": 1,
    "twice_a_week": 3.5,
    "once_a_week": 7,
    "twice_a_month": 15,
    "rarely": 30,
    "other": 7,
}

WATERING_LABEL_MAP = {
    "1-2 times per week": "twice_a_week",
    "2-3 times per week": "twice_a_week",
    "once per week": "once_a_week",
    "twice per week": "twice_a_week",
    "1-2 times a week": "twice_a_week",
    "2 times per week": "twice_a_week",
    "weekly": "once_a_week",
    "daily": "daily",
    "rarely": "rarely",
}


def _parse_watering_days(freq_str: str | None) -> float:
    """Convert watering frequency string to approximate days between waterings."""
    if freq_str is None:
        return 7.0
    key = WATERING_LABEL_MAP.get(freq_str.lower(), freq_str.lower().replace(" ", "_"))
    return WATERING_DAYS_MAP.get(key, 7.0)


# ── 1. Health Score ─────────────────────────────────────────────────────────────

def compute_health_score(flower_data: dict, env_inputs: dict, stress_result: dict | None = None) -> dict:
    """
    Compute a plant health score (0-100) from flower requirements vs user env.

    Weights:
        temperature  25%
        humidity     20%
        sunlight     20%
        watering     15%
        soil         20%

    Returns:
        {
            score: int,
            grade: str,
            explanation: str,
            breakdown: {factor: {score, weight, contribution, details}},
            disclaimer: str
        }
    """
    temp   = env_inputs.get("temperature")
    humid  = env_inputs.get("humidity")
    sun    = env_inputs.get("sunlight_hours")
    ph     = env_inputs.get("soil_ph")
    soil_t = env_inputs.get("soil_type")
    water  = env_inputs.get("watering_frequency")

    td = flower_data.get("temperature", {})
    hd = flower_data.get("humidity", {})
    sd = flower_data.get("sunlight", {})
    soil_d = flower_data.get("soil", {})
    wd = flower_data.get("watering", {})

    # ── Per-factor scores ────────────────────────────────────────────────────────
    temp_score = _range_score(
        temp,
        td.get("optimal_min", 15), td.get("optimal_max", 25),
        td.get("absolute_min", 0), td.get("absolute_max", 40),
    )

    humid_score = _range_score(
        humid,
        hd.get("min", 40), hd.get("max", 80),
        0, 100,
    )

    sun_min = sd.get("hours_per_day_min", 4)
    sun_max = sd.get("hours_per_day_max", 8)
    sun_score = _range_score(sun, sun_min, sun_max, 0, 24)

    # Soil type score
    preferred_soil = soil_d.get("type", "loamy").lower()
    if soil_t and preferred_soil:
        soil_type_score = 1.0 if soil_t.lower() == preferred_soil else (
            0.7 if any(s in soil_t.lower() for s in preferred_soil.split()) else 0.5
        )
    else:
        soil_type_score = 0.5

    ph_score = _range_score(
        ph,
        soil_d.get("ph_min", 6.0), soil_d.get("ph_max", 7.0),
        3.0, 9.0,
    )
    soil_score = (soil_type_score * 0.5 + ph_score * 0.5)

    # Watering score
    ideal_days = _parse_watering_days(wd.get("frequency"))
    user_days  = _parse_watering_days(water)
    watering_score = _range_score(user_days, ideal_days * 0.7, ideal_days * 1.5, 1, 60)

    # ── Weighted average ─────────────────────────────────────────────────────────
    weights = {"temperature": 0.25, "humidity": 0.20, "sunlight": 0.20,
               "watering": 0.15, "soil": 0.20}
    scores  = {"temperature": temp_score, "humidity": humid_score,
               "sunlight": sun_score, "watering": watering_score, "soil": soil_score}

    weighted_sum = sum(scores[k] * weights[k] for k in weights)
    final_score  = round(weighted_sum * 100)
    if stress_result and stress_result.get("stress_detected"):
        issues_count = len(stress_result.get("issues", []))
        deduction = min(25, 8 + issues_count * 5)
        final_score = max(10, final_score - deduction)

    # ── Grade ────────────────────────────────────────────────────────────────────
    if final_score >= 85:   grade = "Excellent"
    elif final_score >= 70: grade = "Good"
    elif final_score >= 50: grade = "Fair"
    else:                   grade = "Needs Attention"

    # ── Natural-language explanation ─────────────────────────────────────────────
    issues: list[str] = []
    praises: list[str] = []
    flower_name = flower_data.get("common_name", "Your plant")

    if temp_score >= 0.85:  praises.append("temperature is ideal")
    elif temp_score < 0.6:  issues.append(
        f"temperature ({temp}°C) is outside the preferred {td.get('optimal_min')}–{td.get('optimal_max')}°C range"
    )

    if humid_score >= 0.85: praises.append("humidity is ideal")
    elif humid_score < 0.6: issues.append(
        f"humidity ({humid}%) is {'below' if (humid or 0) < hd.get('min', 50) else 'above'} "
        f"the preferred {hd.get('min')}–{hd.get('max')}% range"
    )

    if sun_score >= 0.85:   praises.append("sunlight is adequate")
    elif sun_score < 0.6:   issues.append(
        f"sunlight ({sun}h/day) is {'below' if (sun or 0) < sun_min else 'above'} "
        f"the preferred {sun_min}–{sun_max}h/day"
    )

    if soil_score >= 0.85:  praises.append("soil conditions are suitable")
    elif soil_score < 0.6:  issues.append("soil type or pH may not be ideal for this species")

    if watering_score >= 0.85: praises.append("watering frequency looks appropriate")
    elif watering_score < 0.6: issues.append("watering frequency may need adjustment")

    if issues:
        explanation = (
            f"{flower_name} is scoring {final_score}/100. "
            f"Potential concerns: {'; '.join(issues)}. "
            + (f"Positives: {', '.join(praises)}." if praises else "")
        )
    else:
        explanation = (
            f"{flower_name} appears well-suited to the current conditions. "
            f"All key factors ({', '.join(praises or ['conditions'])}) are within acceptable ranges."
        )

    breakdown = {
        factor: {
            "score": round(scores[factor] * 100),
            "weight": f"{int(weights[factor]*100)}%",
            "raw_score": scores[factor],
        }
        for factor in weights
    }

    return {
        "score": final_score,
        "grade": grade,
        "explanation": explanation,
        "breakdown": breakdown,
        "disclaimer": "This is an AI-generated assessment for guidance purposes only. Not a scientific diagnosis.",
    }


# ── 2. Compatibility Score ──────────────────────────────────────────────────────

def compute_compatibility_score(flower_data: dict, env_inputs: dict) -> dict:
    """
    Per-factor environment compatibility assessment.

    Returns:
        {
            overall_score: int,
            factors: {factor: {status, icon, user_value, ideal_range, message}},
            summary: str,
        }
    """
    temp   = env_inputs.get("temperature")
    humid  = env_inputs.get("humidity")
    sun    = env_inputs.get("sunlight_hours")
    ph     = env_inputs.get("soil_ph")
    soil_t = env_inputs.get("soil_type")
    water  = env_inputs.get("watering_frequency")

    td     = flower_data.get("temperature", {})
    hd     = flower_data.get("humidity", {})
    sd     = flower_data.get("sunlight", {})
    soil_d = flower_data.get("soil", {})
    wd     = flower_data.get("watering", {})
    flower_name = flower_data.get("common_name", "This plant")

    factors: dict[str, dict] = {}

    # Temperature
    ts = _range_score(temp, td.get("optimal_min", 15), td.get("optimal_max", 25),
                      td.get("absolute_min", 0), td.get("absolute_max", 40))
    st = _status_label(ts)
    factors["temperature"] = {
        "status": st,
        "icon": _icon_for_status(st),
        "user_value": f"{temp}°C" if temp is not None else "Not provided",
        "ideal_range": f"{td.get('optimal_min')}–{td.get('optimal_max')}°C",
        "score": round(ts * 100),
        "message": (
            "Temperature is within the ideal range."
            if st == "ideal" else
            f"Temperature is slightly {'low' if (temp or 0) < td.get('optimal_min', 15) else 'high'}. "
            f"Ideal range is {td.get('optimal_min')}–{td.get('optimal_max')}°C."
            if st == "slight_issue" else
            f"Temperature is too {'cold' if (temp or 0) < td.get('optimal_min', 15) else 'hot'} for {flower_name}."
        ),
    }

    # Humidity
    hs = _range_score(humid, hd.get("min", 40), hd.get("max", 80), 0, 100)
    st = _status_label(hs)
    factors["humidity"] = {
        "status": st,
        "icon": _icon_for_status(st),
        "user_value": f"{humid}%" if humid is not None else "Not provided",
        "ideal_range": f"{hd.get('min')}–{hd.get('max')}%",
        "score": round(hs * 100),
        "message": (
            "Humidity is within the preferred range."
            if st == "ideal" else
            f"Humidity is slightly {'low' if (humid or 0) < hd.get('min', 40) else 'high'}. "
            f"Try to maintain {hd.get('min')}–{hd.get('max')}%."
            if st == "slight_issue" else
            f"Humidity is too {'low' if (humid or 0) < hd.get('min', 40) else 'high'} for {flower_name}."
        ),
    }

    # Sunlight
    sun_min = sd.get("hours_per_day_min", 4)
    sun_max = sd.get("hours_per_day_max", 8)
    ss = _range_score(sun, sun_min, sun_max, 0, 24)
    st = _status_label(ss)
    factors["sunlight"] = {
        "status": st,
        "icon": _icon_for_status(st),
        "user_value": f"{sun}h/day" if sun is not None else "Not provided",
        "ideal_range": f"{sun_min}–{sun_max}h/day",
        "score": round(ss * 100),
        "message": (
            f"Sunlight is adequate ({sd.get('requirement', 'as required')})."
            if st == "ideal" else
            f"Sunlight is slightly {'low' if (sun or 0) < sun_min else 'high'}. "
            f"Aim for {sun_min}–{sun_max} hours/day."
            if st == "slight_issue" else
            f"Sunlight is too {'low' if (sun or 0) < sun_min else 'intense'} for {flower_name}. "
            f"It prefers {sd.get('requirement', 'moderate light')}."
        ),
    }

    # Soil type
    preferred = soil_d.get("type", "loamy").lower()
    if soil_t:
        match = 1.0 if soil_t.lower() == preferred else (
            0.7 if any(w in soil_t.lower() for w in preferred.split("/")) else 0.45
        )
    else:
        match = 0.5
    st = _status_label(match)
    factors["soil"] = {
        "status": st,
        "icon": _icon_for_status(st),
        "user_value": soil_t.replace("_", " ").title() if soil_t else "Not provided",
        "ideal_range": preferred.title(),
        "score": round(match * 100),
        "message": (
            f"Soil type ({soil_t}) is suitable."
            if st == "ideal" else
            f"Soil type may work but {preferred.title()} is preferred."
            if st == "slight_issue" else
            f"{flower_name} strongly prefers {preferred.title()} soil."
        ),
    }

    # Soil pH
    ps = _range_score(ph, soil_d.get("ph_min", 6.0), soil_d.get("ph_max", 7.0), 3.0, 9.0)
    st = _status_label(ps)
    factors["soil_ph"] = {
        "status": st,
        "icon": _icon_for_status(st),
        "user_value": str(ph) if ph is not None else "Not provided",
        "ideal_range": f"{soil_d.get('ph_min')}–{soil_d.get('ph_max')}",
        "score": round(ps * 100),
        "message": (
            "Soil pH is within the preferred range."
            if st == "ideal" else
            f"Soil pH ({ph}) is slightly outside the preferred {soil_d.get('ph_min')}–{soil_d.get('ph_max')} range."
            if st == "slight_issue" else
            f"Soil pH ({ph}) is unsuitable. {flower_name} needs pH {soil_d.get('ph_min')}–{soil_d.get('ph_max')}."
        ),
    }

    # Watering
    ideal_days = _parse_watering_days(wd.get("frequency"))
    user_days  = _parse_watering_days(water)
    ws = _range_score(user_days, ideal_days * 0.7, ideal_days * 1.5, 1, 60)
    st = _status_label(ws)
    factors["watering"] = {
        "status": st,
        "icon": _icon_for_status(st),
        "user_value": (water or "Not provided").replace("_", " ").title(),
        "ideal_range": wd.get("frequency", "moderate"),
        "score": round(ws * 100),
        "message": (
            "Watering frequency is appropriate."
            if st == "ideal" else
            f"Watering frequency may be slightly {'too frequent' if user_days < ideal_days * 0.7 else 'infrequent'}."
            if st == "slight_issue" else
            f"Watering frequency needs adjustment. {flower_name} prefers: {wd.get('frequency')}."
        ),
    }

    # Overall score (simple average)
    factor_scores = [f["score"] for f in factors.values()]
    overall = round(sum(factor_scores) / len(factor_scores)) if factor_scores else 50

    # Summary sentence
    good = [k for k, v in factors.items() if v["status"] == "ideal"]
    bad  = [k for k, v in factors.items() if v["status"] == "unsuitable"]
    warn = [k for k, v in factors.items() if v["status"] == "slight_issue"]

    if overall >= 80:
        summary = f"Your environment is well-suited for {flower_name}. Most conditions are ideal."
    elif overall >= 60:
        summary = (
            f"Your environment is moderately suitable for {flower_name}. "
            + (f"Issues: {', '.join(warn + bad)}." if (warn + bad) else "")
        )
    else:
        summary = (
            f"Your environment may not be ideal for {flower_name}. "
            f"Key concerns: {', '.join(bad + warn)}."
        )

    return {
        "overall_score": overall,
        "factors": factors,
        "summary": summary,
    }


# ── 3. Sustainability Score ──────────────────────────────────────────────────────

def compute_sustainability_score(flower_data: dict, env_inputs: dict) -> dict:
    """
    Compute an eco-sustainability score based on water efficiency,
    organic method suitability, local climate match, and pest control.

    Returns: {score, tips, breakdown}
    """
    sus = flower_data.get("sustainability_notes", {})
    soil_t = env_inputs.get("soil_type")

    # Water efficiency
    efficiency_map = {"very high": 1.0, "high": 0.85, "moderate": 0.65, "low": 0.4}
    water_eff = efficiency_map.get(sus.get("water_efficiency", "moderate"), 0.65)

    # Organic fertiliser
    organic_score = 1.0 if sus.get("organic_fertilizer_suitable", False) else 0.5

    # Natural pest control
    pest_score = 1.0 if sus.get("natural_pest_control", True) else 0.5

    # Climate match bonus (if climate provided)
    climate_score = 0.75  # default neutral

    # Weighted score
    overall = round(
        (water_eff * 0.35 + organic_score * 0.25 + pest_score * 0.20 + climate_score * 0.20) * 100
    )

    # Tips
    base_tips = sus.get("eco_tips", [])
    tips: list[str] = list(base_tips)
    if water_eff < 0.7:
        tips.append("This plant has moderate water needs — use mulch to reduce evaporation.")
    if not sus.get("organic_fertilizer_suitable", True):
        tips.append("Avoid excessive synthetic fertilisers; try compost teas.")
    if not sus.get("natural_pest_control", True):
        tips.append("If chemical pest control is needed, choose targeted products with low environmental impact.")
    tips.append("Collect rainwater where possible to irrigate your plants.")
    tips.append("Group plants with similar water needs to avoid over-watering.")

    breakdown = {
        "water_efficiency": {
            "label": "Water Efficiency",
            "score": round(water_eff * 100),
            "note": sus.get("water_efficiency", "moderate").title(),
        },
        "organic_methods": {
            "label": "Organic Fertiliser Suitability",
            "score": round(organic_score * 100),
            "note": "Suitable for organic methods" if organic_score >= 0.9 else "Some synthetic inputs may be needed",
        },
        "natural_pest_control": {
            "label": "Natural Pest Control",
            "score": round(pest_score * 100),
            "note": "Natural methods effective" if pest_score >= 0.9 else "May require targeted pest management",
        },
        "climate_match": {
            "label": "Climate Suitability",
            "score": round(climate_score * 100),
            "note": "Enter your climate zone in the environment form for a personalised score.",
        },
    }

    return {
        "score": overall,
        "tips": tips[:6],
        "breakdown": breakdown,
        "disclaimer": "Sustainability score is an AI-generated estimate based on general horticultural guidance.",
    }


# ── 4. Watering Advice ───────────────────────────────────────────────────────────

def compute_watering_advice(flower_data: dict, env_inputs: dict) -> dict:
    """
    Smart watering recommendation based on species + environment.

    Returns: {recommendation, reason, urgency}
    """
    temp     = env_inputs.get("temperature") or 20
    humid    = env_inputs.get("humidity") or 50
    sun      = env_inputs.get("sunlight_hours") or 6
    soil_t   = env_inputs.get("soil_type") or "loamy"
    water    = env_inputs.get("watering_frequency") or "once_a_week"

    td = flower_data.get("temperature", {})
    hd = flower_data.get("humidity", {})
    wd = flower_data.get("watering", {})
    flower_name = flower_data.get("common_name", "Your plant")

    ideal_days  = _parse_watering_days(wd.get("frequency", "once per week"))
    user_days   = _parse_watering_days(water)

    # Evapotranspiration heuristic: high temp + high sun = more water needed
    et_factor = 1.0
    if temp > 28: et_factor += 0.3
    if temp < 12: et_factor -= 0.2
    if sun > 7:   et_factor += 0.2
    if humid > 70: et_factor -= 0.2
    if soil_t == "sandy": et_factor += 0.3
    if soil_t == "clay":  et_factor -= 0.2

    adjusted_ideal_days = max(1, round(ideal_days / et_factor))

    # Decision
    if user_days <= adjusted_ideal_days * 0.6:
        rec = "reduce_watering"
        days_text = f"Wait {max(1, adjusted_ideal_days - 1)} more day(s)"
        urgency = "low"
        reason = (
            f"{flower_name} may be receiving too much water. "
            f"High {'humidity' if humid > 70 else 'moisture' if soil_t == 'clay' else 'current conditions'} "
            f"means the soil is likely still moist. "
            f"Overwatering can cause root rot and yellowing. "
            f"Check the top 2cm of soil — only water if it feels dry."
        )
    elif user_days <= adjusted_ideal_days * 1.2:
        rec = "water_now"
        days_text = "Water today"
        urgency = "medium"
        reason = (
            f"{flower_name} is due for watering based on its usual schedule "
            f"({'~every '+str(adjusted_ideal_days)+' day(s)'}). "
            f"Current conditions ({temp}°C, {sun}h sun) suggest normal evaporation rate."
        )
    elif user_days <= adjusted_ideal_days * 2.0:
        rec = "check_soil"
        days_text = "Check soil first"
        urgency = "medium"
        reason = (
            f"Watering may be slightly overdue. Check if the top 2–3cm of soil feels dry. "
            f"{flower_name} prefers watering approximately every {adjusted_ideal_days} day(s) "
            f"under current conditions."
        )
    else:
        rec = "water_urgently"
        days_text = "Water as soon as possible"
        urgency = "high"
        reason = (
            f"{flower_name} appears to be underwatered based on its schedule "
            f"and current conditions ({temp}°C, {sun}h sun). "
            f"Prolonged under-watering causes wilting and may stress the plant. "
            f"Water thoroughly until it drains from the bottom."
        )

    return {
        "recommendation": rec,
        "display_text": days_text,
        "reason": reason,
        "urgency": urgency,
        "adjusted_ideal_days": adjusted_ideal_days,
        "disclaimer": "This recommendation is based on general plant-care principles and your input data. "
                      "Always check actual soil moisture before watering.",
    }


# ── 5. What-If Simulator ─────────────────────────────────────────────────────────

def compute_what_if(flower_data: dict, base_env: dict, modified_env: dict) -> dict:
    """
    Compare compatibility scores for original vs modified conditions.

    Returns: {original_score, new_score, change, factor_changes, summary}
    """
    original = compute_compatibility_score(flower_data, base_env)
    modified = compute_compatibility_score(flower_data, modified_env)

    orig_score = original["overall_score"]
    new_score  = modified["overall_score"]
    change     = new_score - orig_score

    # Per-factor changes
    factor_changes: dict[str, dict] = {}
    for factor in original["factors"]:
        o = original["factors"][factor]["score"]
        n = modified["factors"][factor]["score"]
        factor_changes[factor] = {
            "original": o,
            "new": n,
            "change": n - o,
            "improved": n > o,
        }

    if change > 10:
        summary = f"These changes would significantly improve compatibility ({change:+d} points)."
    elif change > 3:
        summary = f"These changes would slightly improve compatibility ({change:+d} points)."
    elif change < -10:
        summary = f"Warning: these changes would reduce compatibility ({change:+d} points)."
    elif change < -3:
        summary = f"These changes would slightly reduce compatibility ({change:+d} points)."
    else:
        summary = "These changes have minimal impact on overall compatibility."

    return {
        "original_score": orig_score,
        "new_score": new_score,
        "change": change,
        "factor_changes": factor_changes,
        "summary": summary,
    }
