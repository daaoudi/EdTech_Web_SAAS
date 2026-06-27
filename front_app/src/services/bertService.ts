/* eslint-disable @typescript-eslint/no-explicit-any */

import api from './api';

export interface BertQuizResponse {
  cours_id: string;
  cours_titre: string;
  questions: Array<{
    question: string;
    options: Record<string, string>;
    correct_answer: string;
    explanation: string;
    difficulte: string;
    points: number;
    score: number;
  }>;
  generated_by: string;
}

export interface BertRecommendationResponse {
  user_id: number;
  questions_count: number;
  seuil: number;
  recommendations: Array<{
    cours_id: string;
    cours_titre: string;
    score: number;
    description: string;
    direct_match: boolean;
    nb_erreurs: number;
  }>;
  generated_by: string;
}

export interface BertStatusResponse {
  loaded: boolean;
  cours_count: number;
  questions_count: number;
  model: string;
}

class BertService {
  private baseUrl = '/bert';

  async getStatus(): Promise<BertStatusResponse> {
    try {
      const response = await api.get(`${this.baseUrl}/status`);
      return response.data;
    } catch (error) {
      console.error('Erreur status BERT:', error);
      return { loaded: false, cours_count: 0, questions_count: 0, model: '' };
    }
  }

  async generateQuiz(courseId: string, n: number = 5, difficulte?: string): Promise<BertQuizResponse | null> {
    try {
      let url = `${this.baseUrl}/quiz/${courseId}?n=${n}`;
      if (difficulte) url += `&difficulte=${difficulte}`;
      
      const response = await api.get(url);
      
      
      if (response.data && response.data.questions) {
        response.data.questions = response.data.questions.map((q: any) => {
          
          if (!q.options || Object.keys(q.options).length === 0) {
            q.options = {
              A: "Réponse A",
              B: "Réponse B",
              C: "Réponse C", 
              D: "Réponse D"
            };
          }
          return q;
        });
      }
      
      return response.data;
    } catch (error) {
      console.error('Erreur génération quiz BERT:', error);
      return null;
    }
  }

  async recommendCourses(
    questionsEchouees: string[], 
    seuil: number = 0.5, 
    topN: number = 5
  ): Promise<BertRecommendationResponse | null> {
    try {
      const response = await api.post(`${this.baseUrl}/recommend`, {
        questions_echouees: questionsEchouees,
        seuil: seuil,
        top_n: topN
      });
      return response.data;
    } catch (error) {
      console.error('Erreur recommandation BERT:', error);
      return null;
    }
  }

  async analyzeMyLearning(): Promise<any> {
    try {
      const response = await api.get(`${this.baseUrl}/analyze`);
      return response.data;
    } catch (error) {
      console.error('Erreur analyse BERT:', error);
      return null;
    }
  }

  async analyzeUser(userId: number): Promise<any> {
    try {
      const response = await api.post(`${this.baseUrl}/analyze/${userId}`);
      return response.data;
    } catch (error) {
      console.error('Erreur analyse utilisateur BERT:', error);
      return null;
    }
  }
}

export const bertQuizService = new BertService();
export const bertRecommendationService = bertQuizService;