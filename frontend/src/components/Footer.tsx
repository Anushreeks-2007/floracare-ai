import React from 'react';
import { Sprout, ShieldCheck, Heart } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="bg-slate-900 text-slate-300 py-12 border-t border-slate-800 mt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-white font-bold text-lg">
              <div className="w-8 h-8 rounded-lg bg-emerald-600 flex items-center justify-center text-white">
                <Sprout className="w-5 h-5" />
              </div>
              <span>FloraCare AI</span>
            </div>
            <p className="text-sm text-slate-400 leading-relaxed">
              Intelligent Flower Plant Health, Care & Sustainability System. Powered by transfer learning on Oxford 102 Flowers and real ecological datasets.
            </p>
          </div>

          <div>
            <h4 className="text-white font-semibold text-sm mb-3">AI & Plant Science</h4>
            <ul className="space-y-2 text-sm text-slate-400">
              <li>MobileNetV2 Vision Architecture</li>
              <li>Oxford 102 Flowers Dataset</li>
              <li>Explainable AI (Feature Attribution)</li>
              <li>Computer-Vision Stress Detection</li>
            </ul>
          </div>

          <div>
            <h4 className="text-white font-semibold text-sm mb-3">Care Intelligence</h4>
            <ul className="space-y-2 text-sm text-slate-400">
              <li>Personalized Health Score (0–100)</li>
              <li>Smart Environment Matching</li>
              <li>What-If Environmental Simulator</li>
              <li>Eco-Friendly Sustainable Care Mode</li>
            </ul>
          </div>

          <div>
            <h4 className="text-white font-semibold text-sm mb-3">Advisory Disclaimer</h4>
            <div className="flex items-start gap-2 p-3 rounded-lg bg-slate-800/60 border border-slate-700/60 text-xs text-slate-400">
              <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              <p>
                All plant health, compatibility scores, and watering tips are AI-generated recommendations for guidance purposes, not laboratory scientific diagnoses.
              </p>
            </div>
          </div>
        </div>

        <div className="border-t border-slate-800 pt-6 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500">
          <p>© {new Date().getFullYear()} FloraCare AI System. Designed with botanical care.</p>
          <p className="flex items-center gap-1 mt-2 sm:mt-0">
            Engineered for sustainable plant stewardship <Heart className="w-3.5 h-3.5 text-emerald-500 fill-emerald-500" />
          </p>
        </div>
      </div>
    </footer>
  );
};
