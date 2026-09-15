import React, { useState, useEffect } from 'react';
import {
  Sprout,
  Scan,
  HeartPulse,
  Droplets,
  Bug,
  BarChart3,
  Globe,
  Compass,
  ArrowLeftRight,
  BookOpen,
  Menu,
  X,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';
import { api } from '../services/api';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab }) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [modelReady, setModelReady] = useState<boolean | null>(null);

  useEffect(() => {
    api.getModelStatus()
      .then((data) => setModelReady(data.available))
      .catch(() => setModelReady(false));
  }, []);

  const navItems = [
    { id: 'home', label: 'Home', icon: Sprout },
    { id: 'identify', label: 'Identify Plant', icon: Scan },
    { id: 'health', label: 'Plant Health', icon: HeartPulse },
    { id: 'care', label: 'Care Plan', icon: Droplets },
    { id: 'disease', label: 'Disease Risk', icon: Bug },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
    { id: 'sustainability', label: 'Sustainability', icon: Globe },
    { id: 'recommender', label: 'Plant Recommender', icon: Compass },
    { id: 'compare', label: 'Compare', icon: ArrowLeftRight },
    { id: 'my-plants', label: 'My Plants', icon: BookOpen },
  ];

  return (
    <header className="sticky top-0 z-50 bg-white/95 backdrop-blur-md border-b border-emerald-100 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand Logo */}
          <div
            onClick={() => setActiveTab('home')}
            className="flex items-center gap-2.5 cursor-pointer group"
          >
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-600 to-teal-800 flex items-center justify-center text-white shadow-sm group-hover:scale-105 transition-transform">
              <Sprout className="w-6 h-6" />
            </div>
            <div>
              <span className="text-xl font-bold text-slate-900 tracking-tight flex items-center gap-1.5">
                FloraCare <span className="text-emerald-600 font-extrabold text-sm px-1.5 py-0.5 rounded bg-emerald-50 border border-emerald-200">AI</span>
              </span>
              <span className="block text-[10px] text-slate-500 font-medium uppercase tracking-wider -mt-1">
                Health, Care & Sustainability
              </span>
            </div>
          </div>

          {/* Desktop Navigation Links */}
          <nav className="hidden xl:flex items-center gap-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-semibold transition-all ${
                    isActive
                      ? 'bg-emerald-600 text-white shadow-sm'
                      : 'text-slate-600 hover:text-emerald-700 hover:bg-emerald-50/70'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>

          {/* Status Badge & Mobile Hamburger */}
          <div className="flex items-center gap-3">
            <div
              title={modelReady ? 'MobileNetV2 Model Ready' : 'Oxford 102 Model training recommended'}
              className={`hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${
                modelReady
                  ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                  : 'bg-amber-50 text-amber-700 border-amber-200'
              }`}
            >
              {modelReady ? (
                <>
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                  <span>Model Online</span>
                </>
              ) : (
                <>
                  <AlertCircle className="w-3.5 h-3.5 text-amber-600" />
                  <span>Oxford 102 (Ready to train)</span>
                </>
              )}
            </div>

            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="xl:hidden p-2 rounded-lg text-slate-600 hover:bg-emerald-50 hover:text-emerald-700"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu Dropdown */}
      {mobileMenuOpen && (
        <div className="xl:hidden bg-white border-b border-emerald-100 px-4 pt-2 pb-4 space-y-1 shadow-lg">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => {
                  setActiveTab(item.id);
                  setMobileMenuOpen(false);
                }}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-semibold transition-all ${
                  isActive
                    ? 'bg-emerald-600 text-white'
                    : 'text-slate-700 hover:bg-emerald-50 hover:text-emerald-700'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </div>
      )}
    </header>
  );
};
