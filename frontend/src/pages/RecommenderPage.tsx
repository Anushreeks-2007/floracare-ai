import React, { useState } from 'react';
import {
  Compass,
  Sparkles,
  Search,
  CheckCircle2,
  ArrowRight,
  RefreshCw,
  Sun,
  Droplets,
  Thermometer,
  Layers,
  Award
} from 'lucide-react';
import { api } from '../services/api';
import { FlowerProfile } from '../types';

interface RecommenderPageProps {
  onSelectFlower: (flower: FlowerProfile) => void;
  setActiveTab: (tab: string) => void;
}

export const RecommenderPage: React.FC<RecommenderPageProps> = ({ onSelectFlower, setActiveTab }) => {
  const [temp, setTemp] = useState(22);
  const [humidity, setHumidity] = useState(60);
  const [sunlight, setSunlight] = useState(6);
  const [soilType, setSoilType] = useState('loamy');
  const [waterFreq, setWaterFreq] = useState('2 times per week');
  const [skillLevel, setSkillLevel] = useState('beginner');

  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any>(null);

  const handleRecommend = async () => {
    setLoading(true);
    try {
      const data = await api.recommendFlowers({
        temperature: Number(temp),
        humidity: Number(humidity),
        sunlight_hours: Number(sunlight),
        soil_type: soilType,
        watering_frequency: waterFreq,
        skill_level: skillLevel
      });
      setResults(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleChoosePlant = async (flowerId: number) => {
    try {
      const flower = await api.getFlowerDetail(flowerId);
      onSelectFlower(flower);
      setActiveTab('care');
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8 pb-12">
      {/* Header */}
      <div className="text-center space-y-2">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-xs font-bold text-emerald-800">
          <Compass className="w-3.5 h-3.5 text-emerald-600" />
          <span>Intelligent Plant Matching</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-900 font-serif">
          “Which Flower Should I Grow?”
        </h1>
        <p className="text-sm text-slate-600 max-w-xl mx-auto">
          Tell us about your local environment and gardening preference. Our matching algorithm evaluates all 102 flower species to recommend your top botanical matches.
        </p>
      </div>

      {/* Input Form & Action */}
      <div className="bg-white rounded-3xl p-6 sm:p-8 border border-emerald-100 shadow-sm space-y-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Temperature */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs font-bold text-slate-700">
              <span className="flex items-center gap-1"><Thermometer className="w-3.5 h-3.5 text-rose-500" /> Average Temperature</span>
              <span className="text-emerald-700 font-mono">{temp}°C</span>
            </div>
            <input
              type="range"
              min="5"
              max="38"
              value={temp}
              onChange={(e) => setTemp(Number(e.target.value))}
              className="w-full accent-emerald-600 cursor-pointer"
            />
          </div>

          {/* Humidity */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs font-bold text-slate-700">
              <span className="flex items-center gap-1"><Droplets className="w-3.5 h-3.5 text-blue-500" /> Average Humidity</span>
              <span className="text-emerald-700 font-mono">{humidity}%</span>
            </div>
            <input
              type="range"
              min="20"
              max="95"
              value={humidity}
              onChange={(e) => setHumidity(Number(e.target.value))}
              className="w-full accent-emerald-600 cursor-pointer"
            />
          </div>

          {/* Sunlight */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs font-bold text-slate-700">
              <span className="flex items-center gap-1"><Sun className="w-3.5 h-3.5 text-amber-500" /> Daily Sunlight</span>
              <span className="text-emerald-700 font-mono">{sunlight} hrs/day</span>
            </div>
            <input
              type="range"
              min="2"
              max="12"
              value={sunlight}
              onChange={(e) => setSunlight(Number(e.target.value))}
              className="w-full accent-emerald-600 cursor-pointer"
            />
          </div>

          {/* Soil Type */}
          <div className="space-y-1.5">
            <label className="text-xs font-bold text-slate-700 flex items-center gap-1">
              <Layers className="w-3.5 h-3.5 text-amber-700" /> Available Soil Type:
            </label>
            <select
              value={soilType}
              onChange={(e) => setSoilType(e.target.value)}
              className="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-emerald-500 focus:outline-none"
            >
              <option value="loamy">Loamy (Standard rich garden soil)</option>
              <option value="sandy">Sandy (Dry, well-draining)</option>
              <option value="clay">Clay (Heavy, moisture-dense)</option>
              <option value="peaty">Peaty (Acidic, bark/moss)</option>
            </select>
          </div>

          {/* Watering Commitment */}
          <div className="space-y-1.5">
            <label className="text-xs font-bold text-slate-700">Available Watering Schedule:</label>
            <select
              value={waterFreq}
              onChange={(e) => setWaterFreq(e.target.value)}
              className="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-emerald-500 focus:outline-none"
            >
              <option value="once a week">Low (Once a week / drought hardy)</option>
              <option value="2 times per week">Moderate (1-2 times per week)</option>
              <option value="2-3 times per week">Frequent (2-3 times per week)</option>
            </select>
          </div>

          {/* Gardening Experience */}
          <div className="space-y-1.5">
            <label className="text-xs font-bold text-slate-700">Gardening Experience:</label>
            <select
              value={skillLevel}
              onChange={(e) => setSkillLevel(e.target.value)}
              className="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-emerald-500 focus:outline-none"
            >
              <option value="beginner">Beginner (Prefers resilient, forgiving flowers)</option>
              <option value="intermediate">Intermediate</option>
              <option value="expert">Expert (Can handle delicate orchids & special pH)</option>
            </select>
          </div>
        </div>

        <div className="flex justify-center pt-2">
          <button
            onClick={handleRecommend}
            disabled={loading}
            className="flex items-center gap-2 px-8 py-3.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-sm shadow-md transition-all hover:scale-[1.02] active:scale-[0.98]"
          >
            {loading ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Evaluating 102 Species...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>Find Best Flower Matches</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Recommended Matches List */}
      {results && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-slate-900 font-serif">
              Top Flower Matches For Your Environment
            </h2>
            <span className="text-xs text-slate-500">
              Evaluated {results.total_evaluated} candidate species
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {results.top_recommendations.map((rec: any, idx: number) => (
              <div
                key={rec.id}
                className="bg-white rounded-3xl p-6 border border-emerald-100 shadow-sm hover:shadow-md transition-all flex flex-col justify-between space-y-4 relative overflow-hidden"
              >
                {/* Rank Badge */}
                <div className="absolute top-0 right-0 bg-emerald-600 text-white text-[11px] font-extrabold px-3 py-1 rounded-bl-xl">
                  #{idx + 1} Best Match
                </div>

                <div className="space-y-3">
                  <div className="flex items-center gap-3">
                    <span className="text-4xl p-2 bg-emerald-50 rounded-2xl border border-emerald-100">
                      {rec.emoji}
                    </span>
                    <div>
                      <h3 className="text-lg font-bold text-slate-900">{rec.name}</h3>
                      <p className="text-xs italic text-slate-400 font-serif">{rec.scientific_name}</p>
                    </div>
                  </div>

                  <div className="flex items-center justify-between py-2 border-y border-slate-100 text-xs">
                    <span className="text-slate-500 font-medium">Compatibility:</span>
                    <span className="text-lg font-black text-emerald-700 font-mono">
                      {rec.match_score}%
                    </span>
                  </div>

                  {/* Why recommended */}
                  <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200/80 space-y-1">
                    <span className="text-[11px] font-bold text-slate-700 uppercase tracking-wider block">
                      Why this was recommended:
                    </span>
                    <p className="text-xs text-slate-600 leading-relaxed font-normal">
                      “{rec.explanation}”
                    </p>
                  </div>

                  <div className="text-[11px] text-slate-500 space-y-1">
                    <div>Light: <span className="font-semibold text-slate-700">{rec.sunlight_req}</span></div>
                    <div>Water: <span className="font-semibold text-slate-700">{rec.watering_frequency}</span></div>
                    <div>Difficulty: <span className="font-semibold capitalize text-emerald-700">{rec.care_difficulty}</span></div>
                  </div>
                </div>

                <button
                  onClick={() => handleChoosePlant(rec.id)}
                  className="w-full py-2.5 rounded-xl bg-emerald-50 hover:bg-emerald-600 text-emerald-800 hover:text-white font-bold text-xs border border-emerald-200 transition-all flex items-center justify-center gap-1.5"
                >
                  <span>Select & View Full Care Plan</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
