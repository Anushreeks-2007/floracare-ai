import React, { useState } from 'react';
import {
  Bug,
  AlertTriangle,
  ShieldCheck,
  Activity,
  HeartCrack,
  CheckCircle2,
  Info
} from 'lucide-react';
import { FlowerProfile, StressDetectionResult } from '../types';

interface DiseaseRiskPageProps {
  currentFlower: FlowerProfile | null;
  allFlowers: FlowerProfile[];
  stressResult: StressDetectionResult | null;
  onSelectFlower: (flower: FlowerProfile) => void;
}

export const DiseaseRiskPage: React.FC<DiseaseRiskPageProps> = ({
  currentFlower,
  allFlowers,
  stressResult,
  onSelectFlower
}) => {
  const [selectedId, setSelectedId] = useState<number>(currentFlower?.id || 1);
  const activeFlower = allFlowers.find((f) => f.id === selectedId) || currentFlower || allFlowers[0];

  return (
    <div className="max-w-6xl mx-auto space-y-8 pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-white p-6 rounded-3xl border border-emerald-100 shadow-sm">
        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-50 border border-amber-200 text-xs font-bold text-amber-800">
            <Bug className="w-3.5 h-3.5 text-amber-600" />
            <span>Pathogen & Pest Defense</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 font-serif mt-1 flex items-center gap-2">
            <span>{activeFlower?.emoji}</span>
            <span>{activeFlower?.common_name} Disease & Pest Profile</span>
          </h1>
          <p className="text-xs text-slate-500 italic">
            Species-specific vulnerabilities, organic treatments, and preventive measures.
          </p>
        </div>
  

        <div className="w-full sm:w-auto">
          <label className="text-xs font-bold text-slate-600 block mb-1">Select Species:</label>
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

      {/* Stress Detection Live Alert Banner (if scan conducted) */}
      {stressResult && (
        <div className={`p-6 rounded-3xl border shadow-sm space-y-3 ${
          stressResult.stress_detected
            ? 'bg-amber-50 border-amber-200 text-amber-950'
            : 'bg-emerald-50 border-emerald-200 text-emerald-950'
        }`}>
          <div className="flex items-center gap-3">
            <Activity className="w-6 h-6 shrink-0 text-amber-600" />
            <div>
              <h3 className="font-bold text-base">
                Computer-Vision Stress Diagnosis from Uploaded Image
              </h3>
              <p className="text-xs text-slate-600">
                Stress Level: {stressResult.overall_stress_level} • Automated pixel-level color distribution
              </p>
            </div>
          </div>

          {stressResult.possible_issues?.length > 0 ? (
            <div className="p-4 bg-white/80 rounded-2xl border border-amber-200/80 space-y-2 text-xs text-slate-700">
              <span className="font-bold text-slate-900">Observed Stress Markers:</span>

              <ul className="list-disc list-inside space-y-2">
                {stressResult.possible_issues.map((iss, i) => (
                  <li key={i}>
                    {typeof iss === 'string' ? (
                      iss
                    ) : (
                      <div className="inline-block">
                        <p className="font-semibold text-slate-900">
                          {iss.label}
                        </p>

                        <p className="text-slate-600 mt-1">
                          {iss.description}
                        </p>

                        {iss.recommended_action && (
                          <p className="text-emerald-800 font-semibold mt-1">
                            Action: {iss.recommended_action}
                          </p>
                        )}
                      </div>
                    )}
                  </li>
                ))}
              </ul>

              <div className="pt-2 border-t border-slate-100 font-semibold text-amber-800">
                Stress Level: {stressResult.overall_stress_level}
              </div>
            </div>
          ) : (
            <p className="text-xs text-emerald-800 font-medium">
              No significant visual stress markers were detected on the uploaded specimen.
            </p>
          )}

          <p className="text-[11px] text-slate-500 italic">
            {stressResult.analysis_note}
          </p>
        </div>
      )}

      {/* Common Diseases Cards */}
      <div className="space-y-4">
        <h2 className="text-xl font-bold text-slate-900 font-serif flex items-center gap-2">
          <HeartCrack className="w-5 h-5 text-rose-500" />
          <span>Documented Species Pathogens & Diseases</span>
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {activeFlower?.diseases.map((d, i) => (
            <div key={i} className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-sm space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                <h3 className="font-bold text-base text-slate-900">{d.name}</h3>
                <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded-full bg-rose-100 text-rose-800">
                  Fungal / Pathogen
                </span>
              </div>

              <div className="space-y-2 text-xs">
                <div>
                  <span className="font-bold text-slate-700 block">Symptoms to look for:</span>
                  <p className="text-slate-600 mt-0.5">{d.symptoms}</p>
                </div>
                <div>
                  <span className="font-bold text-emerald-700 block">Preventive Measures:</span>
                  <p className="text-slate-600 mt-0.5">{d.prevention}</p>
                </div>
                <div className="p-3 bg-emerald-50/60 rounded-xl border border-emerald-100">
                  <span className="font-bold text-emerald-900 block">Safe Organic Treatment:</span>
                  <p className="text-emerald-950 mt-0.5">{d.treatment}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Common Pests Cards */}
      <div className="space-y-4">
        <h2 className="text-xl font-bold text-slate-900 font-serif flex items-center gap-2">
          <Bug className="w-5 h-5 text-amber-500" />
          <span>Common Insect Pests & Parasites</span>
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {activeFlower?.pests.map((p, i) => (
            <div key={i} className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-sm space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                <h3 className="font-bold text-base text-slate-900">{p.name}</h3>
                <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded-full bg-amber-100 text-amber-800">
                  Pest Threat
                </span>
              </div>

              <div className="space-y-2 text-xs">
                <div>
                  <span className="font-bold text-slate-700 block">Damage Symptoms:</span>
                  <p className="text-slate-600 mt-0.5">{p.symptoms}</p>
                </div>
                <div>
                  <span className="font-bold text-emerald-700 block">Prevention / Cultural Control:</span>
                  <p className="text-slate-600 mt-0.5">{p.prevention}</p>
                </div>
                <div className="p-3 bg-amber-50/60 rounded-xl border border-amber-100">
                  <span className="font-bold text-amber-900 block">Natural / Biological Management:</span>
                  <p className="text-amber-950 mt-0.5">{p.treatment}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Safe Organic Philosophy Banner */}
      <div className="p-6 rounded-3xl bg-slate-900 text-slate-200 flex items-start gap-4 shadow-md">
        <ShieldCheck className="w-8 h-8 text-emerald-400 shrink-0 mt-0.5" />
        <div className="space-y-1 text-xs sm:text-sm">
          <h4 className="font-bold text-white text-base">Integrated Pest Management (IPM) Principle</h4>
          <p className="text-slate-400 leading-relaxed">
            FloraCare AI prioritizes physical barriers, beneficial insect conservation (ladybugs, hoverflies), and bio-fungicides like neem oil, potassium bicarbonate, and copper soap over harsh synthetic chemicals that harm pollinator biodiversity.
          </p>
        </div>
      </div>
    </div>
  );
};
