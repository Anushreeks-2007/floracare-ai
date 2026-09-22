import React, { useState, useRef } from 'react';
import {
  UploadCloud,
  CheckCircle2,
  AlertTriangle,
  HelpCircle,
  Activity,
  ArrowRight,
  Sparkles,
  Info,
  Layers,
  Eye,
  RefreshCw,
  BookmarkPlus
} from 'lucide-react';
import { api } from '../services/api';
import { PredictionResult, StressDetectionResult, FlowerProfile } from '../types';

interface IdentifyPageProps {
  onFlowerIdentified: (flower: FlowerProfile, pred: PredictionResult, stress: StressDetectionResult) => void;
  setActiveTab: (tab: string) => void;
}

export const IdentifyPage: React.FC<IdentifyPageProps> = ({ onFlowerIdentified, setActiveTab }) => {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [errorDetails, setErrorDetails] = useState<any>(null);

  const [prediction, setPrediction] = useState<PredictionResult | null>(null);
  const [stress, setStress] = useState<StressDetectionResult | null>(null);
  const [profile, setProfile] = useState<FlowerProfile | null>(null);
  const [savedSuccess, setSavedSuccess] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (selectedFile: File) => {
    setFile(selectedFile);
    setPreview(URL.createObjectURL(selectedFile));
    setErrorMsg(null);
    setErrorDetails(null);
    setPrediction(null);
    setStress(null);
    setProfile(null);
    setSavedSuccess(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileChange(e.dataTransfer.files[0]);
    }
  };

  const handleUploadAndAnalyze = async () => {
    if (!file) return;
    setLoading(true);
    setErrorMsg(null);
    setErrorDetails(null);

    try {
      console.log("1. ANALYZE CLICKED");
      const res = await api.predictImage(file);
      console.log("2. PREDICTION RESPONSE:", res);
      
      if (!res.is_plant) {
        setErrorMsg(res.message);
        setErrorDetails(res.details);
      } else if (res.success) {
        setPrediction(res.prediction);
        setStress(res.stress_detection);
        setProfile(res.flower_profile);
        onFlowerIdentified(res.flower_profile, res.prediction, res.stress_detection);
      }
    } catch (err: any) {
      const respData = err.response?.data?.detail || err.response?.data;
      if (respData?.error === 'model_unavailable') {
        setErrorMsg(respData.message || 'Required model/data is unavailable. Please add the trained model and dataset before using this feature.');
        setErrorDetails({ instructions: respData.instructions || 'Run: python ml_model/train.py' });
      } else {
        setErrorMsg(respData?.message || err.message || 'An error occurred during plant identification.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSaveToProfile = async () => {
    if (!profile) return;
    try {
      await api.createProfile({
        flower_id: profile.id,
        nickname: profile.common_name,
        location: 'Garden / Indoor Pot',
        notes: `Identified via FloraCare AI with ${(prediction?.confidence || 0.9 * 100).toFixed(0)}% confidence.`
      });
      setSavedSuccess(true);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8 pb-12">
      {/* Header */}
      <div className="text-center space-y-2">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-xs font-bold text-emerald-800">
          <Sparkles className="w-3.5 h-3.5 text-emerald-600" />
          <span>MobileNetV2 Vision Pipeline</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-900 font-serif">
          Identify Flower & Detect Health Stress
        </h1>
        <p className="text-sm text-slate-600 max-w-xl mx-auto">
          Upload a high-resolution photo of a flowering plant to identify the Oxford 102 species and diagnose initial visible stress symptoms.
        </p>
      </div>

      {/* Upload Box */}
      <div className="bg-white rounded-3xl p-6 sm:p-8 border border-emerald-100 shadow-sm space-y-6">
        <div
          onDragOver={(e) => e.preventDefault()}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all ${
            preview
              ? 'border-emerald-300 bg-emerald-50/20'
              : 'border-slate-300 hover:border-emerald-400 bg-slate-50/50 hover:bg-emerald-50/30'
          }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept="image/jpeg,image/png,image/webp"
            className="hidden"
            onChange={(e) => e.target.files?.[0] && handleFileChange(e.target.files[0])}
          />

          {preview ? (
            <div className="flex flex-col items-center gap-4">
              <div className="relative group">
                <img
                  src={preview}
                  alt="Upload Preview"
                  className="max-h-72 w-auto object-cover rounded-xl shadow-md border border-slate-200"
                />
                <div className="absolute inset-0 bg-black/40 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center text-white text-xs font-semibold">
                  Click to change photo
                </div>
              </div>
              <p className="text-xs text-slate-500">{file?.name} ({(file!.size / 1024 / 1024).toFixed(2)} MB)</p>
            </div>
          ) : (
            <div className="flex flex-col items-center gap-3 py-6">
              <div className="w-16 h-16 rounded-2xl bg-emerald-100/60 text-emerald-700 flex items-center justify-center shadow-inner">
                <UploadCloud className="w-8 h-8" />
              </div>
              <div>
                <p className="text-base font-bold text-slate-800">
                  Click to select or drag and drop flower image
                </p>
                <p className="text-xs text-slate-500 mt-1">
                  Supports JPEG, PNG, WEBP (Max 10 MB). 224×224 normalized.
                </p>
              </div>
            </div>
          )}
        </div>

        {file && (
          <div className="flex justify-center">
            <button
              onClick={handleUploadAndAnalyze}
              disabled={loading}
              className="flex items-center gap-2 px-8 py-3.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-sm shadow-md transition-all hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50"
            >
              {loading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Preprocessing & Identifying...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  <span>Analyze Plant & Health</span>
                </>
              )}
            </button>
          </div>
        )}
      </div>

      {/* Error / Missing Model Banner */}
      {errorMsg && (
        <div className="p-6 rounded-2xl bg-amber-50/80 border border-amber-200 text-amber-900 space-y-3 shadow-sm">
          <div className="flex items-start gap-3">
            <AlertTriangle className="w-6 h-6 text-amber-600 shrink-0 mt-0.5" />
            <div>
              <h3 className="font-bold text-base">Model or Data Notice</h3>
              <p className="text-sm mt-1 leading-relaxed">{errorMsg}</p>
              {errorDetails?.instructions && (
                <div className="mt-3 p-3 bg-amber-100/70 rounded-lg text-xs font-mono text-amber-950 border border-amber-300/60">
                  {errorDetails.instructions}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Prediction Results Display */}
      {prediction && (
        <div className="space-y-8 animate-in fade-in duration-500">
          {/* Main Identification Card */}
          <div className="bg-white rounded-3xl p-6 sm:p-8 border border-emerald-100 shadow-sm space-y-6">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-6 border-b border-slate-100">
              <div className="flex items-center gap-4">
                <span className="text-5xl p-2 bg-emerald-50 rounded-2xl border border-emerald-100">
                  {profile?.emoji || '🌸'}
                </span>
                <div>
                  <div className="flex items-center gap-2">
                    <h2 className="text-2xl sm:text-3xl font-bold text-slate-900 font-serif">
                      {prediction.flower_name}
                    </h2>
                    <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800">
                      {(prediction.confidence * 100).toFixed(1)}% Match
                    </span>
                  </div>
                  <p className="text-sm italic text-slate-500 font-serif mt-0.5">
                    {profile?.scientific_name || prediction.flower_name || 'Unknown Flower'} • Class #{prediction.flower_id}
                  </p>
                </div>
              </div>

              <button
                onClick={handleSaveToProfile}
                disabled={savedSuccess}
                className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold border transition-all ${
                  savedSuccess
                    ? 'bg-emerald-50 border-emerald-300 text-emerald-800'
                    : 'bg-white border-slate-200 hover:border-emerald-400 text-slate-700 hover:text-emerald-800'
                }`}
              >
                <BookmarkPlus className="w-4 h-4" />
                <span>{savedSuccess ? 'Saved to My Plants!' : 'Save Plant Profile'}</span>
              </button>
            </div>

            {/* Top 3 Predictions */}
            <div>
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-3">
                Top 3 Species Predictions
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                {prediction.top_predictions.map((c,i) => (
                  <div key={`${c.name}-${i}`} className="p-3.5 rounded-xl bg-slate-50 border border-slate-200/80 space-y-2">
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-semibold text-slate-800 flex items-center gap-1.5">
                        <span>{c.emoji}</span>
                        <span>{c.name}</span>
                      </span>
                      <span className="font-bold text-emerald-700">{(c.confidence * 100).toFixed(1)}%</span>
                    </div>
                    <div className="w-full bg-slate-200 h-1.5 rounded-full overflow-hidden">
                      <div
                        className="bg-emerald-600 h-full rounded-full transition-all"
                        style={{ width: `${Math.min(100, c.confidence * 100)}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Explainable AI (XAI) Box */}
            <div className="p-5 rounded-2xl bg-emerald-50/60 border border-emerald-100 space-y-2">
              <div className="flex items-center gap-2 text-emerald-900 font-bold text-sm">
                <Eye className="w-4 h-4 text-emerald-700" />
                <span>Why did the AI choose this flower? (Explainable AI)</span>
              </div>
              <p className="text-xs sm:text-sm text-emerald-950/85 leading-relaxed">
                {prediction.ai_explanation}
              </p>
              <div className="pt-2 flex flex-wrap gap-2 text-[11px] text-emerald-800 font-medium">
                <span className="px-2 py-1 bg-white rounded-md border border-emerald-200">
                  Petal Pattern: {profile.visual_features.petal_shape}
                </span>
                <span className="px-2 py-1 bg-white rounded-md border border-emerald-200">
                  Arrangement: {profile.visual_features.petal_arrangement}
                </span>
                <span className="px-2 py-1 bg-white rounded-md border border-emerald-200">
                  Green Foliage: {(prediction.visual_features.green_fraction * 100).toFixed(0)}%
                </span>
              </div>
            </div>
          </div>

          {/* Plant Stress Detection Box */}
          {stress && (
            <div className={`p-6 rounded-3xl border shadow-sm space-y-4 ${
              stress.stress_detected
                ? 'bg-amber-50/50 border-amber-200 text-amber-950'
                : 'bg-emerald-50/50 border-emerald-200 text-emerald-950'
            }`}>
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${
                    stress.stress_detected ? 'bg-amber-100 text-amber-700' : 'bg-emerald-100 text-emerald-700'
                  }`}>
                    <Activity className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="font-bold text-base">
                      {stress.stress_detected ? 'Possible Stress Detected' : 'No Immediate Stress Detected'}
                    </h3>
                    <p className="text-xs text-slate-600">
                      Confidence: {stress.overall_confidence} • Automated CV Analysis
                    </p>
                  </div>
                </div>

                <span className={`px-2.5 py-1 rounded-full text-xs font-bold ${
                  stress.stress_detected ? 'bg-amber-200/70 text-amber-900' : 'bg-emerald-200/70 text-emerald-900'
                }`}>
                  {stress.stress_detected ? 'Attention Needed' : 'Vibrant Foliage'}
                </span>
              </div>

              {stress.possible_issues?.length > 0 && (
                <div className="mt-4">
                  <h4 className="font-semibold text-red-700">Possible Issues</h4>
                  <ul className="mt-2 space-y-2 list-disc list-inside">
                    {stress.possible_issues?.map((iss, i) => (
                      <li key={i}>
                        {typeof iss === 'string' ? iss : (
                          <div>
                            <p className="font-medium">{iss.label}</p>
                            <p className="text-sm">{iss.description}</p>
                            {iss.recommended_action && (
                              <p className="text-sm mt-1">
                                <strong>Action:</strong> {iss.recommended_action}
                              </p>
                            )}
                          </div>
                        )}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {stress.recommended_actions?.length > 0 && (
                <div className="p-3 bg-white rounded-xl border border-slate-200/80 text-xs text-slate-700 space-y-1">
                  <span className="font-bold text-slate-900">Recommended Action:</span>
                  <p>{stress.recommended_actions?.join(' ')}</p>
                </div>
              )}

              <p className="text-[11px] text-slate-500 italic">
                {stress.disclaimer}
              </p>
            </div>
          )}

          {/* Next Steps CTA */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <button
              onClick={() => setActiveTab('health')}
              className="flex items-center justify-between p-5 rounded-2xl bg-gradient-to-r from-emerald-600 to-teal-700 text-white font-bold text-sm shadow-md hover:shadow-lg hover:scale-[1.01] transition-all"
            >
              <div>
                <span className="block text-xs font-medium text-emerald-100">Step 2</span>
                <span className="text-base">Calculate Plant Health Score</span>
              </div>
              <ArrowRight className="w-5 h-5 text-emerald-200" />
            </button>

            <button
              onClick={() => setActiveTab('care')}
              className="flex items-center justify-between p-5 rounded-2xl bg-white border border-emerald-200 text-slate-800 hover:text-emerald-700 font-bold text-sm shadow-sm hover:shadow-md hover:scale-[1.01] transition-all"
            >
              <div>
                <span className="block text-xs font-medium text-slate-500">Step 3</span>
                <span className="text-base">Explore Complete Care Plan</span>
              </div>
              <ArrowRight className="w-5 h-5 text-emerald-600" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
