
import { useState, useEffect, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';

interface ModeStats {
  count: number;
  avg_score: number;
  avg_completion: number;
  success_rate: number;
  combined_score: number;
}

interface BehaviorAnalysis {
  status: string;
  user_id: number;
  total_actions: number;
  preferred_content: string;
  mode_stats?: Record<string, ModeStats>;
  mode_scores?: Record<string, number>;
  dropout_risk: {
    score: number;
    level: string;
    factors: string[];
  };
  action_summary: Record<string, number>;
  recommendations: string[];
  message?: string;
  engagement_score?: number;
  detected_learner_type?: string;
}

const UserBehaviorAnalysis = () => {
  const { user } = useAuth();
  const [analysis, setAnalysis] = useState<BehaviorAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState(false);
  const hasLoaded = useRef(false);

  useEffect(() => {
    if (hasLoaded.current) return;
    hasLoaded.current = true;
    
    const loadAnalysis = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 10000);
        
        const response = await api.get('/behavior/my-analysis', {
          signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        console.log('📊 Analyse comportementale reçue:', response.data);
        setAnalysis(response.data);
      } catch (err) {
        console.error('Erreur chargement analyse:', err);
        setError('Impossible de charger votre analyse comportementale');
      } finally {
        setLoading(false);
      }
    };

    if (user) {
      loadAnalysis();
    } else {
      setLoading(false);
    }
  }, [user]);

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-md p-4">
        <div className="text-center py-4">
          <div className="inline-block w-6 h-6 border-2 border-purple-500 border-t-transparent rounded-full animate-spin" />
          <p className="text-gray-500 text-xs mt-2">Analyse en cours...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-xl shadow-md p-4">
        <div className="text-center py-4">
          <div className="text-2xl mb-2">⚠️</div>
          <p className="text-xs text-gray-500">{error}</p>
          <button 
            onClick={() => window.location.reload()}
            className="mt-2 text-xs text-purple-500 hover:underline"
          >
            Réessayer
          </button>
        </div>
      </div>
    );
  }

  if (!analysis || analysis.status === 'no_data' || !analysis.dropout_risk) {
    return (
      <div className="bg-white rounded-xl shadow-md p-4">
        <div className="text-center py-4">
          <div className="text-2xl mb-2">📊</div>
          <h4 className="text-sm font-semibold mb-1">Analyse comportementale</h4>
          <p className="text-xs text-gray-500">
            {analysis?.message || "Continuez à utiliser la plateforme pour obtenir des analyses personnalisées"}
          </p>
          <div className="mt-3 flex justify-center gap-2 text-xs text-gray-400">
            <span>📚 Suivez des cours</span>
            <span>•</span>
            <span>🎯 Passez des quiz</span>
          </div>
        </div>
      </div>
    );
  }

  const getRiskColor = (level: string): string => {
    switch (level) {
      case 'Élevé': return 'bg-red-100 text-red-800 border-red-300';
      case 'Modéré': return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      default: return 'bg-green-100 text-green-800 border-green-300';
    }
  };

  const getRiskIcon = (level: string): string => {
    switch (level) {
      case 'Élevé': return '🔴';
      case 'Modéré': return '🟡';
      default: return '🟢';
    }
  };

  const getContentIcon = (type: string): string => {
    const icons: Record<string, string> = {
      'video': '🎬',
      'audio': '🎧',
      'texte': '📖',
      'quiz': '🎯',
      'exercise': '💪',
      'inconnu': '📚'
    };
    return icons[type] || '📚';
  };

  const getContentLabel = (type: string): string => {
    const labels: Record<string, string> = {
      'video': 'Vidéo',
      'audio': 'Audio',
      'texte': 'Texte',
      'quiz': 'Quiz',
      'exercise': 'Exercice',
      'inconnu': 'Mixte'
    };
    return labels[type] || type;
  };

  
  const getLearnerTypeLabel = (): string => {
    const learnerType = user?.type_apprenant || analysis.detected_learner_type || 'mixte';
    const labels: Record<string, string> = {
      'visuel': '👁️ Visuel',
      'auditif': '🎧 Auditif',
      'lecture': '📖 Lecture',
      'mixte': '🔄 Mixte'
    };
    return labels[learnerType] || '🔄 Mixte';
  };

 
  const getBestModeFromScores = (): { mode: string; score: number; count: number } => {
    const modeStats = analysis.mode_stats || {};
    let bestMode = 'inconnu';
    let bestScore = 0;
    let bestCount = 0;
    
    for (const [mode, stats] of Object.entries(modeStats)) {
      const score = stats.avg_score || 0;
      const count = stats.count || 0;
      
      
      if (score > bestScore) {
        bestScore = score;
        bestMode = mode;
        bestCount = count;
      } 
      
      else if (score === bestScore && count > bestCount) {
        bestMode = mode;
        bestCount = count;
      }
    }
    
    return { mode: bestMode, score: bestScore, count: bestCount };
  };

 
  const getPreferredContentFromScores = (): string => {
    const bestMode = getBestModeFromScores();
    return bestMode.mode;
  };

  const bestFormat = getBestModeFromScores();
  const bestFormatIcon = getContentIcon(bestFormat.mode);
  const bestFormatLabel = getContentLabel(bestFormat.mode);
  
  
  const truePreferredContent = getPreferredContentFromScores();
  const truePreferredIcon = getContentIcon(truePreferredContent);
  const truePreferredLabel = getContentLabel(truePreferredContent);
  const truePreferredScore = analysis.mode_stats?.[truePreferredContent]?.avg_score || 0;

  
  const riskLevel = analysis.dropout_risk?.level || 'Faible';
  const riskScore = analysis.dropout_risk?.score || 0;
  const riskFactors = analysis.dropout_risk?.factors || [];
  const totalActions = analysis.total_actions || 0;
  const recommendations = analysis.recommendations || [];
  const engagementScore = analysis.engagement_score || Math.round((1 - riskScore) * 100);
  const completionRate = engagementScore;
  const modeStats = analysis.mode_stats || {};

  return (
    <div className="bg-white rounded-xl shadow-md p-4">
      <div className="flex justify-between items-center mb-3">
        <h4 className="font-semibold text-sm">📊 Votre apprentissage</h4>
        <button 
          onClick={() => setExpanded(!expanded)}
          className="text-xs text-gray-400 hover:text-gray-600"
        >
          {expanded ? '▲' : '▼'}
        </button>
      </div>

     
      <div className="mb-3 pb-2 border-b border-gray-100">
        <p className="text-xs text-gray-500">
          Profil détecté: <span className="font-medium">{getLearnerTypeLabel()}</span>
        </p>
      </div>

      
      {bestFormat.mode !== 'inconnu' && bestFormat.score > 0 && (
        <div className="mb-3 p-2 bg-green-50 rounded-lg">
          <p className="text-xs text-gray-500 mb-1">Votre meilleur format</p>
          <div className="flex items-center gap-2">
            <span className="text-xl">{bestFormatIcon}</span>
            <div>
              <p className="font-semibold text-sm">{bestFormatLabel}</p>
              <p className="text-xs font-bold text-green-600">{bestFormat.score.toFixed(1)}%</p>
              <p className="text-xs text-gray-400">{bestFormat.count} cours</p>
            </div>
          </div>
        </div>
      )}
      
      
      <div className={`rounded-lg p-3 mb-4 border ${getRiskColor(riskLevel)}`}>
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs font-medium">Niveau d'engagement</p>
            <p className="text-lg font-bold">
              {getRiskIcon(riskLevel)} {riskLevel}
            </p>
          </div>
          <div className="text-right">
            <p className="text-xs">Complétion</p>
            <p className="text-lg font-bold">{completionRate}%</p>
          </div>
        </div>
        
        
        <div className="mt-2 bg-white/30 rounded-full h-1.5">
          <div 
            className="bg-current h-1.5 rounded-full transition-all duration-500"
            style={{ width: `${completionRate}%` }}
          />
        </div>
        
        {riskFactors.length > 0 && expanded && (
          <div className="mt-2 pt-2 border-t border-gray-200">
            <p className="text-xs font-semibold mb-1">Facteurs détectés :</p>
            <ul className="text-xs list-disc list-inside">
              {riskFactors.map((factor: string, idx: number) => (
                <li key={idx} className="text-gray-700">{factor}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      
      <div className="grid grid-cols-2 gap-3 mb-4">
        <div className="text-center p-2 bg-gray-50 rounded-lg">
          <div className="text-xl font-bold text-purple-600">{totalActions}</div>
          <p className="text-xs text-gray-500">Modules complétés</p>
        </div>
        
       
        <div className="text-center p-2 bg-gray-50 rounded-lg">
          <div className="text-xl">
            {truePreferredIcon}
          </div>
          <p className="text-xs text-gray-500">Format préféré</p>
          <p className="text-xs font-medium">{truePreferredLabel}</p>
          <p className="text-xs text-green-600 font-bold">{truePreferredScore.toFixed(1)}%</p>
        </div>
      </div>

      
      {expanded && Object.keys(modeStats).length > 0 && (
        <div className="mb-4">
          <p className="text-xs font-semibold mb-2">📈 Scores par format</p>
          <div className="space-y-3">
            {Object.entries(modeStats).map(([mode, stats]) => {
              const isBest = mode === bestFormat.mode;
              return (
                <div key={mode} className={isBest ? 'bg-green-50 rounded-lg p-2' : ''}>
                  <div className="flex justify-between text-xs mb-1">
                    <span>
                      {getContentIcon(mode)} {getContentLabel(mode)}
                      <span className="text-gray-400 ml-1">({stats.count} cours)</span>
                    </span>
                    <span className="font-bold">{stats.avg_score.toFixed(1)}%</span>
                  </div>
                  <div className="bg-gray-200 h-1.5 rounded-full overflow-hidden">
                    <div 
                      className="h-full rounded-full transition-all duration-500"
                      style={{
                        width: `${stats.avg_score}%`,
                        backgroundColor: isBest ? '#10B981' : mode === 'texte' ? '#8B5CF6' : mode === 'audio' ? '#10B981' : '#EF4444'
                      }}
                    />
                  </div>
                  {isBest && <p className="text-xs text-green-600 mt-1">🏆 Meilleur score</p>}
                </div>
              );
            })}
          </div>
        </div>
      )}

      
      {recommendations.length > 0 && (
        <div className="bg-purple-50 rounded-lg p-3">
          <p className="text-xs font-semibold mb-2">💡 Recommandations</p>
          <ul className="space-y-1">
            {(expanded ? recommendations : recommendations.slice(0, 2)).map((rec: string, idx: number) => (
              <li key={idx} className="text-xs text-gray-700 flex items-start gap-1">
                <span>•</span>
                <span>{rec}</span>
              </li>
            ))}
          </ul>
          {!expanded && recommendations.length > 2 && (
            <p className="text-xs text-gray-400 mt-1 text-center">
              +{recommendations.length - 2} autres recommandations
            </p>
          )}
        </div>
      )}
    </div>
  );
};

export default UserBehaviorAnalysis;