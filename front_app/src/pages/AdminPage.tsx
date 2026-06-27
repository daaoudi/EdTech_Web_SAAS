/* eslint-disable @typescript-eslint/no-explicit-any */

import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';
import { sequentialMinerService } from '../services/sequentialMinerService';

interface SystemStats {
  total_users: number;
  total_courses: number;
  total_results: number;
  avg_score: number;
}

interface UserStats {
  id: number;
  email: string;
  nom: string;
  prenom: string;
  role_name: string;
  total_results: number;
  avg_score: number;
}

const AdminPage = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<'overview' | 'users' | 'risk' | 'patterns'>('overview');
  const [systemStats, setSystemStats] = useState<SystemStats | null>(null);
  const [users, setUsers] = useState<UserStats[]>([]);
  const [patterns, setPatterns] = useState<any[]>([]);
  const [rules, setRules] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [trainingStatus, setTrainingStatus] = useState<string | null>(null);

  
  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      if (activeTab === 'overview') {
        const statsResponse = await api.get('/stats/system');
        setSystemStats(statsResponse.data);
      } else if (activeTab === 'users') {
        const usersResponse = await api.get('/admin/users');
        setUsers(usersResponse.data);
      } else if (activeTab === 'patterns') {
        const patternsData = await sequentialMinerService.getPatterns(50);
        setPatterns(patternsData.patterns || []);
        const rulesData = await sequentialMinerService.getRules(50);
        setRules(rulesData.rules || []);
      }
    } catch (error) {
      console.error('Erreur chargement données admin:', error);
    } finally {
      setLoading(false);
    }
  }, [activeTab]); 

  useEffect(() => {
    loadData();
  }, [loadData]); 

  const trainModel = async () => {
    setTrainingStatus('loading');
    try {
      await sequentialMinerService.trainModel(true);
      setTrainingStatus('success');
      setTimeout(() => setTrainingStatus(null), 3000);
      
      if (activeTab === 'patterns') {
        const patternsData = await sequentialMinerService.getPatterns(50);
        setPatterns(patternsData.patterns || []);
        const rulesData = await sequentialMinerService.getRules(50);
        setRules(rulesData.rules || []);
      }
    } catch (error) {
      console.error('Erreur entraînement:', error);
      setTrainingStatus('error');
      setTimeout(() => setTrainingStatus(null), 3000);
    }
  };

  const runSimulation = async () => {
    setTrainingStatus('loading');
    try {
      
      await sequentialMinerService.simulate(20, 50);
      
      console.log('✅ Simulation terminée avec succès');
      setTrainingStatus('success');
      setTimeout(() => setTrainingStatus(null), 3000);
    } catch (error) {
      console.error('Erreur simulation:', error);
      setTrainingStatus('error');
      setTimeout(() => setTrainingStatus(null), 3000);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="container mx-auto py-8 px-4">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-800">🛠️ Administration</h1>
          <p className="text-gray-500 mt-1">
            Bienvenue {user?.prenom} {user?.nom}
          </p>
        </div>

        
        <div className="flex flex-wrap gap-2 mb-6 border-b border-gray-200">
          <button
            onClick={() => setActiveTab('overview')}
            className={`px-4 py-2 rounded-t-lg transition ${
              activeTab === 'overview'
                ? 'bg-white text-purple-600 border-b-2 border-purple-600 font-medium'
                : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            📊 Vue d'ensemble
          </button>
          <button
            onClick={() => setActiveTab('users')}
            className={`px-4 py-2 rounded-t-lg transition ${
              activeTab === 'users'
                ? 'bg-white text-purple-600 border-b-2 border-purple-600 font-medium'
                : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            👥 Utilisateurs
          </button>
          <button
            onClick={() => setActiveTab('patterns')}
            className={`px-4 py-2 rounded-t-lg transition ${
              activeTab === 'patterns'
                ? 'bg-white text-purple-600 border-b-2 border-purple-600 font-medium'
                : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            🔍 Patterns & Règles
          </button>
          <button
            onClick={() => window.location.href = '/admin/risk-monitor'}
            className={`px-4 py-2 rounded-t-lg transition ${
              activeTab === 'risk'
                ? 'bg-white text-purple-600 border-b-2 border-purple-600 font-medium'
                : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            📈 Monitoring Risques
          </button>
        </div>

        
        <div className="bg-white rounded-xl shadow-md p-6">
          {loading ? (
            <div className="text-center py-12">
              <div className="inline-block w-8 h-8 border-2 border-purple-500 border-t-transparent rounded-full animate-spin" />
              <p className="text-gray-500 mt-3">Chargement...</p>
            </div>
          ) : (
            <>
              
              {activeTab === 'overview' && systemStats && (
                <div>
                  <h2 className="text-xl font-bold mb-4">Statistiques système</h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    <div className="bg-blue-50 rounded-xl p-4 text-center">
                      <div className="text-3xl font-bold text-blue-600">{systemStats.total_users || 0}</div>
                      <p className="text-sm text-gray-600 mt-1">Utilisateurs</p>
                    </div>
                    <div className="bg-green-50 rounded-xl p-4 text-center">
                      <div className="text-3xl font-bold text-green-600">{systemStats.total_courses || 0}</div>
                      <p className="text-sm text-gray-600 mt-1">Cours</p>
                    </div>
                    <div className="bg-purple-50 rounded-xl p-4 text-center">
                      <div className="text-3xl font-bold text-purple-600">{systemStats.total_results || 0}</div>
                      <p className="text-sm text-gray-600 mt-1">Quiz complétés</p>
                    </div>
                    <div className="bg-orange-50 rounded-xl p-4 text-center">
                      <div className="text-3xl font-bold text-orange-600">{systemStats.avg_score?.toFixed(1) || 0}%</div>
                      <p className="text-sm text-gray-600 mt-1">Score moyen</p>
                    </div>
                  </div>

                 
                  <div className="mt-8 border-t pt-6">
                    <h3 className="font-semibold mb-3">Actions d'entraînement</h3>
                    <div className="flex flex-wrap gap-3">
                      <button
                        onClick={trainModel}
                        disabled={trainingStatus === 'loading'}
                        className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition disabled:opacity-50"
                      >
                        {trainingStatus === 'loading' ? '⏳ Entraînement...' : '🤖 Entraîner le modèle'}
                      </button>
                      <button
                        onClick={runSimulation}
                        disabled={trainingStatus === 'loading'}
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
                      >
                        🎮 Lancer la simulation
                      </button>
                    </div>
                    {trainingStatus === 'success' && (
                      <p className="text-green-600 text-sm mt-2">✅ Opération réussie !</p>
                    )}
                    {trainingStatus === 'error' && (
                      <p className="text-red-600 text-sm mt-2">❌ Erreur lors de l'opération</p>
                    )}
                  </div>
                </div>
              )}

              
              {activeTab === 'users' && (
                <div>
                  <h2 className="text-xl font-bold mb-4">Liste des utilisateurs</h2>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-4 py-2 text-left">ID</th>
                          <th className="px-4 py-2 text-left">Nom</th>
                          <th className="px-4 py-2 text-left">Email</th>
                          <th className="px-4 py-2 text-left">Rôle</th>
                          <th className="px-4 py-2 text-center">Quiz</th>
                          <th className="px-4 py-2 text-center">Score</th>
                        </tr>
                      </thead>
                      <tbody>
                        {users.map((u) => (
                          <tr key={u.id} className="border-t border-gray-100 hover:bg-gray-50">
                            <td className="px-4 py-2">{u.id}</td>
                            <td className="px-4 py-2">{u.prenom} {u.nom}</td>
                            <td className="px-4 py-2">{u.email}</td>
                            <td className="px-4 py-2">
                              <span className={`px-2 py-1 rounded-full text-xs ${
                                u.role_name === 'admin' ? 'bg-red-100 text-red-700' : 'bg-blue-100 text-blue-700'
                              }`}>
                                {u.role_name || 'utilisateur'}
                              </span>
                            </td>
                            <td className="px-4 py-2 text-center">{u.total_results || 0}</td>
                            <td className="px-4 py-2 text-center">{u.avg_score?.toFixed(1) || 0}%</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              
              {activeTab === 'patterns' && (
                <div className="space-y-6">
                  <div>
                    <h2 className="text-xl font-bold mb-4">🔍 Motifs fréquents</h2>
                    {patterns.length > 0 ? (
                      <div className="space-y-2 max-h-96 overflow-y-auto">
                        {patterns.slice(0, 20).map((pattern, idx) => (
                          <div key={idx} className="bg-gray-50 rounded-lg p-3">
                            <div className="flex justify-between items-center">
                              <code className="text-sm">{JSON.stringify(pattern)}</code>
                              <span className="text-xs text-gray-500">
                                Support: {(pattern.support * 100).toFixed(1)}%
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-gray-500">Aucun motif trouvé. Lancez l'entraînement du modèle.</p>
                    )}
                  </div>

                  <div>
                    <h2 className="text-xl font-bold mb-4">📋 Règles d'association</h2>
                    {rules.length > 0 ? (
                      <div className="space-y-2 max-h-96 overflow-y-auto">
                        {rules.slice(0, 20).map((rule, idx) => (
                          <div key={idx} className="bg-gray-50 rounded-lg p-3">
                            <div className="flex justify-between items-start gap-4">
                              <div className="flex-1">
                                <code className="text-sm break-all">
                                  {JSON.stringify(rule.antecedent)} → {JSON.stringify(rule.consequent)}
                                </code>
                              </div>
                              <div className="text-right shrink-0">
                                <span className="text-xs text-green-600 block">
                                  Confiance: {(rule.confidence * 100).toFixed(1)}%
                                </span>
                                <span className="text-xs text-gray-500">
                                  Support: {(rule.support * 100).toFixed(1)}%
                                </span>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-gray-500">Aucune règle trouvée. Lancez l'entraînement du modèle.</p>
                    )}
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminPage;