/* eslint-disable @typescript-eslint/no-explicit-any */

import api from './api';

export interface Mistake {
  id: number;
  question_texte: string;
  reponse_utilisateur: string;
  reponse_correcte: string;
  mode_apprentissage: string;
  nb_fois_erreur: number;
  est_revu: boolean;
  date_erreur: string;
  derniere_erreur: string;
  cours_titre: string;
}

export interface MistakeStats {
  total_erreurs: number;
  erreurs_non_revues: number;
  erreurs_critiques: number;
  cours_plus_erreurs: string | null;
  mode_plus_erreurs: string | null;
}

class MistakeService {
  private baseUrl = '/mistakes';

  async saveMistake(mistake: {
    cours_id: number;
    question_id: number;
    question_texte: string;
    reponse_utilisateur: string;
    reponse_correcte: string;
    mode_apprentissage: string;
    score_obtenu?: number;
    points_possibles?: number;
  }): Promise<{ mistake_id: number }> {
    const response = await api.post(`${this.baseUrl}/save`, mistake);
    return response.data;
  }

  async saveBatchMistakes(mistakes: any[]): Promise<{ saved_count: number }> {
    const response = await api.post(`${this.baseUrl}/batch-save`, { mistakes });
    return response.data;
  }

  async getMyMistakes(cours_id?: number, mode?: string, limit: number = 30): Promise<Mistake[]> {
    const params = new URLSearchParams();
    if (cours_id) params.append('cours_id', cours_id.toString());
    if (mode) params.append('mode', mode);
    params.append('limit', limit.toString());
    
    const response = await api.get(`${this.baseUrl}/my-mistakes?${params.toString()}`);
    return response.data.mistakes;
  }

  async getMyMistakesStats(): Promise<MistakeStats> {
    const response = await api.get(`${this.baseUrl}/my-stats`);
    return response.data.stats;
  }

  async markAsRevised(erreur_id: number): Promise<boolean> {
    const response = await api.post(`${this.baseUrl}/mark-revised`, { erreur_id });
    return response.data.revised;
  }
}

export const mistakeService = new MistakeService();