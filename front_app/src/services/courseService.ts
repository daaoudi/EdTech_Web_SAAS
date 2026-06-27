/* eslint-disable @typescript-eslint/no-explicit-any */

import api from './api';

export interface Course {
  id: number;
  titre: string;
  description: string;
  difficulte: string;
  contenu?: string;
  duree?: number;
  est_actif?: boolean;
  tags?: string[];
  slug?: string;
  url_audio?: string;
  url_video?: string;
  ordre_affichage?: number;
}

export interface UserProgress {
  cours_complets: number;
  score_moyen: number;
  temps_total: number;
  progression_niveau: number;
  stats_par_mode: {
    texte: { nb_cours: number; score_moyen: number };
    audio: { nb_cours: number; score_moyen: number };
    video: { nb_cours: number; score_moyen: number };
  };
}

export const courseService = {
  getAllCourses: async (): Promise<Course[]> => {
    try {
      const response = await api.get('/courses');
      console.log('📚 Cours chargés depuis API:', response.data.length);
      
      
      const courses = response.data
        .filter((course: any) => course.est_actif !== false) 
        .map((course: any) => ({
          id: course.id,
          titre: course.titre,
          description: course.description || 'Aucune description disponible',
          difficulte: course.difficulte || 'débutant',
          contenu: course.contenu_texte || '',
          duree: course.duree_estimee || 0,
          est_actif: course.est_actif,
          tags: course.tags || [],
          slug: course.slug,
          url_audio: course.url_audio,
          url_video: course.url_video,
          ordre_affichage: course.ordre_affichage
        }));
      
      return courses;
    } catch (error) {
      console.error('Erreur chargement cours:', error);
      throw error;
    }
  },

  getCourseById: async (id: number): Promise<Course> => {
    try {
      const response = await api.get(`/courses/${id}`);
      const course = response.data;
      
      return {
        id: course.id,
        titre: course.titre,
        description: course.description || 'Aucune description disponible',
        difficulte: course.difficulte || 'débutant',
        contenu: course.contenu_texte || '',
        duree: course.duree_estimee || 0,
        est_actif: course.est_actif,
        tags: course.tags || [],
        slug: course.slug,
        url_audio: course.url_audio,
        url_video: course.url_video,
        ordre_affichage: course.ordre_affichage
      };
    } catch (error) {
      console.error(`Erreur chargement cours ${id}:`, error);
      throw error;
    }
  },

  getUserProgress: async (): Promise<UserProgress> => {
    try {
      const response = await api.get('/users/me/progress');
      console.log('📊 Données de progression brutes:', response.data);
      
      const data = response.data;
      
      
      const defaultStats = {
        texte: { nb_cours: 0, score_moyen: 0 },
        audio: { nb_cours: 0, score_moyen: 0 },
        video: { nb_cours: 0, score_moyen: 0 },
      };
      
     
      if (data.stats_par_mode) {
        return {
          cours_complets: data.cours_complets || data.cours_completes || 0,
          score_moyen: data.score_moyen || 0,
          temps_total: data.temps_total || 0,
          progression_niveau: data.progression_niveau || 0,
          stats_par_mode: {
            texte: data.stats_par_mode.texte || { nb_cours: 0, score_moyen: 0 },
            audio: data.stats_par_mode.audio || { nb_cours: 0, score_moyen: 0 },
            video: data.stats_par_mode.video || { nb_cours: 0, score_moyen: 0 },
          }
        };
      }
      
      
      return {
        cours_complets: data.cours_complets || 0,
        score_moyen: data.score_moyen || 0,
        temps_total: data.temps_total || 0,
        progression_niveau: data.progression_niveau || 0,
        stats_par_mode: defaultStats,
      };
    } catch (error) {
      console.error('Erreur chargement progression:', error);
      return {
        cours_complets: 0,
        score_moyen: 0,
        temps_total: 0,
        progression_niveau: 0,
        stats_par_mode: {
          texte: { nb_cours: 0, score_moyen: 0 },
          audio: { nb_cours: 0, score_moyen: 0 },
          video: { nb_cours: 0, score_moyen: 0 },
        },
      };
    }
  },

  getUserPreferences: async () => {
    try {
      const response = await api.get('/users/me/preferences');
      return response.data;
    } catch (error) {
      console.error('Erreur chargement préférences:', error);
      return {
        score_texte: 0,
        score_audio: 0,
        score_video: 0,
        confiance: 0,
        date_calcul: null,
        date_maj: null,
        historique: []
      };
    }
  },

  updateProgress: async (courseId: number, progress: number, score?: number) => {
    try {
      const response = await api.post('/users/me/progress', {
        course_id: courseId,
        progress,
        score,
      });
      return response.data;
    } catch (error) {
      console.error('Erreur mise à jour progression:', error);
      throw error;
    }
  },
};