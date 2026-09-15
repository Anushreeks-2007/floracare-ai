import React from 'react';
import {
  Scan,
  HeartPulse,
  Droplets,
  Bug,
  Globe,
  BarChart3,
  ArrowRight,
  Sparkles,
  CheckCircle2,
  Compass,
  Layers,
  Leaf
} from 'lucide-react';

interface HomePageProps {
  setActiveTab: (tab: string) => void;
}

export const HomePage: React.FC<HomePageProps> = ({ setActiveTab }) => {
  const featureCards = [
    {
      id: 'identify',
      icon: Scan,
      title: '🌸 AI Identification',
      tag: 'Oxford 102 Species',
      desc: 'Deep learning classification using fine-tuned MobileNetV2 with Explainable AI visual attribution.',
      color: 'from-emerald-500/10 to-teal-500/10 border-emerald-200'
    },
    {
      id: 'health',
      icon: HeartPulse,
      title: '🌱 Health Assessment',
      tag: '0–100 Health Score',
      desc: 'Dynamic evaluation of species requirements against your local temperature, humidity, and soil.',
      color: 'from-rose-500/10 to-orange-500/10 border-rose-200'
    },
    {
      id: 'care',
      icon: Droplets,
      title: '💧 Smart Watering',
      tag: 'Condition-Aware Advisor',
      desc: 'Predictive watering advisor: "Water today / Wait / Check soil first" based on environmental factors.',
      color: 'from-blue-500/10 to-cyan-500/10 border-blue-200'
    },
    {
      id: 'disease',
      icon: Bug,
      title: '🦠 Disease Risk',
      tag: 'CV Stress Detection',
      desc: 'Computer-vision analysis of leaf yellowing, brown spots, and wilting with safe organic treatments.',
      color: 'from-amber-500/10 to-yellow-500/10 border-amber-200'
    },
    {
      id: 'sustainability',
      icon: Globe,
      title: '🌍 Sustainable Care',
      tag: 'Eco-Score & Conservation',
      desc: 'Eco-friendly gardening practices: rainwater reuse, natural pest management, and organic soil health.',
      color: 'from-teal-500/10 to-emerald-500/10 border-teal-200'
    },
    {
      id: 'analytics',
      icon: BarChart3,
      title: '📊 Data Insights',
      tag: 'Data Mining & Clustering',
      desc: 'Unsupervised K-Means clustering of 102 species into ecological archetypes and correlation patterns.',
      color: 'from-purple-500/10 to-indigo-500/10 border-purple-200'
    },
  ];

  return (
    <div className="space-y-16 pb-12">
      {/* Botanical Hero Section */}
      <section className="relative overflow-hidden rounded-3xl botanical-gradient text-white p-8 sm:p-14 lg:p-20 shadow-xl">
        <div className="relative z-10 max-w-3xl space-y-6">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/15 backdrop-blur-md border border-white/20 text-xs font-semibold text-emerald-100">
            <Sparkles className="w-3.5 h-3.5 text-emerald-300" />
            <span>Next-Generation Botanical AI Assistant</span>
          </div>

          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight leading-[1.15] font-serif">
            Understand Your Plant. <br />
            Improve Its Health. <br />
            <span className="text-emerald-200 italic font-normal">Grow Sustainably.</span>
          </h1>

          <p className="text-base sm:text-lg text-emerald-50/90 leading-relaxed max-w-2xl font-normal">
            AI-powered flower identification, computer-vision stress detection, personalized environmental compatibility matching, and eco-friendly care recommendations.
          </p>

          <div className="flex flex-wrap items-center gap-4 pt-4">
            <button
              onClick={() => setActiveTab('identify')}
              className="flex items-center gap-2.5 px-6 py-3.5 rounded-xl bg-white text-emerald-900 font-bold text-sm shadow-lg hover:bg-emerald-50 transition-all hover:scale-[1.02] active:scale-[0.98]"
            >
              <Scan className="w-4 h-4 text-emerald-600" />
              <span>Identify My Plant</span>
              <ArrowRight className="w-4 h-4 text-emerald-600 ml-1" />
            </button>

            <button
              onClick={() => setActiveTab('care')}
              className="flex items-center gap-2.5 px-6 py-3.5 rounded-xl bg-emerald-800/60 hover:bg-emerald-800/90 text-white font-semibold text-sm border border-emerald-500/40 backdrop-blur-md transition-all hover:scale-[1.02] active:scale-[0.98]"
            >
              <Droplets className="w-4 h-4 text-emerald-300" />
              <span>Explore Plant Care</span>
            </button>
          </div>

          <div className="flex items-center gap-6 pt-6 text-xs text-emerald-100/80">
            <div className="flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-300" />
              <span>102 Oxford Flower Species</span>
            </div>
            <div className="flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-300" />
              <span>Explainable AI Insights</span>
            </div>
            <div className="flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-300" />
              <span>Zero Fake Fallbacks</span>
            </div>
          </div>
        </div>

        {/* Decorative Botanical Elements */}
        <div className="absolute -right-16 -bottom-16 w-96 h-96 rounded-full bg-emerald-500/20 blur-3xl pointer-events-none" />
        <div className="absolute right-12 top-12 opacity-15 hidden lg:block">
          <Leaf className="w-80 h-80 text-white stroke-[1]" />
        </div>
      </section>

      {/* Feature Cards Grid */}
      <section className="space-y-6">
        <div className="text-center max-w-2xl mx-auto space-y-2">
          <h2 className="text-2xl sm:text-3xl font-bold text-slate-900 font-serif">
            Intelligent Botanical Architecture
          </h2>
          <p className="text-sm text-slate-600">
            More than just flower recognition — a holistic care, diagnosis, and environmental stewardship ecosystem.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {featureCards.map((feat) => {
            const Icon = feat.icon;
            return (
              <div
                key={feat.id}
                onClick={() => setActiveTab(feat.id)}
                className={`group p-6 rounded-2xl bg-gradient-to-br ${feat.color} border bg-white/70 hover:bg-white cursor-pointer shadow-sm hover:shadow-md transition-all duration-300 flex flex-col justify-between`}
              >
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="w-12 h-12 rounded-xl bg-white shadow-sm flex items-center justify-center text-emerald-700 group-hover:scale-110 transition-transform">
                      <Icon className="w-6 h-6" />
                    </div>
                    <span className="text-[11px] font-semibold text-emerald-800 bg-emerald-100/70 px-2.5 py-0.5 rounded-full">
                      {feat.tag}
                    </span>
                  </div>

                  <div>
                    <h3 className="text-lg font-bold text-slate-900 group-hover:text-emerald-700 transition-colors">
                      {feat.title}
                    </h3>
                    <p className="text-sm text-slate-600 mt-2 leading-relaxed">
                      {feat.desc}
                    </p>
                  </div>
                </div>

                <div className="mt-5 flex items-center text-xs font-bold text-emerald-700 group-hover:translate-x-1 transition-transform">
                  <span>Open Feature</span>
                  <ArrowRight className="w-3.5 h-3.5 ml-1" />
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* Workflow Showcase */}
      <section className="bg-white rounded-3xl p-8 sm:p-12 border border-emerald-100 shadow-sm space-y-8">
        <div className="text-center max-w-xl mx-auto space-y-2">
          <span className="text-xs font-bold uppercase tracking-wider text-emerald-600">
            End-to-End Plant Journey
          </span>
          <h2 className="text-2xl font-bold text-slate-900 font-serif">
            How FloraCare AI Works
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 relative">
          {[
            { step: '01', title: 'Upload & Validate', desc: 'Preprocesses image (224×224) and verifies floral/vegetation composition.' },
            { step: '02', title: 'Classify & Diagnose', desc: 'MobileNetV2 identifies the flower; computer vision detects leaf stress & disease risk.' },
            { step: '03', title: 'Smart Match', desc: 'Calculates 0–100 Health Score & environmental compatibility against real databases.' },
            { step: '04', title: 'Action & Track', desc: 'Delivers daily tasks, smart watering advice, growth journal, and eco-guidance.' }
          ].map((s, idx) => (
            <div key={s.step} className="p-5 rounded-xl bg-emerald-50/40 border border-emerald-100/80 space-y-2 relative">
              <span className="text-2xl font-black text-emerald-300 font-mono">{s.step}</span>
              <h3 className="font-bold text-slate-900 text-base">{s.title}</h3>
              <p className="text-xs text-slate-600 leading-relaxed">{s.desc}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
};
