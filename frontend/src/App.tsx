import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { Footer } from './components/Footer';
import { HomePage } from './pages/HomePage';
import { IdentifyPage } from './pages/IdentifyPage';
import { HealthAssessmentPage } from './pages/HealthAssessmentPage';
import { CarePlanPage } from './pages/CarePlanPage';
import { DiseaseRiskPage } from './pages/DiseaseRiskPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { SustainabilityPage } from './pages/SustainabilityPage';
import { RecommenderPage } from './pages/RecommenderPage';
import { ComparePage } from './pages/ComparePage';
import { MyPlantsPage } from './pages/MyPlantsPage';
import { api } from './services/api';
import { FlowerProfile, PredictionResult, StressDetectionResult } from './types';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('home');
  const [allFlowers, setAllFlowers] = useState<FlowerProfile[]>([]);
  const [currentFlower, setCurrentFlower] = useState<FlowerProfile | null>(null);
  const [predictionResult, setPredictionResult] = useState<PredictionResult | null>(null);
  const [stressResult, setStressResult] = useState<StressDetectionResult | null>(null);

  useEffect(() => {
    // Preload complete flowers catalog
    api.getFlowers()
      .then(async (res) => {
        if (res.results && res.results.length > 0) {
          // Fetch full detailed records
          const firstDetail = await api.getFlowerDetail(res.results[0].id);
          setCurrentFlower(firstDetail);

          // Preload list
          const details = await Promise.all(
            res.results.slice(0, 102).map((r: any) => api.getFlowerDetail(r.id))
          );
          setAllFlowers(details);
        }
      })
      .catch(console.error);
  }, []);

  const handleFlowerIdentified = (
    flower: FlowerProfile,
    pred: PredictionResult,
    stress: StressDetectionResult
  ) => {
    setCurrentFlower(flower);
    setPredictionResult(pred);
    setStressResult(stress);
  };

  const renderActivePage = () => {
    switch (activeTab) {
      case 'home':
        return <HomePage setActiveTab={setActiveTab} />;
      case 'identify':
        return (
          <IdentifyPage
            onFlowerIdentified={handleFlowerIdentified}
            setActiveTab={setActiveTab}
          />
        );
      case 'health':
        return (
          <HealthAssessmentPage
            currentFlower={currentFlower}
            allFlowers={allFlowers}
            onSelectFlower={setCurrentFlower}
            setActiveTab={setActiveTab}
          />
        );
      case 'care':
        return (
          <CarePlanPage
            currentFlower={currentFlower}
            allFlowers={allFlowers}
            onSelectFlower={setCurrentFlower}
          />
        );
      case 'disease':
        return (
          <DiseaseRiskPage
            currentFlower={currentFlower}
            allFlowers={allFlowers}
            stressResult={stressResult}
            onSelectFlower={setCurrentFlower}
          />
        );
      case 'analytics':
        return <AnalyticsPage />;
      case 'sustainability':
        return (
          <SustainabilityPage
            currentFlower={currentFlower}
            allFlowers={allFlowers}
            onSelectFlower={setCurrentFlower}
          />
        );
      case 'recommender':
        return (
          <RecommenderPage
            onSelectFlower={setCurrentFlower}
            setActiveTab={setActiveTab}
          />
        );
      case 'compare':
        return <ComparePage allFlowers={allFlowers} />;
      case 'my-plants':
        return (
          <MyPlantsPage
            allFlowers={allFlowers}
            setActiveTab={setActiveTab}
            onSelectFlower={setCurrentFlower}
          />
        );
      default:
        return <HomePage setActiveTab={setActiveTab} />;
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#f7faf7]">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 pt-8">
        {renderActivePage()}
      </main>
      <Footer />
    </div>
  );
};
