export interface FlowerProfile {
  id: number;
  oxford_label: string;
  common_name: string;
  scientific_name: string;
  emoji: string;
  description: string;
  temperature: {
    optimal_min: number;
    optimal_max: number;
    absolute_min: number;
    absolute_max: number;
    unit: string;
  };
  humidity: {
    min: number;
    max: number;
    optimal: number;
    unit: string;
  };
  sunlight: {
    requirement: string;
    hours_per_day_min: number;
    hours_per_day_max: number;
    description: string;
  };
  climate: string;
  growing_season: string;
  soil: {
    type: string;
    ph_min: number;
    ph_max: number;
    drainage: string;
    fertility: string;
    nutrients: string[];
  };
  watering: {
    frequency: string;
    intensity: string;
    overwatering_signs: string[];
    underwatering_signs: string[];
  };
  nutrition: {
    fertilizer: string;
    key_nutrients: string[];
    fertilize_when: string;
    precautions: string;
  };
  diseases: Array<{
    name: string;
    symptoms: string;
    prevention: string;
    treatment: string;
  }>;
  pests: Array<{
    name: string;
    symptoms: string;
    prevention: string;
    treatment: string;
  }>;
  care_difficulty: 'easy' | 'moderate' | 'hard';
  sustainability_notes: {
    water_efficiency: string;
    organic_fertilizer_suitable: boolean;
    natural_pest_control: boolean;
    native_regions: string[];
    eco_tips: string[];
  };
  visual_features: {
    petal_color: string[];
    petal_shape: string;
    petal_arrangement: string;
    distinctive_features: string[];
  };
}

export interface PredictionCandidate {
  rank: number;
  label: string;
  name: string;
  confidence: number;
  emoji: string;
}

export interface PredictionResult {
  success: boolean;
  flower_id: number;
  flower_label: string;
  flower_name: string;
  emoji: string;
  confidence: number;
  top_predictions: PredictionCandidate[];
  visual_features: {
    dominant_colors: string[];
    avg_brightness: number;
    green_fraction: number;
    vivid_fraction: number;
  };
  ai_explanation: string;
  model_info: {
    architecture: string;
    weights: string;
    classes: number;
  };
}

export interface StressDetectionResult {
  stress_detected: boolean;
  possible_issues: Array<{
    label: string;
    description: string;
    recommended_action: string;
  }>;
  overall_stress_level: 'low' | 'moderate' | 'high' | string;
  analysis_note: string;
}
export interface HealthScoreResult {
  score: number;
  grade: string;
  explanation: string;
  breakdown: Record<string, {
    score: number;
    weight: string;
    raw_score: number;
  }>;
  disclaimer: string;
}

export interface CompatibilityFactor {
  status: 'ideal' | 'slight_issue' | 'too_low' | 'too_high';
  icon: string;
  user_value: string;
  ideal_range: string;
  score: number;
  message: string;
}

export interface CompatibilityResult {
  overall_score: number;
  factors: Record<string, CompatibilityFactor>;
  summary: string;
}

export interface DailyTask {
  title: string;
  category: string;
  priority: 'high' | 'medium' | 'low';
  icon: string;
  action: string;
}

export interface ActionPlanResult {
  flower_id: number;
  flower_name: string;
  date_assessed: string;
  total_tasks: number;
  tasks: DailyTask[];
}

export interface WateringAdviceResult {
  recommendation: 'Water today' | 'Wait' | 'Check soil first';
  icon: string;
  urgency: 'high' | 'medium' | 'low';
  reason: string;
  next_check_days: number;
  soil_moisture_disclaimer: string;
}

export interface SustainabilityResult {
  score: number;
  rating: string;
  summary: string;
  breakdown: Record<string, {
    score: number;
    weight: string;
    description: string;
  }>;
  actionable_recommendations: string[];
}

export interface WhatIfResult {
  original_score: number;
  new_score: number;
  change: number;
  improved: boolean;
  factor_changes: Record<string, {
    original: number;
    new: number;
    change: number;
    improved: boolean;
  }>;
  summary: string;
}

export interface PlantProfile {
  id: string;
  flower_id: number;
  flower_name: string;
  scientific_name: string;
  emoji: string;
  nickname: string;
  location: string;
  notes: string;
  watering_day: string;
  care_difficulty: string;
  climate: string;
  sunlight: string;
  watering_freq: string;
  created_at: string;
  journal_entries: JournalEntry[];
}

export interface JournalEntry {
  id: string;
  date: string;
  day_label: string;
  notes: string;
  image_url?: string;
  cv_metrics?: {
    greenness_index: number;
    coverage_pct: number;
    vitality: string;
  };
}
