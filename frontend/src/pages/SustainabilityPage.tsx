import React, { useState, useEffect } from 'react';
import {
  Globe,
  Leaf,
  Droplets,
  Recycle,
  Sparkles,
  CheckCircle2,
  AlertCircle,
  ShieldCheck,
  Award
} from 'lucide-react';
import { api } from '../services/api';
import { FlowerProfile, SustainabilityResult } from '../types';

interface SustainabilityPageProps {
  currentFlower: FlowerProfile | null;
  allFlowers: FlowerProfile[];
  onSelectFlower: (flower: FlowerProfile) => void;
}

export const SustainabilityPage: React.FC<SustainabilityPageProps> = ({
  currentFlower,
  allFlowers,
  onSelectFlower
}) => {
  const [selectedId, setSelectedId] = useState<number>(currentFlower?.id || 1);
  const activeFlower = allFlowers.find((f) => f.id === selectedId) || currentFlower || allFlowers[0];

  // User eco-practices toggle
  const [practices, setPractices] = useState({
    rainwater_harvesting: true,
    organic_compost: true,
    natural_pest_management: true,
    mulching: true,
    drip_irrigation: false,
  });

  const [sustainData, setSustainData] = useState<SustainabilityResult | null>(null);

  useEffect(() => {
    if (!activeFlower) return;
    api.getSustainabilityScore({
      flower_id: activeFlower.id,
      environment: {
        temperature: 22,
        humidity: 60,
        soil_type: activeFlower.soil.type
      },
      practices
    }).then(setSustainData).catch(console.error);
  }, [activeFlower, practices]);

  const togglePractice = (key: keyof typeof practices) => {
    setPractices((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8 pb-12">
      {/* Header */}
      <div className="text-center space-y-2">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-teal-50 border border-teal-200 text-xs font-bold text-teal-800">
          <Globe className="w-3.5 h-3.5 text-teal-600" />
          <span>Sustainable Horticultural Stewardship</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-900 font-serif">
          Sustainable Care & Eco-Impact Mode
        </h1>
        <p className="text-sm text-slate-600 max-w-2xl mx-auto">
          Evaluate the ecological footprint of your plant care routine: water conservation, organic soil stewardship, and pollinator habitat enhancement.
        </p>
      </div>

      {/* Main Score Banner */}
      <div className="bg-gradient-to-r from-teal-900 via-emerald-900 to-slate-900 text-white rounded-3xl p-6 sm:p-10 shadow-xl space-y-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6 pb-6 border-b border-white/10">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-2xl bg-teal-500/20 border border-teal-400/30 flex items-center justify-center text-teal-300">
              <Leaf className="w-9 h-9" />
            </div>
            <div>
              <span className="text-xs font-bold uppercase tracking-wider text-teal-300">
                Unique Feature 9 • Environmental Assessment
              </span>
              <h2 className="text-2xl sm:text-3xl font-bold font-serif flex items-center gap-2">
                <span>{activeFlower?.common_name}</span>
                <span className="text-sm font-sans font-extrabold px-3 py-0.5 rounded-full bg-teal-500/30 text-teal-200 border border-teal-400/30">
                  {sustainData?.rating || 'Eco-Friendly'}
                </span>
              </h2>
            </div>
          </div>

          <div className="flex items-center gap-3 bg-white/10 px-5 py-3 rounded-2xl border border-white/15">
            <div className="text-right">
              <span className="text-[10px] text-teal-200 uppercase font-bold tracking-wider block">Sustainability Score</span>
              <span className="text-3xl font-black font-mono text-white">{sustainData?.score || 85}</span>
              <span className="text-xs text-teal-300 font-bold"> / 100</span>
            </div>
            <Award className="w-8 h-8 text-teal-300 ml-1" />
          </div>
        </div>

        <p className="text-sm text-teal-50/90 leading-relaxed max-w-3xl">
          “{sustainData?.summary || 'Excellent sustainability posture. Species water demands are moderate, and practicing natural pest management minimizes harmful soil runoffs.'}”
        </p>
      </div>

      {/* Interactive Eco-Practices Checklist */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Checklist */}
        <div className="lg:col-span-2 bg-white rounded-3xl p-6 sm:p-8 border border-emerald-100 shadow-sm space-y-6">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <div>
              <h3 className="font-bold text-lg text-slate-900 font-serif">
                Your Eco-Friendly Horticultural Practices
              </h3>
              <p className="text-xs text-slate-500">
                Toggle the sustainable habits you practice to dynamically recalculate your score
              </p>
            </div>
            <Recycle className="w-5 h-5 text-emerald-600" />
          </div>

          <div className="space-y-3">
            {[
              { id: 'rainwater_harvesting', label: 'Rainwater Collection & Greywater Reuse', desc: 'Saves municipal treated tap water; provides chlorine-free ambient temperature hydration.' },
              { id: 'organic_compost', label: 'Compost & Organic Matter Amendments', desc: 'Replaces chemical nitrogen/phosphorus synthetics with rich micro-organism humus.' },
              { id: 'natural_pest_management', label: 'Natural Pest Management (IPM)', desc: 'Encourages beneficial predatory insects (ladybugs) and uses cold-pressed neem oils.' },
              { id: 'mulching', label: 'Organic Mulch Layer', desc: 'Suppresses weed competition and retains soil moisture, cutting watering frequency by 40%.' },
              { id: 'drip_irrigation', label: 'Targeted Drip or Sub-irrigation', desc: 'Delivers water strictly to roots, eliminating evaporation loss and fungal leaf spot risks.' },
            ].map((p) => {
              const active = practices[p.id as keyof typeof practices];
              return (
                <div
                  key={p.id}
                  onClick={() => togglePractice(p.id as keyof typeof practices)}
                  className={`p-4 rounded-2xl border cursor-pointer transition-all flex items-start gap-3.5 ${
                    active
                      ? 'bg-emerald-50/60 border-emerald-300'
                      : 'bg-slate-50 border-slate-200 opacity-60 hover:opacity-90'
                  }`}
                >
                  <div className={`w-5 h-5 rounded-md mt-0.5 flex items-center justify-center border transition-all ${
                    active ? 'bg-emerald-600 border-emerald-600 text-white' : 'border-slate-300 bg-white'
                  }`}>
                    {active && <CheckCircle2 className="w-3.5 h-3.5" />}
                  </div>
                  <div className="space-y-0.5">
                    <h4 className="text-sm font-bold text-slate-900">{p.label}</h4>
                    <p className="text-xs text-slate-600">{p.desc}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Col: Actionable Eco Recommendations */}
        <div className="bg-white rounded-3xl p-6 border border-emerald-100 shadow-sm space-y-4">
          <h3 className="font-bold text-base text-slate-900 flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-emerald-600" />
            <span>Recommended Improvements</span>
          </h3>

          <div className="space-y-3 text-xs text-slate-600">
            {sustainData?.actionable_recommendations.map((rec, i) => (
              <div key={i} className="p-3 bg-emerald-50/50 rounded-xl border border-emerald-100 space-y-1">
                <span className="font-bold text-emerald-900 block">Eco Tip #{i + 1}:</span>
                <p>{rec}</p>
              </div>
            )) || (
              <div className="p-3 bg-emerald-50/50 rounded-xl border border-emerald-100 space-y-1">
                <span className="font-bold text-emerald-900 block">Maintain local biodiversity:</span>
                <p>Plant companion herbs like lavender or basil nearby to naturally deter thrips and aphids.</p>
              </div>
            )}
          </div>

          <div className="p-4 rounded-xl bg-slate-900 text-white space-y-2 text-xs">
            <div className="flex items-center gap-2 font-bold text-emerald-300">
              <ShieldCheck className="w-4 h-4" />
              <span>Native Region Alignment</span>
            </div>
            <p className="text-slate-300 leading-relaxed text-[11px]">
              {activeFlower?.common_name} originates in {activeFlower?.sustainability_notes.native_regions.join(', ')}. Growing it in similar climate bands drastically reduces artificial heating and dehumidification energy.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
