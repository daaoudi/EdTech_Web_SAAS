
import { useState } from 'react';
import { sequentialMinerService } from '../services/sequentialMinerService';

interface RiskData {
  user_id: number;
  risk_score: number;
  risk_level: string;
  risk_factors: string[];
  actions_analyzed: number;
  timestamp: string;
}

interface SimulationResult {
  simulation: {
    total_logs: number;
    sequences_count: number;
    patterns_count: number;
    rules_count: number;
  };
  risk_analysis: {
    high_risk_users: number;
    moderate_risk_users: number;
    low_risk_users: number;
    average_risk_score: number;
  };
}

const StudentRiskMonitor = () => {
  const [riskData, setRiskData] = useState<RiskData | null>(null);
  const [loading, setLoading] = useState(false);
  const [userActions, setUserActions] = useState<string[]>([]);
  const [simulationResult, setSimulationResult] = useState<SimulationResult | null>(null);

  const generateMockActions = (): string[] => {
    return [
      'video_start', 'video_complete', 'quiz_start', 'quiz_fail', 
      'quiz_fail', 'quiz_fail', 'navigate_course', 'navigate_course',
      'inactive', 'quiz_start', 'quiz_complete'
    ];
  };

  const analyzeRisk = async (): Promise<void> => {
    setLoading(true);
    try {
      const actions = userActions.length > 0 ? userActions : generateMockActions();
      const result = await sequentialMinerService.analyzeUserRisk(actions);
      setRiskData(result);
    } catch (error) {
      console.error('Erreur analyse risque:', error);
    } finally {
      setLoading(false);
    }
  };

  const runSimulation = async (): Promise<void> => {
    setLoading(true);
    try {
      const result = await sequentialMinerService.simulate(15, 40);
      setSimulationResult(result);
    } catch (error) {
      console.error('Erreur simulation:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (level: string): string => {
    switch (level) {
      case 'Élevé': 
        return 'bg-red-100 text-red-800 border-red-300';
      case 'Modéré': 
        return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      default: 
        return 'bg-green-100 text-green-800 border-green-300';
    }
  };

  const handleActionsChange = (e: React.ChangeEvent<HTMLTextAreaElement>): void => {
    const actions = e.target.value.split(',').map(s => s.trim()).filter(s => s);
    setUserActions(actions);
  };

  return (
    <div className="space-y-6 p-6">
      <div className="bg-white rounded-xl shadow-md p-6">
        <h2 className="text-2xl font-bold mb-4">📊 Analyse de Risque de Décrochage</h2>
        
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Actions utilisateur (séparées par des virgules)
          </label>
          <textarea
            value={userActions.join(', ')}
            onChange={handleActionsChange}
            placeholder="ex: video_start, quiz_start, quiz_fail, inactive"
            className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-purple-500"
            rows={3}
          />
          <p className="text-xs text-gray-500 mt-1">
            Exemple: video_start, video_complete, quiz_start, quiz_fail, quiz_fail, inactive
          </p>
        </div>
        
        <div className="flex gap-3">
          <button
            onClick={analyzeRisk}
            disabled={loading}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition disabled:opacity-50"
          >
            {loading ? 'Analyse...' : '🔍 Analyser le risque'}
          </button>
          <button
            onClick={runSimulation}
            disabled={loading}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
          >
            🎮 Lancer la simulation
          </button>
        </div>
      </div>

      
      {riskData && (
        <div className={`rounded-xl p-6 border-2 ${getRiskColor(riskData.risk_level)}`}>
          <div className="flex justify-between items-start">
            <div>
              <h3 className="text-xl font-bold mb-2">📈 Analyse du risque</h3>
              <p className="text-3xl font-bold mb-2">
                Score: {(riskData.risk_score * 100).toFixed(0)}%
              </p>
              <p className="text-lg mb-2">
                Niveau: <span className="font-bold">{riskData.risk_level}</span>
              </p>
              <p className="text-sm">
                Actions analysées: {riskData.actions_analyzed}
              </p>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-500">
                {new Date(riskData.timestamp).toLocaleString()}
              </p>
            </div>
          </div>
          
          {riskData.risk_factors.length > 0 && (
            <div className="mt-4">
              <h4 className="font-semibold mb-2">⚠️ Facteurs de risque:</h4>
              <ul className="list-disc list-inside space-y-1">
                {riskData.risk_factors.map((factor: string, idx: number) => (
                  <li key={idx} className="text-sm">{factor}</li>
                ))}
              </ul>
            </div>
          )}
          
          <div className="mt-4 pt-4 border-t border-gray-200">
            <h4 className="font-semibold mb-2">💡 Recommandations:</h4>
            <ul className="list-disc list-inside space-y-1 text-sm">
              {riskData.risk_level === 'Élevé' && (
                <>
                  <li>Contacter immédiatement l'étudiant pour un entretien</li>
                  <li>Proposer du contenu plus adapté à son niveau</li>
                  <li>Mettre en place un suivi personnalisé</li>
                </>
              )}
              {riskData.risk_level === 'Modéré' && (
                <>
                  <li>Envoyer des rappels de motivation</li>
                  <li>Suggérer des exercices de renforcement</li>
                  <li>Proposer une session de tutorat</li>
                </>
              )}
              {riskData.risk_level === 'Faible' && (
                <>
                  <li>Continuer à encourager l'apprentissage</li>
                  <li>Proposer des défis supplémentaires</li>
                </>
              )}
            </ul>
          </div>
        </div>
      )}

      
      {simulationResult && (
        <div className="bg-white rounded-xl shadow-md p-6">
          <h3 className="text-xl font-bold mb-4">🎮 Résultats de la simulation</h3>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <p className="text-2xl font-bold text-purple-600">{simulationResult.simulation.total_logs}</p>
              <p className="text-sm text-gray-600">Logs générés</p>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <p className="text-2xl font-bold text-blue-600">{simulationResult.simulation.sequences_count}</p>
              <p className="text-sm text-gray-600">Séquences</p>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <p className="text-2xl font-bold text-green-600">{simulationResult.simulation.patterns_count}</p>
              <p className="text-sm text-gray-600">Motifs</p>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <p className="text-2xl font-bold text-orange-600">{simulationResult.simulation.rules_count}</p>
              <p className="text-sm text-gray-600">Règles</p>
            </div>
          </div>
          
          <div className="bg-gray-50 rounded-lg p-4">
            <h4 className="font-semibold mb-2">📊 Distribution des risques:</h4>
            <div className="flex gap-4">
              <div className="flex-1 text-center">
                <div className="text-2xl font-bold text-red-600">
                  {simulationResult.risk_analysis.high_risk_users}
                </div>
                <p className="text-sm text-gray-600">Risque Élevé</p>
              </div>
              <div className="flex-1 text-center">
                <div className="text-2xl font-bold text-yellow-600">
                  {simulationResult.risk_analysis.moderate_risk_users}
                </div>
                <p className="text-sm text-gray-600">Risque Modéré</p>
              </div>
              <div className="flex-1 text-center">
                <div className="text-2xl font-bold text-green-600">
                  {simulationResult.risk_analysis.low_risk_users}
                </div>
                <p className="text-sm text-gray-600">Risque Faible</p>
              </div>
            </div>
            <p className="text-center text-sm text-gray-500 mt-3">
              Score moyen: {(simulationResult.risk_analysis.average_risk_score * 100).toFixed(1)}%
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default StudentRiskMonitor;