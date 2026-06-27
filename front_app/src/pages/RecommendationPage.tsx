
import { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';

interface RecommendationData {
  recommended_mode: string;
  learner_type: string;
  recommended_title: string;
  confidence: number;
  confidence_text: string;
  message: string;
  scores: {
    text: number;
    audio: number;
    video: number;
  };
  metrics: {
    text: number;
    audio: number;
    video: number;
  };
  user_id?: number;
  user_name?: string;
  timestamp?: string;
}


type LearningMode = 'text' | 'audio' | 'video';

const RecommendationPage = () => {
  const { user } = useAuth();
  const [recommendation, setRecommendation] = useState<RecommendationData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadRecommendation();
  }, []);

  const loadRecommendation = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.get('/recommend/learning-mode');
      console.log('📊 Recommandation reçue:', response.data);
      setRecommendation(response.data);
    } catch (error) {
      console.error('Failed to load recommendation:', error);
      setError('Impossible de charger les recommandations');
    } finally {
      setLoading(false);
    }
  };

  const getLearnerTypeDisplay = (type: string) => {
    const types: Record<string, { icon: string; label: string }> = {
      'visuel': { icon: '👁️', label: 'Visuel' },
      'auditif': { icon: '🎧', label: 'Auditif' },
      'lecture': { icon: '📖', label: 'Lecture' },
      'mixte': { icon: '🔄', label: 'Mixte' }
    };
    return types[type] || types['mixte'];
  };

  const getModeDisplay = (mode: string) => {
    const modes: Record<string, { icon: string; label: string; color: string }> = {
      'text': { icon: '📖', label: 'Texte', color: 'text-purple-600' },
      'audio': { icon: '🎧', label: 'Audio', color: 'text-green-600' },
      'video': { icon: '🎬', label: 'Vidéo', color: 'text-red-600' }
    };
    return modes[mode] || { icon: '📚', label: mode, color: 'text-gray-600' };
  };

  
  const getMetricValue = (mode: string): number => {
    if (!recommendation) return 0;
    const metrics = recommendation.metrics;
    switch (mode) {
      case 'text': return metrics.text;
      case 'audio': return metrics.audio;
      case 'video': return metrics.video;
      default: return 0;
    }
  };

  
  const learningModes: LearningMode[] = ['text', 'audio', 'video'];

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto space-y-8">
        <div className="text-center py-12">
          <div className="inline-block w-12 h-12 border-4 border-purple-500 border-t-transparent rounded-full animate-spin" />
          <p className="text-gray-600 mt-4">Analyse de votre profil en cours...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto space-y-8">
        <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-center">
          <div className="text-4xl mb-3">⚠️</div>
          <p className="text-red-600">{error}</p>
          <button
            onClick={loadRecommendation}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
          >
            Réessayer
          </button>
        </div>
      </div>
    );
  }

  if (!recommendation) {
    return (
      <div className="max-w-4xl mx-auto space-y-8">
        <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-6 text-center">
          <div className="text-4xl mb-3">📊</div>
          <p className="text-gray-600">Aucune donnée disponible pour la recommandation.</p>
          <p className="text-sm text-gray-500 mt-2">Complétez quelques cours pour obtenir des recommandations personnalisées.</p>
        </div>
      </div>
    );
  }

  const learnerInfo = getLearnerTypeDisplay(recommendation.learner_type);
  const recommendedMode = getModeDisplay(recommendation.recommended_mode);

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-fade-in">
      
      <div className="bg-gradient-to-r from-purple-500 to-pink-500 rounded-2xl p-6 text-white">
        <h1 className="text-3xl font-bold mb-2">🔍 Recommandation personnalisée</h1>
        <p className="opacity-90">Basée sur vos performances d'apprentissage</p>
      </div>

      
      <div className="bg-white rounded-xl shadow-md p-6">
        <h2 className="text-xl font-bold mb-4 text-gray-800">Votre profil d'apprentissage</h2>
        <div className="space-y-3">
          <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
            <span className="text-2xl">👤</span>
            <div>
              <p className="font-semibold">{user?.prenom} {user?.nom}</p>
              <p className="text-sm text-gray-500">{user?.email}</p>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="p-3 bg-purple-50 rounded-lg">
              <p className="text-sm text-gray-500">Type d'apprenant</p>
              <p className="font-semibold text-lg">{learnerInfo.icon} {learnerInfo.label}</p>
            </div>
            <div className="p-3 bg-blue-50 rounded-lg">
              <p className="text-sm text-gray-500">Niveau</p>
              <p className="font-semibold text-lg">
                {user?.niveau_global === 'débutant' && '🌱 Débutant'}
                {user?.niveau_global === 'intermédiaire' && '📚 Intermédiaire'}
                {user?.niveau_global === 'avancé' && '🚀 Avancé'}
                {!user?.niveau_global && '📖 À déterminer'}
              </p>
            </div>
          </div>
        </div>
      </div>

      
      <div className="bg-gradient-to-r from-blue-500 to-indigo-600 rounded-xl p-6 text-white">
        <h2 className="text-xl font-bold mb-3">🤖 Recommandation IA</h2>
        <div className="bg-white/10 rounded-lg p-4">
          <p className="text-lg leading-relaxed">{recommendation.message}</p>
          <div className="mt-3 flex items-center gap-2 text-sm text-white/80">
            <span>Confiance:</span>
            <span className={`px-2 py-0.5 rounded-full ${
              recommendation.confidence_text === 'Élevée' ? 'bg-green-500' :
              recommendation.confidence_text === 'Moyenne' ? 'bg-yellow-500' : 'bg-gray-500'
            }`}>
              {recommendation.confidence_text}
            </span>
          </div>
        </div>
      </div>

      
      <div className="bg-white rounded-xl shadow-md p-6">
        <h2 className="text-xl font-bold mb-4 text-gray-800">📊 Analyse des performances</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          {learningModes.map((mode) => {
            const score = getMetricValue(mode);
            const modeInfo = getModeDisplay(mode);
            const isBest = recommendation.recommended_mode === mode;
            return (
              <div key={mode} className={`p-4 rounded-xl text-center ${isBest ? 'bg-green-50 border-2 border-green-200' : 'bg-gray-50'}`}>
                <div className="text-3xl mb-2">{modeInfo.icon}</div>
                <p className="font-semibold">{modeInfo.label}</p>
                <p className={`text-2xl font-bold ${modeInfo.color}`}>{score.toFixed(1)}%</p>
                {isBest && <span className="text-xs text-green-600 mt-1 inline-block">🏆 Meilleur score</span>}
              </div>
            );
          })}
        </div>

        <div className="border-t pt-4">
          <p className="font-semibold mb-2">💡 Analyse détaillée</p>
          <ul className="space-y-2 text-sm text-gray-600">
            <li className="flex items-start gap-2">
              <span>📈</span>
              <span>Votre mode le plus performant est <strong>{recommendedMode.label}</strong> avec un score de {getMetricValue(recommendation.recommended_mode).toFixed(1)}%</span>
            </li>
            <li className="flex items-start gap-2">
              <span>🎯</span>
              <span>Nous vous recommandons de privilégier ce format pour vos prochains cours.</span>
            </li>
            <li className="flex items-start gap-2">
              <span>🌟</span>
              <span>Continuez à pratiquer régulièrement pour maintenir votre progression.</span>
            </li>
          </ul>
        </div>
      </div>

      
      <div className="bg-white rounded-xl shadow-md p-6">
        <h2 className="text-xl font-bold mb-4 text-gray-800">📚 Prochaines étapes recommandées</h2>
        <div className="space-y-3">
          <div className="flex items-center gap-3 p-3 bg-purple-50 rounded-lg">
            <span className="text-2xl">🎯</span>
            <div>
              <p className="font-semibold">Continuez avec le mode {recommendedMode.label}</p>
              <p className="text-sm text-gray-600">Concentrez-vous sur les cours en {recommendedMode.label} pour maximiser votre apprentissage</p>
            </div>
          </div>
          <div className="flex items-center gap-3 p-3 bg-blue-50 rounded-lg">
            <span className="text-2xl">📝</span>
            <div>
              <p className="font-semibold">Pratiquez régulièrement</p>
              <p className="text-sm text-gray-600">Des sessions courtes mais fréquentes sont plus efficaces</p>
            </div>
          </div>
          <div className="flex items-center gap-3 p-3 bg-green-50 rounded-lg">
            <span className="text-2xl">🏆</span>
            <div>
              <p className="font-semibold">Testez vos connaissances</p>
              <p className="text-sm text-gray-600">Les quiz et exercices renforcent votre apprentissage</p>
            </div>
          </div>
        </div>
      </div>

      
      <div className="text-center">
        <button
          onClick={loadRecommendation}
          className="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition"
        >
          🔄 Actualiser la recommandation
        </button>
      </div>
    </div>
  );
};

export default RecommendationPage;