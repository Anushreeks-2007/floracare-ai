import React, { useState, useEffect } from 'react';
import {
  ArrowLeftRight,
  Sparkles,
  Layers,
  Thermometer,
  Droplets,
  Sun,
  ShieldAlert,
  Award,
  RefreshCw
} from 'lucide-react';
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Legend,
  ResponsiveContainer,
  Tooltip
} from 'recharts';
import { api } from '../services/api';
import { FlowerProfile } from '../types';

interface ComparePageProps {
  allFlowers: FlowerProfile[];
}

export const ComparePage: React.FC<ComparePageProps> = ({ allFlowers }) => {
  const [id1, setId1] = useState<number>(allFlowers[0]?.id || 1);
  const [id2, setId2] = useState<number>(allFlowers[1]?.id || 2);
  const [compareData, setCompareData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const fetchComparison = async () => {
    setLoading(true);
    try {
      const res = await api.compareFlowers(id1, id2);
      setCompareData(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (allFlowers.length >= 2) {
      fetchComparison();
    }
  }, [id1, id2]);

  const p1 = compareData?.comparison?.p1_summary;
  const p2 = compareData?.comparison?.p2_summary;

  return (
    <div className="max-w-6xl mx-auto space-y-8 pb-12">
      {/* Header */}
      <div className="text-center space-y-2">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-xs font-bold text-emerald-800">
          <ArrowLeftRight className="w-3.5 h-3.5 text-emerald-600" />
          <span>Species-to-Species Analysis</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-900 font-serif">
          Plant Species Search & Comparison
        </h1>
        <p className="text-sm text-slate-600 max-w-xl mx-auto">
          Compare temperature tolerances, watering rhythms, sunlight demands, and maintenance difficulties side-by-side.
        </p>
      </div>

      {/* Selectors Bar */}
      <div className="bg-white rounded-3xl p-6 border border-emerald-100 shadow-sm grid grid-cols-1 sm:grid-cols-2 gap-6 items-center">
        {/* Plant 1 Selector */}
        <div className="space-y-1.5">
          <label className="text-xs font-bold text-slate-700">Primary Plant Specimen:</label>
          <select
            value={id1}
            onChange={(e) => setId1(Number(e.target.value))}
            className="w-full px-4 py-2.5 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-emerald-500 font-semibold text-slate-800"
          >
            {allFlowers.map((f) => (
              <option key={f.id} value={f.id}>
                {f.emoji} {f.common_name} ({f.climate})
              </option>
            ))}
          </select>
        </div>

        {/* Plant 2 Selector */}
        <div className="space-y-1.5">
          <label className="text-xs font-bold text-slate-700">Comparison Specimen:</label>
          <select
            value={id2}
            onChange={(e) => setId2(Number(e.target.value))}
            className="w-full px-4 py-2.5 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-emerald-500 font-semibold text-slate-800"
          >
            {allFlowers.map((f) => (
              <option key={f.id} value={f.id}>
                {f.emoji} {f.common_name} ({f.climate})
              </option>
            ))}
          </select>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center py-12">
          <RefreshCw className="w-8 h-8 animate-spin text-emerald-600" />
        </div>
      ) : compareData && (
        <div className="space-y-8">
          {/* Radar Chart Section */}
          <div className="bg-white rounded-3xl p-6 sm:p-8 border border-emerald-100 shadow-sm space-y-4">
            <h3 className="font-bold text-lg text-slate-900 font-serif text-center">
              Multi-Dimensional Botanical Radar Profile
            </h3>
            <div className="h-72 w-full flex items-center justify-center">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart cx="50%" cy="50%" outerRadius="80%" data={compareData.comparison.radar_data}>
                  <PolarGrid stroke="#e2e8f0" />
                  <PolarAngleAxis dataKey="subject" tick={{ fontSize: 11, fill: '#475569' }} />
                  <PolarRadiusAxis angle={30} domain={[0, 100]} />
                  <Radar name={p1?.name || 'Plant 1'} dataKey="p1" stroke="#16a34a" fill="#16a34a" fillOpacity={0.4} />
                  <Radar name={p2?.name || 'Plant 2'} dataKey="p2" stroke="#2563eb" fill="#2563eb" fillOpacity={0.4} />
                  <Legend wrapperStyle={{ fontSize: 12 }} />
                  <Tooltip />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Side-by-Side Comparison Matrix */}
          <div className="bg-white rounded-3xl overflow-hidden border border-emerald-100 shadow-sm">
            <div className="grid grid-cols-3 bg-emerald-50/60 p-4 font-bold text-sm text-slate-900 border-b border-emerald-100">
              <span>Metric / Factor</span>
              <span className="text-emerald-800 flex items-center gap-1.5">
                <span>{p1?.emoji}</span>
                <span>{p1?.name}</span>
              </span>
              <span className="text-blue-800 flex items-center gap-1.5">
                <span>{p2?.emoji}</span>
                <span>{p2?.name}</span>
              </span>
            </div>

            <div className="divide-y divide-slate-100 text-xs sm:text-sm">
              {[
                { factor: 'Optimal Temperature', val1: p1?.temp_range, val2: p2?.temp_range },
                { factor: 'Optimal Humidity', val1: `${p1?.humidity_optimal}% (${p1?.humidity_range})`, val2: `${p2?.humidity_optimal}% (${p2?.humidity_range})` },
                { factor: 'Sunlight Demand', val1: `${p1?.sunlight_hours} hrs (${p1?.sunlight_req})`, val2: `${p2?.sunlight_hours} hrs (${p2?.sunlight_req})` },
                { factor: 'Soil Type & pH', val1: `${p1?.soil_type} (pH ${p1?.soil_ph})`, val2: `${p2?.soil_type} (pH ${p2?.soil_ph})` },
                { factor: 'Watering Frequency', val1: p1?.watering_frequency, val2: p2?.watering_frequency },
                { factor: 'Water Efficiency', val1: p1?.eco_water_efficiency, val2: p2?.eco_water_efficiency },
                { factor: 'Care Difficulty', val1: p1?.care_difficulty, val2: p2?.care_difficulty },
                { factor: 'Vulnerabilities', val1: `${p1?.diseases_count} diseases, ${p1?.pests_count} pests`, val2: `${p2?.diseases_count} diseases, ${p2?.pests_count} pests` },
              ].map((row, idx) => (
                <div key={idx} className="grid grid-cols-3 p-4 hover:bg-slate-50/80 transition-colors">
                  <span className="font-semibold text-slate-700">{row.factor}</span>
                  <span className="text-slate-800 font-medium capitalize">{row.val1}</span>
                  <span className="text-slate-800 font-medium capitalize">{row.val2}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
