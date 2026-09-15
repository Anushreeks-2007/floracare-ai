import React, { useState, useEffect } from 'react';
import {
  BookOpen,
  Calendar,
  Plus,
  Trash2,
  Camera,
  TrendingUp,
  Activity,
  Sparkles,
  Layers,
  Clock,
  CheckCircle2,
  Image as ImageIcon
} from 'lucide-react';
import { api } from '../services/api';
import { PlantProfile, FlowerProfile } from '../types';

interface MyPlantsPageProps {
  allFlowers: FlowerProfile[];
  setActiveTab: (tab: string) => void;
  onSelectFlower: (flower: FlowerProfile) => void;
}

export const MyPlantsPage: React.FC<MyPlantsPageProps> = ({ allFlowers, setActiveTab, onSelectFlower }) => {
  const [profiles, setProfiles] = useState<PlantProfile[]>([]);
  const [selectedProfile, setSelectedProfile] = useState<PlantProfile | null>(null);
  const [comparison, setComparison] = useState<any>(null);

  // New Profile modal/form
  const [showAddModal, setShowAddModal] = useState(false);
  const [newFlowerId, setNewFlowerId] = useState<number>(allFlowers[0]?.id || 1);
  const [newNickname, setNewNickname] = useState('');
  const [newLocation, setNewLocation] = useState('Balcony Window');
  const [newNotes, setNewNotes] = useState('Potted in organic loam');

  // New Journal Entry form
  const [showEntryModal, setShowEntryModal] = useState(false);
  const [entryLabel, setEntryLabel] = useState('Day 14 Checkup');
  const [entryNotes, setEntryNotes] = useState('New shoots and leaves appearing.');
  const [entryFile, setEntryFile] = useState<File | null>(null);

  const loadProfiles = async () => {
    try {
      const list = await api.getProfiles();
      setProfiles(list);
      if (list.length > 0 && !selectedProfile) {
        setSelectedProfile(list[0]);
      }
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    loadProfiles();
  }, []);

  useEffect(() => {
    if (selectedProfile) {
      api.getJournalComparison(selectedProfile.id)
        .then(setComparison)
        .catch(console.error);
    }
  }, [selectedProfile]);

  const handleCreateProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const created = await api.createProfile({
        flower_id: newFlowerId,
        nickname: newNickname || undefined,
        location: newLocation,
        notes: newNotes
      });
      setShowAddModal(false);
      setNewNickname('');
      await loadProfiles();
      setSelectedProfile(created);
    } catch (err) {
      console.error(err);
    }
  };

  const handleDeleteProfile = async (id: string) => {
    if (!confirm('Are you sure you want to delete this plant profile?')) return;
    try {
      await api.deleteProfile(id);
      setSelectedProfile(null);
      await loadProfiles();
    } catch (err) {
      console.error(err);
    }
  };

  const handleAddJournalEntry = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedProfile) return;

    const fd = new FormData();
    fd.append('day_label', entryLabel);
    fd.append('notes', entryNotes);
    if (entryFile) {
      fd.append('file', entryFile);
    }

    try {
      await api.addJournalEntry(selectedProfile.id, fd);
      setShowEntryModal(false);
      setEntryFile(null);
      await loadProfiles();
      const updated = await api.getProfiles();
      const match = updated.find((p) => p.id === selectedProfile.id);
      if (match) setSelectedProfile(match);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8 pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-white p-6 rounded-3xl border border-emerald-100 shadow-sm">
        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-xs font-bold text-emerald-800">
            <BookOpen className="w-3.5 h-3.5 text-emerald-600" />
            <span>Personal Botanical Garden</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 font-serif mt-1">
            My Plants, Care Calendar & Growth Journal
          </h1>
          <p className="text-xs text-slate-500">
            Maintain plant records, track weekly care schedules, and monitor computer-vision growth progression over time.
          </p>
        </div>

        <button
          onClick={() => setShowAddModal(true)}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold shadow-sm transition-all"
        >
          <Plus className="w-4 h-4" />
          <span>Add New Plant</span>
        </button>
      </div>

      {profiles.length === 0 ? (
        <div className="bg-white rounded-3xl p-12 text-center border border-emerald-100 shadow-sm space-y-4">
          <div className="w-16 h-16 rounded-2xl bg-emerald-50 text-emerald-600 flex items-center justify-center mx-auto">
            <BookOpen className="w-8 h-8" />
          </div>
          <div className="space-y-1">
            <h3 className="text-lg font-bold text-slate-800">No Plant Profiles Saved Yet</h3>
            <p className="text-xs text-slate-500 max-w-sm mx-auto">
              Identify a flower using the AI camera or add one manually to begin tracking growth and care schedules.
            </p>
          </div>
          <button
            onClick={() => setShowAddModal(true)}
            className="px-5 py-2.5 rounded-xl bg-emerald-600 text-white font-bold text-xs"
          >
            Create Your First Plant Profile
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column: Plant Profiles List */}
          <div className="lg:col-span-1 space-y-4">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">
              Saved Plant Profiles ({profiles.length})
            </h3>

            <div className="space-y-3">
              {profiles.map((p) => {
                const isSelected = selectedProfile?.id === p.id;
                return (
                  <div
                    key={p.id}
                    onClick={() => setSelectedProfile(p)}
                    className={`p-4 rounded-2xl border cursor-pointer transition-all flex items-center justify-between ${
                      isSelected
                        ? 'bg-emerald-50 border-emerald-300 shadow-sm'
                        : 'bg-white border-slate-200/80 hover:border-emerald-200'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-3xl p-1.5 bg-white rounded-xl shadow-xs border border-slate-100">
                        {p.emoji}
                      </span>
                      <div>
                        <h4 className="font-bold text-sm text-slate-900">{p.nickname}</h4>
                        <p className="text-[11px] text-slate-500">{p.flower_name} • {p.location}</p>
                      </div>
                    </div>

                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteProfile(p.id);
                      }}
                      className="p-1.5 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Right 2 Columns: Selected Plant Detail + Growth Journal */}
          {selectedProfile && (
            <div className="lg:col-span-2 space-y-6">
              {/* Profile Summary Card */}
              <div className="bg-white rounded-3xl p-6 border border-emerald-100 shadow-sm space-y-4">
                <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                  <div className="flex items-center gap-3">
                    <span className="text-4xl">{selectedProfile.emoji}</span>
                    <div>
                      <h3 className="text-xl font-bold text-slate-900 font-serif">
                        {selectedProfile.nickname}
                      </h3>
                      <p className="text-xs text-slate-500">
                        {selectedProfile.flower_name} ({selectedProfile.scientific_name}) • Added on {selectedProfile.created_at}
                      </p>
                    </div>
                  </div>

                  <button
                    onClick={() => {
                      const found = allFlowers.find((f) => f.id === selectedProfile.flower_id);
                      if (found) {
                        onSelectFlower(found);
                        setActiveTab('care');
                      }
                    }}
                    className="px-3 py-1.5 rounded-xl bg-emerald-50 text-emerald-800 text-xs font-bold border border-emerald-200 hover:bg-emerald-600 hover:text-white transition-colors"
                  >
                    View Care Guide
                  </button>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                  <div className="p-2.5 bg-slate-50 rounded-xl">
                    <span className="text-slate-400 block text-[10px]">Location:</span>
                    <span className="font-semibold text-slate-800">{selectedProfile.location}</span>
                  </div>
                  <div className="p-2.5 bg-slate-50 rounded-xl">
                    <span className="text-slate-400 block text-[10px]">Light Req:</span>
                    <span className="font-semibold text-slate-800 capitalize">{selectedProfile.sunlight}</span>
                  </div>
                  <div className="p-2.5 bg-slate-50 rounded-xl">
                    <span className="text-slate-400 block text-[10px]">Water Frequency:</span>
                    <span className="font-semibold text-slate-800">{selectedProfile.watering_freq}</span>
                  </div>
                  <div className="p-2.5 bg-slate-50 rounded-xl">
                    <span className="text-slate-400 block text-[10px]">Difficulty:</span>
                    <span className="font-semibold text-slate-800 capitalize">{selectedProfile.care_difficulty}</span>
                  </div>
                </div>
              </div>

              {/* Unique Feature 11: Weekly Care Calendar Planner */}
              <div className="bg-white rounded-3xl p-6 border border-emerald-100 shadow-sm space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="font-bold text-base text-slate-900 flex items-center gap-2">
                    <Calendar className="w-4 h-4 text-emerald-600" />
                    <span>Weekly Care Planner</span>
                  </h3>
                  <span className="text-xs text-slate-500">Customizable schedule</span>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-2 text-center text-xs">
                  {[
                    { day: 'Mon', task: 'Soil moisture check', icon: '🌱' },
                    { day: 'Tue', task: 'Rest day', icon: '☀️' },
                    { day: 'Wed', task: 'Watering & misting', icon: '💧' },
                    { day: 'Thu', task: 'Foliage dust wipe', icon: '🍃' },
                    { day: 'Fri', task: 'Leaf pest inspection', icon: '🔍' },
                    { day: 'Sat', task: 'Turn pot for light', icon: '🔄' },
                    { day: 'Sun', task: 'Growth observation', icon: '📈' },
                  ].map((d) => (
                    <div key={d.day} className="p-2.5 rounded-xl bg-slate-50 border border-slate-200/80 space-y-1">
                      <span className="font-extrabold text-slate-800 block">{d.day}</span>
                      <span className="text-base">{d.icon}</span>
                      <span className="text-[10px] text-slate-500 block leading-tight">{d.task}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Unique Feature 13: Growth Journal & CV Comparison */}
              <div className="bg-white rounded-3xl p-6 border border-emerald-100 shadow-sm space-y-5">
                <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                  <div className="flex items-center gap-2">
                    <TrendingUp className="w-5 h-5 text-emerald-600" />
                    <h3 className="font-bold text-base text-slate-900">
                      Growth Journal Timeline & CV Comparison
                    </h3>
                  </div>

                  <button
                    onClick={() => setShowEntryModal(true)}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-emerald-600 text-white text-xs font-bold"
                  >
                    <Plus className="w-3.5 h-3.5" />
                    <span>New Observation</span>
                  </button>
                </div>

                {/* CV Growth Comparison Highlight Banner */}
                {comparison?.has_comparison && (
                  <div className="p-4 rounded-2xl bg-emerald-50 border border-emerald-200 space-y-2">
                    <div className="flex items-center justify-between text-xs font-bold text-emerald-900">
                      <span>Timeline Computer-Vision Analysis:</span>
                      <span>{comparison.start_date} → {comparison.latest_date}</span>
                    </div>
                    <div className="flex items-center gap-4 text-xs">
                      <div>
                        <span className="text-slate-500 block text-[10px]">Foliage Density:</span>
                        <span className="font-bold text-emerald-700 font-mono">{comparison.foliage_growth_change}</span>
                      </div>
                      <div>
                        <span className="text-slate-500 block text-[10px]">Green Vitality Index:</span>
                        <span className="font-bold text-emerald-700 font-mono">{comparison.chlorophyll_vitality_change}</span>
                      </div>
                    </div>
                    <p className="text-xs text-emerald-950 font-medium">
                      “{comparison.trend_summary}”
                    </p>
                  </div>
                )}

                {/* Journal Entries List */}
                <div className="space-y-3">
                  {selectedProfile.journal_entries.length === 0 ? (
                    <p className="text-xs text-slate-400 text-center py-4 italic">
                      No journal entries yet. Click "New Observation" to log your first photo and notes.
                    </p>
                  ) : (
                    selectedProfile.journal_entries.map((entry) => (
                      <div key={entry.id} className="p-4 rounded-2xl bg-slate-50 border border-slate-200/80 flex items-start gap-4">
                        {entry.image_url ? (
                          <img
                            src={entry.image_url}
                            alt="Journal plant"
                            className="w-16 h-16 object-cover rounded-xl border border-slate-200"
                          />
                        ) : (
                          <div className="w-16 h-16 rounded-xl bg-slate-200 flex items-center justify-center text-slate-400">
                            <ImageIcon className="w-6 h-6" />
                          </div>
                        )}
                        <div className="space-y-1 flex-1 text-xs">
                          <div className="flex items-center justify-between">
                            <span className="font-bold text-slate-900">{entry.day_label}</span>
                            <span className="text-[10px] text-slate-400">{entry.date}</span>
                          </div>
                          <p className="text-slate-600">{entry.notes}</p>
                          {entry.cv_metrics && (
                            <span className="inline-block px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 text-[10px] font-semibold">
                              Canopy Coverage: {entry.cv_metrics.coverage_pct}% • Vitality: {entry.cv_metrics.vitality}
                            </span>
                          )}
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Add Profile Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl max-w-md w-full p-6 space-y-4 shadow-2xl">
            <h3 className="font-bold text-lg text-slate-900 font-serif">Add Plant to My Garden</h3>
            <form onSubmit={handleCreateProfile} className="space-y-3 text-xs">
              <div>
                <label className="font-bold text-slate-700 block mb-1">Select Flower Species:</label>
                <select
                  value={newFlowerId}
                  onChange={(e) => setNewFlowerId(Number(e.target.value))}
                  className="w-full p-2.5 bg-slate-50 border rounded-xl"
                >
                  {allFlowers.map((f) => (
                    <option key={f.id} value={f.id}>{f.emoji} {f.common_name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="font-bold text-slate-700 block mb-1">Nickname:</label>
                <input
                  type="text"
                  placeholder="e.g. My Patio Rose"
                  value={newNickname}
                  onChange={(e) => setNewNickname(e.target.value)}
                  className="w-full p-2.5 bg-slate-50 border rounded-xl"
                />
              </div>
              <div>
                <label className="font-bold text-slate-700 block mb-1">Location:</label>
                <input
                  type="text"
                  placeholder="e.g. Living Room Window"
                  value={newLocation}
                  onChange={(e) => setNewLocation(e.target.value)}
                  className="w-full p-2.5 bg-slate-50 border rounded-xl"
                />
              </div>
              <div>
                <label className="font-bold text-slate-700 block mb-1">Notes:</label>
                <textarea
                  value={newNotes}
                  onChange={(e) => setNewNotes(e.target.value)}
                  className="w-full p-2.5 bg-slate-50 border rounded-xl h-16"
                />
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 rounded-xl border text-slate-600 font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl bg-emerald-600 text-white font-bold"
                >
                  Save Plant
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Add Journal Entry Modal */}
      {showEntryModal && (
        <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl max-w-md w-full p-6 space-y-4 shadow-2xl">
            <h3 className="font-bold text-lg text-slate-900 font-serif">New Journal Observation</h3>
            <form onSubmit={handleAddJournalEntry} className="space-y-3 text-xs">
              <div>
                <label className="font-bold text-slate-700 block mb-1">Observation Label:</label>
                <input
                  type="text"
                  value={entryLabel}
                  onChange={(e) => setEntryLabel(e.target.value)}
                  className="w-full p-2.5 bg-slate-50 border rounded-xl"
                />
              </div>
              <div>
                <label className="font-bold text-slate-700 block mb-1">Growth Notes:</label>
                <textarea
                  value={entryNotes}
                  onChange={(e) => setEntryNotes(e.target.value)}
                  className="w-full p-2.5 bg-slate-50 border rounded-xl h-20"
                />
              </div>
              <div>
                <label className="font-bold text-slate-700 block mb-1">Upload Photo (Optional):</label>
                <input
                  type="file"
                  accept="image/*"
                  onChange={(e) => e.target.files?.[0] && setEntryFile(e.target.files[0])}
                  className="w-full p-2 bg-slate-50 border rounded-xl"
                />
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowEntryModal(false)}
                  className="px-4 py-2 rounded-xl border text-slate-600 font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl bg-emerald-600 text-white font-bold"
                >
                  Add Entry
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
