import React, { useState, useEffect } from 'react';
import {
  BarChart3,
  PieChart as PieIcon,
  ScatterChart as ScatterIcon,
  TrendingUp,
  Cpu,
  Layers,
  Sparkles,
  RefreshCw,
  Info
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  ScatterChart,
  Scatter,
  ZAxis
} from 'recharts';
import { api } from '../services/api';

export const AnalyticsPage: React.FC = () => {
  const [summary, setSummary] = useState<any>(null);
  const [mining, setMining] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([api.getAnalyticsSummary(), api.getDataMiningInsights()])
      .then(([s, m]) => {
        setSummary(s);
        setMining(m);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const COLORS = ['#2d6a4f', '#52b788', '#95d5b2', '#d8f3dc', '#b7e4c7', '#74c69d'];
  const CLUSTER_COLORS = ['#2563eb', '#16a34a', '#d97706', '#9333ea'];

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-24 space-y-3">
        <RefreshCw className="w-8 h-8 animate-spin text-emerald-600" />
        <p className="text-sm font-semibold text-slate-600">Running data mining algorithms across 102 flower species...</p>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-8 pb-12">
      {/* Header */}
      <div className="text-center space-y-2">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-purple-50 border border-purple-200 text-xs font-bold text-purple-800">
          <Cpu className="w-3.5 h-3.5 text-purple-600" />
          <span>Data Mining & Machine Learning Analytics</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-900 font-serif">
          Botanical Data Mining & Intelligence Dashboard
        </h1>
        <p className="text-sm text-slate-600 max-w-2xl mx-auto">
          Unsupervised clustering (K-Means), ecological correlations, and environmental tolerance distributions derived from the Oxford 102 Flowers care dataset.
        </p>
      </div>

      {/* Top Metric Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-2xl border border-emerald-100 shadow-sm space-y-1">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Total Species</span>
          <p className="text-2xl sm:text-3xl font-black text-slate-900 font-mono">{summary?.total_species}</p>
          <span className="text-[11px] text-emerald-700 font-medium">Oxford Flowers102 Classes</span>
        </div>
        <div className="bg-white p-5 rounded-2xl border border-emerald-100 shadow-sm space-y-1">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Avg Optimal Temp</span>
          <p className="text-2xl sm:text-3xl font-black text-slate-900 font-mono">
            {summary?.environmental_averages.avg_optimal_temp_min}–{summary?.environmental_averages.avg_optimal_temp_max}°C
          </p>
          <span className="text-[11px] text-slate-500">Global botanical mean</span>
        </div>
        <div className="bg-white p-5 rounded-2xl border border-emerald-100 shadow-sm space-y-1">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Avg Humidity Need</span>
          <p className="text-2xl sm:text-3xl font-black text-slate-900 font-mono">
            {summary?.environmental_averages.avg_optimal_humidity}%
          </p>
          <span className="text-[11px] text-blue-600">Relative ambient moisture</span>
        </div>
        <div className="bg-white p-5 rounded-2xl border border-emerald-100 shadow-sm space-y-1">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Care Archetypes</span>
          <p className="text-2xl sm:text-3xl font-black text-purple-700 font-mono">4 Clusters</p>
          <span className="text-[11px] text-purple-600 font-medium">K-Means Segregation</span>
        </div>
      </div>

      {/* Key Data Mining Discoveries */}
      <div className="bg-gradient-to-r from-purple-900 via-indigo-900 to-slate-900 text-white rounded-3xl p-6 sm:p-8 shadow-xl space-y-6">
        <div className="flex items-center gap-3 pb-3 border-b border-white/10">
          <Sparkles className="w-6 h-6 text-purple-300" />
          <div>
            <h2 className="text-xl font-bold font-serif">Data Mining Discoveries & Findings</h2>
            <p className="text-xs text-purple-200">Statistically discovered patterns from species multidimensional feature vectors</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {mining?.insights.map((ins: any, i: number) => (
            <div key={i} className="p-4 rounded-2xl bg-white/10 border border-white/10 backdrop-blur-sm space-y-1.5">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold text-white">{ins.finding}</h3>
                <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-purple-500/30 text-purple-200">
                  {ins.stat}
                </span>
              </div>
              <p className="text-xs text-purple-100/80 leading-relaxed">{ins.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* 2-Column Visual Charts: Climate Breakdown & Care Difficulty */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Climate Distribution Bar Chart */}
        <div className="bg-white p-6 rounded-3xl border border-emerald-100 shadow-sm space-y-4">
          <h3 className="font-bold text-base text-slate-900 flex items-center gap-2">
            <BarChart3 className="w-4 h-4 text-emerald-600" />
            <span>Species Distribution Across Climate Zones</span>
          </h3>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={summary?.climate_distribution}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="climate" tick={{ fontSize: 11 }} />
                <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="count" fill="#2d6a4f" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Care Difficulty Pie Chart */}
        <div className="bg-white p-6 rounded-3xl border border-emerald-100 shadow-sm space-y-4">
          <h3 className="font-bold text-base text-slate-900 flex items-center gap-2">
            <PieIcon className="w-4 h-4 text-emerald-600" />
            <span>Care Difficulty Breakdown</span>
          </h3>
          <div className="h-64 w-full flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={summary?.difficulty_distribution}
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={85}
                  paddingAngle={5}
                  dataKey="count"
                  nameKey="difficulty"
                  label={({ difficulty, percentage }) => `${difficulty} (${percentage}%)`}
                >
                  {summary?.difficulty_distribution.map((entry: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* K-Means Clustering Visual Scatter & Profiles */}
      <div className="bg-white p-6 sm:p-8 rounded-3xl border border-emerald-100 shadow-sm space-y-6">
        <div>
          <div className="flex items-center justify-between">
            <h3 className="text-xl font-bold text-slate-900 font-serif flex items-center gap-2">
              <ScatterIcon className="w-5 h-5 text-purple-600" />
              <span>K-Means Ecological Clustering (k=4)</span>
            </h3>
            <span className="text-xs px-2.5 py-1 rounded-full bg-purple-50 text-purple-800 font-bold border border-purple-200">
              Unsupervised Learning
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            2D feature space projection: Optimal Temperature vs Optimal Humidity with unsupervised cluster centroid assignments.
          </p>
        </div>

        {/* 4 Cluster Profiles Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {mining?.clusters.map((c: any) => (
            <div
              key={c.cluster_id}
              className="p-4 rounded-2xl border space-y-2"
              style={{ borderColor: `${CLUSTER_COLORS[c.cluster_id]}40`, backgroundColor: `${CLUSTER_COLORS[c.cluster_id]}08` }}
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-extrabold uppercase" style={{ color: CLUSTER_COLORS[c.cluster_id] }}>
                  Cluster #{c.cluster_id + 1}
                </span>
                <span className="text-xs font-mono font-bold text-slate-700">{c.count} species</span>
              </div>
              <h4 className="font-bold text-sm text-slate-900">{c.cluster_name}</h4>
              <div className="text-[11px] text-slate-600 space-y-0.5">
                <div>Centroid Temp: <span className="font-semibold">{c.avg_temp}°C</span></div>
                <div>Centroid Humidity: <span className="font-semibold">{c.avg_humidity}%</span></div>
              </div>
              <p className="text-[10px] text-slate-500 pt-1 border-t border-slate-200/50">
                Examples: {c.representative_flowers.join(', ')}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
