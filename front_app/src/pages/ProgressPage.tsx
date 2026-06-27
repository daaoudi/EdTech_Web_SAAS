 
import { useEffect, useState } from 'react';
import { courseService } from '../services/courseService';
import type { UserProgress } from '../services/courseService';
import { Line, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

const ProgressPage = () => {
  const [progress, setProgress] = useState<UserProgress | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadProgress();
  }, []);

  const loadProgress = async () => {
    try {
      setLoading(true);
      const data = await courseService.getUserProgress();
      setProgress(data);
      setError(null);
    } catch (err) {
      console.error('Failed to load progress:', err);
      setError('Impossible de charger les statistiques');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="text-center py-20">
        <div className="text-4xl mb-4">📊</div>
        <div className="text-xl text-gray-600">Chargement des statistiques...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-20">
        <div className="text-4xl mb-4">⚠️</div>
        <div className="text-xl text-red-600">{error}</div>
        <button 
          onClick={loadProgress}
          className="mt-4 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
        >
          Réessayer
        </button>
      </div>
    );
  }

  if (!progress) {
    return (
      <div className="text-center py-20">
        <div className="text-4xl mb-4">📊</div>
        <div className="text-xl text-gray-600">Aucune donnée de progression disponible</div>
        <p className="text-gray-500 mt-2">Commencez votre premier cours pour voir vos statistiques</p>
      </div>
    );
  }

  
  const coursComplets = progress.cours_complets ?? 0;
  const scoreMoyen = progress.score_moyen ?? 0;
  const tempsTotal = progress.temps_total ?? 0;
  const progressionNiveau = progress.progression_niveau ?? 0;

 
  const defaultStats = {
    texte: { nb_cours: 0, score_moyen: 0 },
    audio: { nb_cours: 0, score_moyen: 0 },
    video: { nb_cours: 0, score_moyen: 0 },
  };
  
  const statsParMode = progress.stats_par_mode || defaultStats;
  
  
  const safeStats = {
    texte: statsParMode.texte || defaultStats.texte,
    audio: statsParMode.audio || defaultStats.audio,
    video: statsParMode.video || defaultStats.video,
  };

  const modeNames = {
    texte: 'Mode Texte',
    audio: 'Mode Audio',
    video: 'Mode Vidéo',
  };

  const modeColors = {
    texte: '#8B5CF6',
    audio: '#10B981',
    video: '#EF4444',
  };

  
  const lineChartData = {
    labels: ['Semaine 1', 'Semaine 2', 'Semaine 3', 'Semaine 4'],
    datasets: [
      {
        label: 'Progression (%)',
        data: [25, 45, 65, progressionNiveau],
        borderColor: '#3B82F6',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4,
        fill: true,
      },
    ],
  };

  
  const doughnutData = {
    labels: Object.values(modeNames),
    datasets: [
      {
        data: [
          safeStats.texte.nb_cours || 0,
          safeStats.audio.nb_cours || 0,
          safeStats.video.nb_cours || 0,
        ],
        backgroundColor: [modeColors.texte, modeColors.audio, modeColors.video],
        borderWidth: 0,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: {
        position: 'bottom' as const,
      },
    },
  };

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold text-primary-800">📊 Vos statistiques</h1>

      
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl shadow-md p-6 text-center">
          <div className="text-4xl font-bold text-primary-600 mb-2">{coursComplets}</div>
          <div className="text-gray-600">Cours complétés</div>
        </div>
        <div className="bg-white rounded-xl shadow-md p-6 text-center">
          <div className="text-4xl font-bold text-green-600 mb-2">{scoreMoyen.toFixed(1)}%</div>
          <div className="text-gray-600">Score moyen</div>
        </div>
        <div className="bg-white rounded-xl shadow-md p-6 text-center">
          <div className="text-4xl font-bold text-blue-600 mb-2">
            {Math.floor(tempsTotal / 60)}h{tempsTotal % 60 > 0 ? `${tempsTotal % 60}min` : ''}
          </div>
          <div className="text-gray-600">Temps total</div>
        </div>
        <div className="bg-white rounded-xl shadow-md p-6 text-center">
          <div className="text-4xl font-bold text-purple-600 mb-2">{progressionNiveau}%</div>
          <div className="text-gray-600">Progression globale</div>
        </div>
      </div>

      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white rounded-xl shadow-md p-6">
          <h2 className="text-xl font-bold mb-4">Évolution de la progression</h2>
          {progressionNiveau > 0 ? (
            <Line data={lineChartData} options={options} />
          ) : (
            <div className="text-center py-12 text-gray-500">
              <p>Commencez votre premier cours pour voir votre progression</p>
            </div>
          )}
        </div>
        <div className="bg-white rounded-xl shadow-md p-6">
          <h2 className="text-xl font-bold mb-4">Répartition par mode</h2>
          <div className="max-w-md mx-auto">
            {safeStats.texte.nb_cours + safeStats.audio.nb_cours + safeStats.video.nb_cours > 0 ? (
              <Doughnut data={doughnutData} options={options} />
            ) : (
              <div className="text-center py-12 text-gray-500">
                <p>Pas encore de données par mode</p>
              </div>
            )}
          </div>
        </div>
      </div>

      
      <div className="bg-white rounded-xl shadow-md p-6">
        <h2 className="text-xl font-bold mb-6">Performance par mode d'apprentissage</h2>
        <div className="space-y-6">
          {Object.entries(safeStats).map(([mode, stats]) => {
            const score = stats?.score_moyen ?? 0;
            const nbCours = stats?.nb_cours ?? 0;
            
            return (
              <div key={mode}>
                <div className="flex justify-between mb-2">
                  <span className="font-semibold">
                    {mode === 'texte' && '📖 Mode Texte'}
                    {mode === 'audio' && '🎧 Mode Audio'}
                    {mode === 'video' && '🎬 Mode Vidéo'}
                  </span>
                  <span className="text-gray-600">
                    {nbCours} cours • Score: {score.toFixed(1)}%
                  </span>
                </div>
                <div className="bg-gray-200 h-3 rounded-full overflow-hidden">
                  <div 
                    className="h-full rounded-full transition-all"
                    style={{ 
                      width: `${score}%`,
                      backgroundColor: modeColors[mode as keyof typeof modeColors]
                    }}
                  />
                </div>
              </div>
            );
          })}
        </div>
        
        {safeStats.texte.nb_cours + safeStats.audio.nb_cours + safeStats.video.nb_cours === 0 && (
          <div className="text-center py-8 text-gray-500">
            <p className="mb-2">📚</p>
            <p>Aucune donnée disponible pour le moment</p>
            <p className="text-sm mt-2">Commencez un cours pour voir vos performances par mode</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProgressPage;