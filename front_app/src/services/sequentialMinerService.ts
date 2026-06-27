/* eslint-disable @typescript-eslint/no-explicit-any */

import api from './api';

export interface RiskAnalysis {
  user_id: number;
  user_email?: string;
  risk_score: number;
  risk_level: 'Élevé' | 'Modéré' | 'Faible';
  risk_factors: string[];
  actions_analyzed: number;
  timestamp: string;
}

export interface Rule {
  antecedent: string[];
  consequent: string[];
  support: number;
  confidence: number;
  lift: number;
}

class SequentialMinerService {
  private baseUrl = '/sequential';

  async getStatus(): Promise<any> {
    const response = await api.get(`${this.baseUrl}/status`);
    return response.data;
  }

  async getPatterns(limit: number = 50): Promise<any> {
    const response = await api.get(`${this.baseUrl}/patterns?limit=${limit}`);
    return response.data;
  }

  async getRules(limit: number = 50, minConfidence?: number): Promise<any> {
    let url = `${this.baseUrl}/rules?limit=${limit}`;
    if (minConfidence) url += `&min_confidence=${minConfidence}`;
    const response = await api.get(url);
    return response.data;
  }

  async analyzeUserRisk(userActions: string[], threshold: number = 0.6): Promise<RiskAnalysis> {
    const response = await api.post(`${this.baseUrl}/analyze`, {
      user_actions: userActions,
      threshold: threshold
    });
    return response.data;
  }

  async getUserRiskHistory(userId: number): Promise<any> {
    const response = await api.get(`${this.baseUrl}/user/${userId}/risk`);
    return response.data;
  }

  async trainModel(useSampleData: boolean = true): Promise<any> {
    const response = await api.post(`${this.baseUrl}/train?use_sample_data=${useSampleData}`);
    return response.data;
  }

  async simulate(nUsers: number = 10, nActions: number = 30): Promise<any> {
    const response = await api.post(`${this.baseUrl}/simulate?n_users=${nUsers}&n_actions=${nActions}`);
    return response.data;
  }

  async saveModel(): Promise<any> {
    const response = await api.post(`${this.baseUrl}/save`);
    return response.data;
  }
}

export const sequentialMinerService = new SequentialMinerService();