
import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';

interface RiskPattern {
  pattern: string[];
  support: number;
}

interface DropoutRisk {
  score: number;
  level: string;
  factors: string[];
}

interface BehaviorAnalysis {
  status: string;
  user_id: number;
  total_sessions: number;
  total_actions: number;
  dropout_risk: DropoutRisk;
  engagement_level: string;
  risk_patterns: RiskPattern[];
  recommendations: string[];
  message?: string;
}

const BehaviorRiskAnalysis = () => {
  const { user } = useAuth();
  const [analysis, setAnalysis] = useState<BehaviorAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    const loadAnalysis = async () => {
      try {
        setLoading(true);
        const response = await api.get('/behavior/sequential-analysis');
        console.log('📊 Analyse séquentielle reçue:', response.data);
        setAnalysis(response.data);
      } catch (error) {
        console.error('Erreur chargement analyse:', error);
      } finally {
        setLoading(false);
      }
    };
    
    if (user) loadAnalysis();
  }, [user]);

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'Élevé': return 'bg-red-100 text-red-800 border-red-300';
      case 'Modéré': return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      default: return 'bg-green-100 text-green-800 border-green-300';
    }
  };

  const getRiskIcon = (level: string) => {
    switch (level) {
      case 'Élevé': return '🔴';
      case 'Modéré': return '🟡';
      default: return '🟢';
    }
  };

  const getEngagementIcon = (level: string) => {
    switch (level) {
      case 'Critique': return '⚠️';
      case 'Attention': return '⚡';
      default: return '✅';
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-md p-4">
        <div className="text-center py-2">
          <div className="inline-block w-5 h-5 border-2 border-purple-500 border-t-transparent rounded-full animate-spin" />
          <p className="text-xs text-gray-500 mt-1">Analyse des patterns...</p>
        </div>
      </div>
    );
  }

  if (!analysis || analysis.status === 'insufficient_data') {
    return (
      <div className="bg-white rounded-xl shadow-md p-4">
        <div className="text-center py-2">
          <div className="text-xl mb-1">📊</div>
          <p className="text-xs text-gray-500">
            {analysis?.message || "Continuez votre apprentissage pour l'analyse comportementale"}
          </p>
        </div>
      </div>
    );
  }

  const risk = analysis.dropout_risk;
  const riskScore = risk.score;
  const riskLevel = risk.level;
  const riskFactors = risk.factors || [];
  const engagementScore = Math.round((1 - riskScore) * 100);

  return (
    <div className="bg-white rounded-xl shadow-md p-4">
      <div className="flex justify-between items-center mb-3">
        <h4 className="font-semibold text-sm">⚠️ Risque de décrochage</h4>
        <button 
          onClick={() => setExpanded(!expanded)}
          className="text-xs text-gray-400 hover:text-gray-600"
        >
          {expanded ? '▲' : '▼'}
        </button>
      </div>

      <div className={`rounded-lg p-3 mb-3 border ${getRiskColor(riskLevel)}`}>
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs font-medium">Niveau de risque</p>
            <p className="text-lg font-bold">
              {getRiskIcon(riskLevel)} {riskLevel}
            </p>
          </div>
          <div className="text-right">
            <p className="text-xs">Score</p>
            <p className="text-lg font-bold">{(riskScore * 100).toFixed(0)}%</p>
          </div>
        </div>
        
        <div className="mt-2 bg-gray-200 rounded-full h-1.5">
          <div 
            className={`h-1.5 rounded-full transition-all duration-500 ${
              riskScore > 0.6 ? 'bg-red-500' : riskScore > 0.3 ? 'bg-yellow-500' : 'bg-green-500'
            }`}
            style={{ width: `${riskScore * 100}%` }}
          />
        </div>
        
        {expanded && riskFactors.length > 0 && (
          <div className="mt-2 pt-2 border-t border-gray-200">
            <p className="text-xs font-semibold mb-1">Facteurs détectés :</p>
            <ul className="text-xs list-disc list-inside">
              {riskFactors.map((factor, idx) => (
                <li key={idx} className="text-gray-700">{factor}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      <div className="grid grid-cols-2 gap-2 mb-3">
        <div className="text-center p-1 bg-gray-50 rounded-lg">
          <div className="text-sm font-bold text-purple-600">{analysis.total_sessions}</div>
          <p className="text-[10px] text-gray-500">Sessions</p>
        </div>
        <div className="text-center p-1 bg-gray-50 rounded-lg">
          <div className="text-sm font-bold text-blue-600">{analysis.total_actions}</div>
          <p className="text-[10px] text-gray-500">Actions</p>
        </div>
      </div>

      <div className="mb-3">
        <div className="flex justify-between text-xs mb-1">
          <span>Engagement</span>
          <span>{getEngagementIcon(analysis.engagement_level)} {analysis.engagement_level}</span>
        </div>
        <div className="bg-gray-200 h-1 rounded-full overflow-hidden">
          <div 
            className="bg-purple-500 h-full rounded-full"
            style={{ width: `${engagementScore}%` }}
          />
        </div>
      </div>

      {expanded && analysis.risk_patterns.length > 0 && (
        <div className="mb-3">
          <p className="text-xs font-semibold mb-1">⚠️ Patterns à risque détectés :</p>
          <div className="space-y-1">
            {analysis.risk_patterns.slice(0, 2).map((pattern, idx) => (
              <div key={idx} className="text-xs text-gray-600 bg-red-50 p-1 rounded">
                {pattern.pattern.join(' → ')}
                <span className="text-gray-400 ml-1">({(pattern.support * 100).toFixed(0)}%)</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {analysis.recommendations.length > 0 && (
        <div className="bg-yellow-50 rounded-lg p-2">
          <p className="text-xs font-semibold mb-1">💡 Recommandations</p>
          <ul className="space-y-0.5">
            {analysis.recommendations.slice(0, 2).map((rec, idx) => (
              <li key={idx} className="text-xs text-gray-700 flex items-start gap-1">
                <span>•</span>
                <span>{rec}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default BehaviorRiskAnalysis;