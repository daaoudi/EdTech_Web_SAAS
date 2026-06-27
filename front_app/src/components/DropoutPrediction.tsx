
import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';



interface SequentialAnalysis {
  status: string;
  user_id: number;
  total_sessions: number;
  total_actions: number;
  dropout_risk: {
    score: number;
    level: string;
    factors: string[];
  };
  engagement_level: string;
  risk_patterns: Array<{ pattern: string[]; support: number }>;
  recommendations: string[];
  message?: string;
}

const DropoutPrediction = () => {
  const { user } = useAuth();
  const [analysis, setAnalysis] = useState<SequentialAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    const loadPrediction = async () => {
      try {
        setLoading(true);
        const response = await api.get('/behavior/sequential-analysis');
        console.log('📊 Prédiction décrochage reçue:', response.data);
        setAnalysis(response.data);
      } catch (error) {
        console.error('Erreur chargement prédiction:', error);
      } finally {
        setLoading(false);
      }
    };
    
    if (user) loadPrediction();
  }, [user]);

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-md p-4">
        <div className="text-center py-4">
          <div className="inline-block w-6 h-6 border-2 border-purple-500 border-t-transparent rounded-full animate-spin" />
          <p className="text-xs text-gray-500 mt-2">Analyse du risque...</p>
        </div>
      </div>
    );
  }

  if (!analysis || analysis.status === 'insufficient_data') {
    return (
      <div className="bg-white rounded-xl shadow-md p-4">
        <div className="text-center py-4">
          <div className="text-3xl mb-2">📊</div>
          <h4 className="text-sm font-semibold mb-1">Prédiction décrochage</h4>
          <p className="text-xs text-gray-500">
            {analysis?.message || "Continuez votre apprentissage pour une prédiction précise"}
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

  const risk = analysis.dropout_risk;
  const riskScore = risk.score;
  const riskLevel = risk.level;
  const riskFactors = risk.factors || [];
  const engagementScore = Math.round((1 - riskScore) * 100);
  const riskPercentage = Math.round(riskScore * 100);

  
  const getRiskColor = () => {
    switch (riskLevel) {
      case 'Élevé': return 'bg-red-500';
      case 'Modéré': return 'bg-yellow-500';
      default: return 'bg-green-500';
    }
  };

  const getRiskBgColor = () => {
    switch (riskLevel) {
      case 'Élevé': return 'bg-red-50 border-red-200';
      case 'Modéré': return 'bg-yellow-50 border-yellow-200';
      default: return 'bg-green-50 border-green-200';
    }
  };

  const getRiskIcon = () => {
    switch (riskLevel) {
      case 'Élevé': return '🔴';
      case 'Modéré': return '🟡';
      default: return '🟢';
    }
  };

  const getRiskMessage = () => {
    switch (riskLevel) {
      case 'Élevé':
        return "⚠️ Risque élevé de décrochage détecté. Une action immédiate est recommandée.";
      case 'Modéré':
        return "⚡ Risque modéré de décrochage. Une attention particulière est nécessaire.";
      default:
        return "✅ Risque faible de décrochage. L'étudiant est sur la bonne voie.";
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-md p-4">
      <div className="flex justify-between items-center mb-3">
        <h4 className="font-semibold text-sm">⚠️ Prédiction de décrochage</h4>
        <button 
          onClick={() => setExpanded(!expanded)}
          className="text-xs text-gray-400 hover:text-gray-600"
        >
          {expanded ? '▲' : '▼'}
        </button>
      </div>

      
      <div className={`rounded-lg p-4 mb-4 border-2 ${getRiskBgColor()}`}>
        <div className="flex items-center justify-between mb-3">
          <div>
            <p className="text-xs font-medium text-gray-500">Niveau de risque</p>
            <p className="text-2xl font-bold">
              {getRiskIcon()} {riskLevel}
            </p>
          </div>
          <div className="text-right">
            <p className="text-xs font-medium text-gray-500">Score</p>
            <p className="text-2xl font-bold">{riskPercentage}%</p>
          </div>
        </div>
        
        
        <div className="mb-3">
          <div className="bg-gray-200 rounded-full h-2.5">
            <div 
              className={`h-2.5 rounded-full transition-all duration-500 ${getRiskColor()}`}
              style={{ width: `${riskPercentage}%` }}
            />
          </div>
        </div>
        
        <p className="text-xs text-gray-600 mt-2">{getRiskMessage()}</p>
      </div>

      
      <div className="grid grid-cols-3 gap-2 mb-4">
        <div className="text-center p-2 bg-gray-50 rounded-lg">
          <div className="text-lg font-bold text-purple-600">{analysis.total_sessions || 0}</div>
          <p className="text-[10px] text-gray-500">Sessions</p>
        </div>
        <div className="text-center p-2 bg-gray-50 rounded-lg">
          <div className="text-lg font-bold text-blue-600">{analysis.total_actions || 0}</div>
          <p className="text-[10px] text-gray-500">Actions</p>
        </div>
        <div className="text-center p-2 bg-gray-50 rounded-lg">
          <div className="text-lg font-bold text-green-600">{engagementScore}%</div>
          <p className="text-[10px] text-gray-500">Engagement</p>
        </div>
      </div>

      
      {expanded && riskFactors.length > 0 && (
        <div className="mb-4 p-3 bg-red-50 rounded-lg">
          <p className="text-xs font-semibold text-red-700 mb-2">⚠️ Facteurs de risque détectés :</p>
          <ul className="space-y-1">
            {riskFactors.map((factor, idx) => (
              <li key={idx} className="text-xs text-red-600 flex items-start gap-2">
                <span>•</span>
                <span>{factor}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      
      {expanded && analysis.risk_patterns && analysis.risk_patterns.length > 0 && (
        <div className="mb-4 p-3 bg-orange-50 rounded-lg">
          <p className="text-xs font-semibold text-orange-700 mb-2">📊 Patterns comportementaux :</p>
          <div className="space-y-1">
            {analysis.risk_patterns.slice(0, 3).map((pattern, idx) => (
              <div key={idx} className="text-xs text-gray-600">
                <span className="font-mono">{pattern.pattern.join(' → ')}</span>
                <span className="text-gray-400 ml-2">({(pattern.support * 100).toFixed(0)}% des cas)</span>
              </div>
            ))}
          </div>
        </div>
      )}

      
      {analysis.recommendations && analysis.recommendations.length > 0 && (
        <div className={`rounded-lg p-3 ${
          riskLevel === 'Élevé' ? 'bg-red-100' : riskLevel === 'Modéré' ? 'bg-yellow-100' : 'bg-green-100'
        }`}>
          <p className="text-xs font-semibold mb-2">💡 Recommandations :</p>
          <ul className="space-y-1">
            {analysis.recommendations.slice(0, 3).map((rec, idx) => (
              <li key={idx} className="text-xs text-gray-700 flex items-start gap-1">
                <span>•</span>
                <span>{rec}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      
      {analysis.dropout_risk && analysis.dropout_risk.score > 0 && (
        <div className="mt-3 pt-2 border-t border-gray-100">
          <div className="flex justify-between text-xs text-gray-500">
            <span>Dernière analyse</span>
            <span>{new Date().toLocaleDateString()}</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default DropoutPrediction;