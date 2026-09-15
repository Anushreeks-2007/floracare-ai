import React, { useState, useEffect } from 'react';
import {
  Droplets,
  Thermometer,
  Sun,
  Layers,
  Sparkles,
  Sliders,
  AlertCircle,
  Clock,
  HelpCircle,
  CheckCircle2,
  TrendingUp,
  TrendingDown,
  Info
} from 'lucide-react';
import { api } from '../services/api';
import { FlowerProfile, WateringAdviceResult, WhatIfResult } from '../types';

interface CarePlanPageProps {
  currentFlower: FlowerProfile | null;
  allFlowers: FlowerProfile[];
  onSelectFlower: (flower: FlowerProfile) => void;
}

export const CarePlanPage: React.FC<CarePlanPageProps> = ({
  currentFlower,
  allFlowers,
  onSelectFlower
}) => {
  const [selectedId, setSelectedId] = useState<number>(currentFlower?.id || 1);
  const activeFlower = allFlowers.find((f) => f.id === selectedId) || currentFlower || allFlowers[0];

  // Watering Advisor state
  const [wateringAdvice, setWateringAdvice] = useState<WateringAdviceResult | null>(null);
  const [recentWatering, setRecentWatering] = useState<string>('3 days ago');

  // What-If Simulator state
  const [simTemp, setSimTemp] = useState<number>(22);
  const [simHumid, setSimHumid] = useState<number>(60);
  const [simSun, setSimSun] = useState<number>(6);
  const [simPh, setSimPh] = useState<number>(6.5);
  const [whatIfResult, setWhatIfResult] = useState<WhatIfResult | null>(null);
  const [simLoading, setSimLoading] = useState(false);

  // Fetch initial watering advice
  useEffect(() => {
    if (!activeFlower) return;
    api.getWateringAdvice({
      flower_id: activeFlower.id,
      temperature: simTemp,
      humidity: simHumid,
      sunlight_hours: simSun,
      soil_type: activeFlower.soil.type,
      recent_watering: recentWatering
    }).then(setWateringAdvice).catch(console.error);
  }, [activeFlower, recentWatering, simTemp, simHumid]);

  // Run What-If simulation
  useEffect(() => {
    if (!activeFlower) return;
    setSimLoading(true);
    api.runWhatIfSimulation({
      flower_id: activeFlower.id,
      base_env: {
        temperature: 15,
        humidity: 40,
        sunlight_hours: 4,
        soil_ph: 5.5
      },
      modifications: {
        temperature: simTemp,
        humidity: simHumid,
        sunlight_hours: simSun,
        soil_ph: simPh
      }
    })
      .then(setWhatIfResult)
      .catch(console.error)
      .finally(() => setSimLoading(false));
  }, [activeFlower, simTemp, simHumid, simSun, simPh]);

  return (
    <div className="max-w-6xl mx-auto space-y-8 pb-12">
      {/* Header & Flower Picker */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-white p-6 rounded-3xl border border-emerald-100 shadow-sm">
        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-xs font-bold text-emerald-800">
            <Droplets className="w-3.5 h-3.5 text-emerald-600" />
            <span>Species-Specific Care Specifications</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 font-serif mt-1 flex items-center gap-2">
            <span>{activeFlower?.emoji}</span>
            <span>{activeFlower?.common_name} Care Guide</span>
          </h1>
          <p className="text-xs text-slate-500 italic font-serif">
            {activeFlower?.scientific_name} • Native to {activeFlower?.sustainability_notes.native_regions.join(', ')}
          </p>
        </div>

        <div className="w-full sm:w-auto">
          <label className="text-xs font-bold text-slate-600 block mb-1">Switch Plant Profile:</label>
          <select
            value={selectedId}
            onChange={(e) => {
              const id = Number(e.target.value);
              setSelectedId(id);
              const found = allFlowers.find((f) => f.id === id);
              if (found) onSelectFlower(found);
            }}
            className="px-3.5 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-emerald-500 focus:outline-none font-semibold text-slate-800"
          >
            {allFlowers.map((f) => (
              <option key={f.id} value={f.id}>
                {f.emoji} {f.common_name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Unique Feature 10: Smart Watering Advisor */}
      {wateringAdvice && (
        <div className="bg-gradient-to-br from-blue-900 via-indigo-950 to-slate-900 text-white rounded-3xl p-6 sm:p-8 shadow-xl space-y-6">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-white/10">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-2xl bg-blue-500/20 border border-blue-400/30 flex items-center justify-center text-blue-300">
                <Droplets className="w-7 h-7" />
              </div>
              <div>
                <span className="text-[11px] font-bold uppercase tracking-wider text-blue-300">
                  Unique Feature 10 • Smart Watering Advisor
                </span>
                <h2 className="text-xl sm:text-2xl font-extrabold tracking-tight">
                  Watering Recommendation: <span className="text-blue-200 font-serif underline decoration-blue-400/60">{wateringAdvice.recommendation}</span>
                </h2>
              </div>
            </div>

            <div className="flex items-center gap-2 text-xs bg-white/10 px-3 py-1.5 rounded-xl border border-white/15">
              <Clock className="w-3.5 h-3.5 text-blue-300" />
              <span>Next Check: in {wateringAdvice.next_check_days} days</span>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 space-y-3">
              <div className="p-4 rounded-2xl bg-white/10 border border-white/10 backdrop-blur-md space-y-1">
                <span className="text-xs font-bold text-blue-200 uppercase tracking-wider">Algorithmic Rationale:</span>
                <p className="text-sm text-slate-100 leading-relaxed">
                  “{wateringAdvice.reason}”
                </p>
              </div>

              <p className="text-[11px] text-slate-400 italic">
                {wateringAdvice.soil_moisture_disclaimer}
              </p>
            </div>

            <div className="p-4 rounded-2xl bg-white/5 border border-white/10 space-y-2">
              <span className="text-xs font-bold text-slate-300 uppercase tracking-wider">Recent Watering Input:</span>
              <select
                value={recentWatering}
                onChange={(e) => setRecentWatering(e.target.value)}
                className="w-full px-3 py-2 text-xs bg-slate-800 border border-slate-700 rounded-xl text-white focus:outline-none focus:ring-1 focus:ring-blue-400"
              >
                <option value="today">Watered Today</option>
                <option value="yesterday">Watered Yesterday</option>
                <option value="3 days ago">3 days ago</option>
                <option value="5 days ago">5 days ago</option>
                <option value="over a week ago">Over a week ago</option>
              </select>
              <p className="text-[10px] text-slate-400">
                Species Baseline: {activeFlower?.watering.frequency} ({activeFlower?.watering.intensity} intensity)
              </p>
            </div>
          </div>
        </div>
      )}

      {/* 4 Core Care Requirement Pillars */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* 1. Environmental */}
        <div className="bg-white rounded-3xl p-6 border border-emerald-100 shadow-sm space-y-4">
          <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-700 flex items-center justify-center">
            <Thermometer className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-bold text-base text-slate-900">🌡️ Climate & Temp</h3>
            <p className="text-xs text-slate-500 capitalize">{activeFlower?.climate} Zone • {activeFlower?.growing_season} bloom</p>
          </div>
          <div className="space-y-2 text-xs text-slate-600 border-t border-slate-100 pt-3">
            <div className="flex justify-between">
              <span>Optimal Temp:</span>
              <span className="font-bold text-slate-800">{activeFlower?.temperature.optimal_min}–{activeFlower?.temperature.optimal_max}°C</span>
            </div>
            <div className="flex justify-between">
              <span>Absolute Limits:</span>
              <span className="font-bold text-slate-800">{activeFlower?.temperature.absolute_min} to {activeFlower?.temperature.absolute_max}°C</span>
            </div>
            <div className="flex justify-between">
              <span>Humidity Range:</span>
              <span className="font-bold text-slate-800">{activeFlower?.humidity.min}–{activeFlower?.humidity.max}%</span>
            </div>
          </div>
        </div>

        {/* 2. Sunlight */}
        <div className="bg-white rounded-3xl p-6 border border-emerald-100 shadow-sm space-y-4">
          <div className="w-10 h-10 rounded-xl bg-amber-50 text-amber-700 flex items-center justify-center">
            <Sun className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-bold text-base text-slate-900">☀️ Light Needs</h3>
            <p className="text-xs text-slate-500 capitalize">{activeFlower?.sunlight.requirement}</p>
          </div>
          <div className="space-y-2 text-xs text-slate-600 border-t border-slate-100 pt-3">
            <div className="flex justify-between">
              <span>Daily Exposure:</span>
              <span className="font-bold text-slate-800">{activeFlower?.sunlight.hours_per_day_min}–{activeFlower?.sunlight.hours_per_day_max} hrs/day</span>
            </div>
            <p className="text-[11px] text-slate-600 leading-snug">
              {activeFlower?.sunlight.description}
            </p>
          </div>
        </div>

        {/* 3. Soil */}
        <div className="bg-white rounded-3xl p-6 border border-emerald-100 shadow-sm space-y-4">
          <div className="w-10 h-10 rounded-xl bg-orange-50 text-orange-700 flex items-center justify-center">
            <Layers className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-bold text-base text-slate-900">🌱 Soil & pH</h3>
            <p className="text-xs text-slate-500 capitalize">{activeFlower?.soil.type} ({activeFlower?.soil.drainage})</p>
          </div>
          <div className="space-y-2 text-xs text-slate-600 border-t border-slate-100 pt-3">
            <div className="flex justify-between">
              <span>Suitable pH:</span>
              <span className="font-bold text-slate-800">{activeFlower?.soil.ph_min} – {activeFlower?.soil.ph_max}</span>
            </div>
            <div className="flex justify-between">
              <span>Soil Fertility:</span>
              <span className="font-bold text-slate-800 capitalize">{activeFlower?.soil.fertility}</span>
            </div>
            <div className="flex justify-between">
              <span>Key Nutrients:</span>
              <span className="font-bold text-slate-800 capitalize">{activeFlower?.soil.nutrients.join(', ')}</span>
            </div>
          </div>
        </div>

        {/* 4. Nutrition */}
        <div className="bg-white rounded-3xl p-6 border border-emerald-100 shadow-sm space-y-4">
          <div className="w-10 h-10 rounded-xl bg-teal-50 text-teal-700 flex items-center justify-center">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-bold text-base text-slate-900">🌿 Nutrition</h3>
            <p className="text-xs text-slate-500">Feeding Guidelines</p>
          </div>
          <div className="space-y-2 text-xs text-slate-600 border-t border-slate-100 pt-3">
            <p className="text-[11px] text-slate-700 font-medium">
              {activeFlower?.nutrition.fertilizer}
            </p>
            <p className="text-[10px] text-slate-500">
              Schedule: {activeFlower?.nutrition.fertilize_when}
            </p>
          </div>
        </div>
      </div>

      {/* Unique Feature 8: What-If Simulator */}
      <div className="bg-white rounded-3xl p-6 sm:p-8 border border-emerald-100 shadow-sm space-y-6">
        <div className="flex items-center justify-between pb-4 border-b border-slate-100">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-100 text-emerald-700 flex items-center justify-center">
              <Sliders className="w-5 h-5" />
            </div>
            <div>
              <span className="text-xs font-bold uppercase tracking-wider text-emerald-700">
                Unique Feature 8 • Interactive Experimentation
              </span>
              <h3 className="text-xl font-bold text-slate-900 font-serif">
                “What If I Change The Conditions?” Simulator
              </h3>
            </div>
          </div>

          {whatIfResult && (
            <div className="flex items-center gap-3">
              <div className="text-right">
                <span className="text-[11px] text-slate-400 block">Current Compatibility</span>
                <span className="text-xs font-mono font-semibold text-slate-500 line-through">
                  {whatIfResult.original_score}%
                </span>
              </div>
              <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-emerald-50 border border-emerald-200">
                <span className="text-lg font-black font-mono text-emerald-800">
                  {whatIfResult.new_score}%
                </span>
                {whatIfResult.change >= 0 ? (
                  <TrendingUp className="w-4 h-4 text-emerald-600" />
                ) : (
                  <TrendingDown className="w-4 h-4 text-rose-500" />
                )}
              </div>
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {/* Slider 1: Temp */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs font-bold text-slate-700">
              <span>Adjust Temp</span>
              <span className="text-emerald-700 font-mono">{simTemp}°C</span>
            </div>
            <input
              type="range"
              min="0"
              max="40"
              value={simTemp}
              onChange={(e) => setSimTemp(Number(e.target.value))}
              className="w-full accent-emerald-600 cursor-pointer"
            />
          </div>

          {/* Slider 2: Humidity */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs font-bold text-slate-700">
              <span>Adjust Humidity</span>
              <span className="text-emerald-700 font-mono">{simHumid}%</span>
            </div>
            <input
              type="range"
              min="10"
              max="100"
              value={simHumid}
              onChange={(e) => setSimHumid(Number(e.target.value))}
              className="w-full accent-emerald-600 cursor-pointer"
            />
          </div>

          {/* Slider 3: Sunlight */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs font-bold text-slate-700">
              <span>Adjust Sunlight</span>
              <span className="text-emerald-700 font-mono">{simSun} hrs</span>
            </div>
            <input
              type="range"
              min="0"
              max="14"
              value={simSun}
              onChange={(e) => setSimSun(Number(e.target.value))}
              className="w-full accent-emerald-600 cursor-pointer"
            />
          </div>

          {/* Slider 4: Soil pH */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs font-bold text-slate-700">
              <span>Adjust Soil pH</span>
              <span className="text-emerald-700 font-mono">{simPh}</span>
            </div>
            <input
              type="range"
              min="4.5"
              max="8.5"
              step="0.1"
              value={simPh}
              onChange={(e) => setSimPh(Number(e.target.value))}
              className="w-full accent-emerald-600 cursor-pointer"
            />
          </div>
        </div>

        {whatIfResult && (
          <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200/80 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs">
            <p className="text-slate-700 leading-relaxed font-normal">
              “{whatIfResult.summary}”
            </p>
            <span className={`px-2.5 py-1 rounded-full font-bold whitespace-nowrap ${
              whatIfResult.change > 0 ? 'bg-emerald-100 text-emerald-800' :
              whatIfResult.change < 0 ? 'bg-rose-100 text-rose-800' : 'bg-slate-200 text-slate-700'
            }`}>
              {whatIfResult.change > 0 ? `+${whatIfResult.change}% Improvement` : `${whatIfResult.change}% Delta`}
            </span>
          </div>
        )}
      </div>
    </div>
  );
};
