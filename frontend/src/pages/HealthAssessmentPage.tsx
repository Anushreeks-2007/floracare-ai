import React, { useState, useEffect } from 'react';
import {
  HeartPulse,
  Sliders,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  HelpCircle,
  Sparkles,
  CalendarCheck,
  Droplets,
  Sun,
  Thermometer,
  Layers,
  ArrowRight
} from 'lucide-react';
import { api } from '../services/api';
import { FlowerProfile, HealthScoreResult, CompatibilityResult, ActionPlanResult } from '../types';

interface HealthAssessmentPageProps {
  currentFlower: FlowerProfile | null;
  allFlowers: FlowerProfile[];
  onSelectFlower: (flower: FlowerProfile) => void;
  setActiveTab: (tab: string) => void;
}

export const HealthAssessmentPage: React.FC<HealthAssessmentPageProps> = ({
  currentFlower,
  allFlowers,
  onSelectFlower,
  setActiveTab
}) => {
  // Environmental input state
  const [selectedId, setSelectedId] = useState<number>(currentFlower?.id || 1);
  const [temp, setTemp] = useState<number>(22);
  const [humidity, setHumidity] = useState<number>(60);
  const [sunlightHours, setSunlightHours] = useState<number>(6);
  const [soilType, setSoilType] = useState<string>('loamy');
  const [soilPh, setSoilPh] = useState<number>(6.5);
  const [wateringFreq, setWateringFreq] = useState<string>('2 times per week');

  const [loading, setLoading] = useState(false);
  const [healthScore, setHealthScore] = useState<HealthScoreResult | null>(null);
  const [compatibility, setCompatibility] = useState<CompatibilityResult | null>(null);
  const [actionPlan, setActionPlan] = useState<ActionPlanResult | null>(null);

  useEffect(() => {
    if (currentFlower) {
      setSelectedId(currentFlower.id);
    }
  }, [currentFlower]);

  const activeFlower = allFlowers.find((f) => f.id === selectedId) || currentFlower || allFlowers[0];

  const handleRunAssessment = async () => {
    if (!activeFlower) return;
    setLoading(true);
    const payload = {
      flower_id: activeFlower.id,
      temperature: Number(temp),
      humidity: Number(humidity),
      sunlight_hours: Number(sunlightHours),
      soil_type: soilType,
      soil_ph: Number(soilPh),
      watering_frequency: wateringFreq
    };

    try {
      const [hRes, cRes, aRes] = await Promise.all([
        api.getHealthScore(payload),
        api.getCompatibility(payload),
        api.getActionPlan(payload)
      ]);
      setHealthScore(hRes);
      setCompatibility(cRes);
      setActionPlan(aRes);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activeFlower) {
      handleRunAssessment();
    }
  }, [selectedId]);

  return (
    <div className="max-w-6xl mx-auto space-y-8 pb-12">
      {/* Header */}
      <div className="text-center space-y-2">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-rose-50 border border-rose-200 text-xs font-bold text-rose-800">
          <HeartPulse className="w-3.5 h-3.5 text-rose-600" />
          <span>Condition-Aware Health Engine</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-900 font-serif">
          Plant Health Score & Smart Environment Match
        </h1>
        <p className="text-sm text-slate-600 max-w-2xl mx-auto">
          Input your plant's ambient conditions to receive an AI-calculated Health Score (0–100), per-factor environment compatibility breakdown, and today's action plan.
        </p>
      </div>

      {/* Target Flower Selector & Inputs Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Environment Form */}
        <div className="lg:col-span-1 bg-white rounded-3xl p-6 border border-emerald-100 shadow-sm space-y-5">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <h2 className="font-bold text-base text-slate-900 flex items-center gap-2">
              <Sliders className="w-4 h-4 text-emerald-600" />
              <span>Current Environment</span>
            </h2>
            <span className="text-xs text-slate-500">Live Inputs</span>
          </div>

          {/* Flower Selector */}
          <div className="space-y-1.5">
            <label className="text-xs font-bold text-slate-700">Select Flower Species:</label>
            <select
              value={selectedId}
              onChange={(e) => {
                const newId = Number(e.target.value);
                setSelectedId(newId);
                const found = allFlowers.find((f) => f.id === newId);
                if (found) onSelectFlower(found);
              }}
              className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-emerald-500 focus:outline-none font-medium"
            >
              {allFlowers.map((f) => (
                <option key={f.id} value={f.id}>
                  {f.emoji} {f.common_name} ({f.climate})
                </option>
              ))}
            </select>
          </div>

          {/* Temperature Slider */}
          <div className="space-y-1">
            <div className="flex justify-between text-xs font-bold text-slate-700">
              <span className="flex items-center gap-1"><Thermometer className="w-3.5 h-3.5 text-rose-500" /> Temperature</span>
              <span className="text-emerald-700 font-mono">{temp}°C</span>
            </div>
            <input
              type="range"
              min="-10"
              max="45"
              step="0.5"
              value={temp}
              onChange={(e) => setTemp(Number(e.target.value))}
              className="w-full accent-emerald-600 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-400">
              <span>-10°C</span>
              <span>Ideal: {activeFlower?.temperature.optimal_min}–{activeFlower?.temperature.optimal_max}°C</span>
              <span>45°C</span>
            </div>
          </div>

          {/* Humidity Slider */}
          <div className="space-y-1">
            <div className="flex justify-between text-xs font-bold text-slate-700">
              <span className="flex items-center gap-1"><Droplets className="w-3.5 h-3.5 text-blue-500" /> Humidity</span>
              <span className="text-emerald-700 font-mono">{humidity}%</span>
            </div>
            <input
              type="range"
              min="10"
              max="100"
              value={humidity}
              onChange={(e) => setHumidity(Number(e.target.value))}
              className="w-full accent-emerald-600 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-400">
              <span>10%</span>
              <span>Ideal: {activeFlower?.humidity.min}–{activeFlower?.humidity.max}%</span>
              <span>100%</span>
            </div>
          </div>

          {/* Sunlight Hours */}
          <div className="space-y-1">
            <div className="flex justify-between text-xs font-bold text-slate-700">
              <span className="flex items-center gap-1"><Sun className="w-3.5 h-3.5 text-amber-500" /> Sunlight</span>
              <span className="text-emerald-700 font-mono">{sunlightHours} hrs/day</span>
            </div>
            <input
              type="range"
              min="0"
              max="14"
              value={sunlightHours}
              onChange={(e) => setSunlightHours(Number(e.target.value))}
              className="w-full accent-emerald-600 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-400">
              <span>0h (shade)</span>
              <span>Prefers: {activeFlower?.sunlight.requirement}</span>
              <span>14h (full sun)</span>
            </div>
          </div>

          {/* Soil Type */}
          <div className="space-y-1.5">
            <label className="text-xs font-bold text-slate-700 flex items-center gap-1">
              <Layers className="w-3.5 h-3.5 text-amber-700" /> Soil Substrate:
            </label>
            <select
              value={soilType}
              onChange={(e) => setSoilType(e.target.value)}
              className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-emerald-500 focus:outline-none"
            >
              <option value="loamy">Loamy (Balanced organic soil)</option>
              <option value="sandy">Sandy (Fast draining)</option>
              <option value="clay">Clay (Heavy, moisture retentive)</option>
              <option value="peaty">Peaty / Orchid Bark (Acidic, airy)</option>
              <option value="chalky">Chalky / Alkaline</option>
            </select>
          </div>

          {/* Soil pH */}
          <div className="space-y-1">
            <div className="flex justify-between text-xs font-bold text-slate-700">
              <span>Soil pH</span>
              <span className="text-emerald-700 font-mono">{soilPh}</span>
            </div>
            <input
              type="range"
              min="4.0"
              max="9.0"
              step="0.1"
              value={soilPh}
              onChange={(e) => setSoilPh(Number(e.target.value))}
              className="w-full accent-emerald-600 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-400">
              <span>4.0 (acidic)</span>
              <span>Ideal: {activeFlower?.soil.ph_min}–{activeFlower?.soil.ph_max}</span>
              <span>9.0 (alkaline)</span>
            </div>
          </div>

          {/* Watering Frequency */}
          <div className="space-y-1.5">
            <label className="text-xs font-bold text-slate-700">Watering Frequency:</label>
            <select
              value={wateringFreq}
              onChange={(e) => setWateringFreq(e.target.value)}
              className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-emerald-500 focus:outline-none"
            >
              <option value="daily">Daily</option>
              <option value="2-3 times per week">2-3 times per week</option>
              <option value="2 times per week">2 times per week</option>
              <option value="once a week">Once a week</option>
              <option value="every 2 weeks">Every 2 weeks</option>
            </select>
          </div>

          <button
            onClick={handleRunAssessment}
            disabled={loading}
            className="w-full py-3 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-sm shadow-sm transition-all"
          >
            {loading ? 'Recomputing...' : 'Update Health Assessment'}
          </button>
        </div>

        {/* Right 2 Columns: Health Score & Environment Match */}
        <div className="lg:col-span-2 space-y-6">
          {/* Health Score Main Card */}
          {healthScore && (
            <div className="bg-white rounded-3xl p-6 sm:p-8 border border-emerald-100 shadow-sm space-y-6">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-100">
                <div className="flex items-center gap-4">
                  <div className="relative w-24 h-24 flex items-center justify-center">
                    <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
                      <path
                        className="text-slate-100"
                        strokeWidth="3.5"
                        stroke="currentColor"
                        fill="none"
                        d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                      />
                      <path
                        className={
                          healthScore.score >= 80 ? 'text-emerald-500' :
                          healthScore.score >= 60 ? 'text-amber-500' : 'text-rose-500'
                        }
                        strokeDasharray={`${healthScore.score}, 100`}
                        strokeWidth="3.5"
                        strokeLinecap="round"
                        stroke="currentColor"
                        fill="none"
                        d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                      />
                    </svg>
                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                      <span className="text-2xl font-black text-slate-900 font-mono">{healthScore.score}</span>
                      <span className="text-[10px] uppercase font-bold text-slate-400">/ 100</span>
                    </div>
                  </div>

                  <div>
                    <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                      Personalized Plant Health
                    </span>
                    <h2 className="text-2xl font-bold text-slate-900 font-serif flex items-center gap-2">
                      <span>{activeFlower?.common_name}</span>
                      <span className={`text-xs px-2.5 py-0.5 rounded-full font-bold ${
                        healthScore.grade === 'Excellent' ? 'bg-emerald-100 text-emerald-800' :
                        healthScore.grade === 'Good' ? 'bg-teal-100 text-teal-800' :
                        healthScore.grade === 'Fair' ? 'bg-amber-100 text-amber-800' : 'bg-rose-100 text-rose-800'
                      }`}>
                        Grade: {healthScore.grade}
                      </span>
                    </h2>
                    <p className="text-xs text-slate-500 mt-1">
                      Calculated across 5 environmental factors + visual stress indicators
                    </p>
                  </div>
                </div>

                <div className="text-right">
                  <span className="text-xs text-slate-500">Optimal Climate:</span>
                  <span className="block text-sm font-bold text-slate-800 capitalize">
                    {activeFlower?.climate} Zone
                  </span>
                </div>
              </div>

              {/* Natural language explanation */}
              <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200/80 space-y-1">
                <span className="text-xs font-bold text-slate-700 uppercase tracking-wider">AI Assessment Summary:</span>
                <p className="text-sm text-slate-700 leading-relaxed font-normal">
                  “{healthScore.explanation}”
                </p>
              </div>

              {/* Factor Breakdown Bars */}
              <div className="space-y-3">
                <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Score Contribution Breakdown:</span>
                <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 text-center">
                  {Object.entries(healthScore.breakdown).map(([k, v]) => (
                    <div key={k} className="p-3 bg-slate-50/70 rounded-xl border border-slate-200/60">
                      <span className="text-[11px] font-bold text-slate-500 capitalize block">{k}</span>
                      <span className="text-lg font-black text-slate-900 font-mono mt-0.5 block">{v.score}%</span>
                      <span className="text-[10px] text-slate-400">Weight: {v.weight}</span>
                    </div>
                  ))}
                </div>
              </div>

              <p className="text-[11px] text-slate-400 italic">
                {healthScore.disclaimer}
              </p>
            </div>
          )}

          {/* Smart Environment Match Matrix */}
          {compatibility && (
            <div className="bg-white rounded-3xl p-6 sm:p-8 border border-emerald-100 shadow-sm space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-xl font-bold text-slate-900 font-serif">
                    How Suitable Is Your Environment?
                  </h3>
                  <p className="text-xs text-slate-500">
                    Direct comparison against {activeFlower?.common_name}'s botanical tolerances
                  </p>
                </div>
                <div className="px-3.5 py-1.5 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-extrabold font-mono">
                  Compatibility: {compatibility.overall_score}%
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {Object.entries(compatibility.factors).map(([factorName, f]) => {
                  const isIdeal = f.status === 'ideal';
                  const isSlight = f.status === 'slight_issue';
                  return (
                    <div
                      key={factorName}
                      className={`p-4 rounded-2xl border transition-all ${
                        isIdeal
                          ? 'bg-emerald-50/40 border-emerald-200'
                          : isSlight
                          ? 'bg-amber-50/40 border-amber-200'
                          : 'bg-rose-50/40 border-rose-200'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold uppercase tracking-wider text-slate-700 capitalize flex items-center gap-1.5">
                          <span>{f.icon}</span>
                          <span>{factorName}</span>
                        </span>
                        <span className={`text-xs font-extrabold px-2 py-0.5 rounded-full ${
                          isIdeal ? 'bg-emerald-100 text-emerald-800' :
                          isSlight ? 'bg-amber-100 text-amber-800' : 'bg-rose-100 text-rose-800'
                        }`}>
                          {isIdeal ? '✅ Ideal' : isSlight ? '⚠️ Slight Issue' : '❌ Unsuitable'}
                        </span>
                      </div>

                      <div className="mt-2 text-xs text-slate-600 space-y-0.5">
                        <div className="flex justify-between">
                          <span>Your Input:</span>
                          <span className="font-semibold text-slate-800">{f.user_value}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Ideal Range:</span>
                          <span className="font-semibold text-emerald-700">{f.ideal_range}</span>
                        </div>
                      </div>

                      <p className="mt-2 text-[11px] text-slate-600 leading-snug">
                        {f.message}
                      </p>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* "What Should I Do Today?" Action Plan */}
          {actionPlan && (
            <div className="bg-white rounded-3xl p-6 sm:p-8 border border-emerald-100 shadow-sm space-y-5">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                <div className="flex items-center gap-2.5">
                  <div className="w-9 h-9 rounded-xl bg-emerald-100 text-emerald-700 flex items-center justify-center">
                    <CalendarCheck className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-slate-900 font-serif">
                      🌱 What Should I Do Today?
                    </h3>
                    <p className="text-xs text-slate-500">
                      Personalized daily plant action plan for {actionPlan.flower_name}
                    </p>
                  </div>
                </div>
                <span className="text-xs font-bold text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-200">
                  {actionPlan.total_tasks} Tasks Scheduled
                </span>
              </div>

              <div className="space-y-3">
                {actionPlan.tasks.map((task, i) => (
                  <div
                    key={i}
                    className="p-4 rounded-2xl bg-slate-50/70 border border-slate-200/80 hover:border-emerald-300 transition-all flex items-start gap-3.5"
                  >
                    <span className="text-2xl mt-0.5">{task.icon}</span>
                    <div className="space-y-1 flex-1">
                      <div className="flex items-center justify-between">
                        <h4 className="text-sm font-bold text-slate-900">{task.title}</h4>
                        <span className={`text-[10px] font-extrabold uppercase px-2 py-0.5 rounded-full ${
                          task.priority === 'high' ? 'bg-rose-100 text-rose-800' :
                          task.priority === 'medium' ? 'bg-amber-100 text-amber-800' : 'bg-slate-200 text-slate-700'
                        }`}>
                          {task.priority} Priority
                        </span>
                      </div>
                      <p className="text-xs text-slate-600 leading-relaxed">
                        {task.action}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
