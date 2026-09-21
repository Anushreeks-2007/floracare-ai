import axios from 'axios';
import {
  FlowerProfile,
  HealthScoreResult,
  CompatibilityResult,
  ActionPlanResult,
  WateringAdviceResult,
  SustainabilityResult,
  WhatIfResult,
  PlantProfile
} from '../types';

const API_BASE = 'https://floracare-ai-ojuq.onrender.com/';

export const api = {
  // Model Status & Evaluation
  getModelStatus: async () => {
    const res = await axios.get(`${API_BASE}/model/status`);
    return res.data;
  },

  getModelEvaluation: async () => {
    const res = await axios.get(`${API_BASE}/model/evaluation`);
    return res.data;
  },

  // Identify / Predict
  predictImage: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await axios.post(`${API_BASE}/predict`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return res.data;
  },

  // Flowers Catalog
  getFlowers: async (params?: { q?: string; climate?: string; difficulty?: string }) => {
    const res = await axios.get(`${API_BASE}/flowers`, { params });
    return res.data;
  },

  getFlowerDetail: async (flowerId: number): Promise<FlowerProfile> => {
    const res = await axios.get(`${API_BASE}/flowers/${flowerId}`);
    return res.data;
  },

  compareFlowers: async (id1: number, id2: number) => {
    const res = await axios.get(`${API_BASE}/flowers/compare`, {
      params: { id1, id2 }
    });
    return res.data;
  },

  recommendFlowers: async (envData: any) => {
    const res = await axios.post(`${API_BASE}/flowers/recommender`, envData);
    return res.data;
  },

  // Plant Care & Scoring
  getHealthScore: async (data: any): Promise<HealthScoreResult> => {
    const res = await axios.post(`${API_BASE}/care/health-score`, data);
    return res.data;
  },

  getCompatibility: async (data: any): Promise<CompatibilityResult> => {
    const res = await axios.post(`${API_BASE}/care/compatibility`, data);
    return res.data;
  },

  getActionPlan: async (data: any): Promise<ActionPlanResult> => {
    const res = await axios.post(`${API_BASE}/care/action-plan`, data);
    return res.data;
  },

  getWateringAdvice: async (data: any): Promise<WateringAdviceResult> => {
    const res = await axios.post(`${API_BASE}/care/watering-advisor`, data);
    return res.data;
  },

  getSustainabilityScore: async (data: any): Promise<SustainabilityResult> => {
    const res = await axios.post(`${API_BASE}/care/sustainability`, data);
    return res.data;
  },

  runWhatIfSimulation: async (data: any): Promise<WhatIfResult> => {
    const res = await axios.post(`${API_BASE}/care/what-if`, data);
    return res.data;
  },

  // Analytics & Data Mining
  getAnalyticsSummary: async () => {
    const res = await axios.get(`${API_BASE}/analytics/summary`);
    return res.data;
  },

  getDataMiningInsights: async () => {
    const res = await axios.get(`${API_BASE}/analytics/mining`);
    return res.data;
  },

  // Profiles & Journal
  getProfiles: async (): Promise<PlantProfile[]> => {
    const res = await axios.get(`${API_BASE}/profiles`);
    return res.data;
  },

  createProfile: async (data: any): Promise<PlantProfile> => {
    const res = await axios.post(`${API_BASE}/profiles`, data);
    return res.data;
  },

  deleteProfile: async (profileId: string) => {
    const res = await axios.delete(`${API_BASE}/profiles/${profileId}`);
    return res.data;
  },

  addJournalEntry: async (profileId: string, formData: FormData) => {
    const res = await axios.post(`${API_BASE}/journal/${profileId}/entry`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return res.data;
  },

  getJournalComparison: async (profileId: string) => {
    const res = await axios.get(`${API_BASE}/journal/${profileId}/compare`);
    return res.data;
  }
};
