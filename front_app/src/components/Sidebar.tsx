import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { courseService } from '../services/courseService';
import type { UserProgress } from '../services/courseService';
import { useEffect, useState } from 'react';
import UserBehaviorAnalysis from './UserBehaviorAnalysis';
import BehaviorRiskAnalysis from './BehaviorRiskAnalysis';
import api from '../services/api';
import DropoutPrediction from './DropoutPrediction';
import { useLearningContext } from '../contexts/LearningContext';


interface SidebarProps {
  open?: boolean;
  onClose?: () => void;
}


const COURSE_CATEGORIES = {
  HTML: {
    id: 'html',
    icon: '📄',
    color: 'text-orange-600',
    bgColor: 'bg-orange-50',
    borderColor: 'border-orange-200',
    courses: [
      { id: 6, title: 'Formatage du Texte en HTML', icon: '📝' },
      { id: 11, title: 'Les Liens Hypertextes en HTML', icon: '🔗' },
      { id: 12, title: 'Images en HTML', icon: '🖼️' },
      { id: 8, title: 'Formulaires HTML Avancés', icon: '📝' },
      { id: 13, title: 'Les Tableaux en HTML', icon: '📊' },
      { id: 14, title: 'HTML Head - Métadonnées', icon: '🧩' },
      { id: 15, title: 'HTML Multimédia', icon: '🎬' },
      { id: 9, title: 'HTML5 Sémantique', icon: '🏗️' },
    ]
  },
  CSS: {
    id: 'css',
    icon: '🎨',
    color: 'text-blue-600',
    bgColor: 'bg-blue-50',
    borderColor: 'border-blue-200',
    courses: [
      { id: 16, title: 'CSS Media Queries', icon: '📱' },
      { id: 17, title: 'CSS - Sélecteurs', icon: '🎯' },
      { id: 18, title: 'CSS - Couleurs', icon: '🎨' },
      { id: 19, title: 'CSS - Arrière-plans', icon: '🖼️' },
      { id: 20, title: 'CSS - Bordures', icon: '🖼️' },
      { id: 22, title: 'CSS - Marges', icon: '📐' },
      { id: 23, title: 'CSS - Padding', icon: '📦' },
      { id: 24, title: 'CSS - Texte', icon: '📝' },
      { id: 25, title: 'CSS - Polices', icon: '🔤' },
      { id: 26, title: 'CSS - Liens', icon: '🔗' },
      { id: 27, title: 'CSS - Listes', icon: '📋' },
      { id: 28, title: 'CSS - Tableaux', icon: '📊' },
      { id: 29, title: 'CSS - Display & Visibility', icon: '👁️' },
      { id: 30, title: 'CSS - Positionnement', icon: '📍' },
      { id: 31, title: 'CSS - Overflow', icon: '📦' },
      { id: 32, title: 'CSS - Float', icon: '🌊' },
      { id: 10, title: 'CSS Flexbox & Grid', icon: '🎨' },
    ]
  },
  JavaScript: {
    id: 'js',
    icon: '🚀',
    color: 'text-yellow-600',
    bgColor: 'bg-yellow-50',
    borderColor: 'border-yellow-200',
    courses: [
      { id: 33, title: 'JavaScript - Introduction', icon: '🚀' },
      { id: 34, title: 'JavaScript - Variables', icon: '📦' },
      { id: 35, title: 'JavaScript - Types de Données', icon: '🔢' },
      { id: 36, title: 'JavaScript - Opérateurs', icon: '➕' },
      { id: 37, title: 'JavaScript - Conditions', icon: '🤔' },
      { id: 38, title: 'JavaScript - Boucles', icon: '🔄' },
      { id: 39, title: 'JavaScript - Chaînes', icon: '📝' },
      { id: 40, title: 'JavaScript - Nombres', icon: '🔢' },
      { id: 41, title: 'JavaScript - Fonctions', icon: '🎯' },
      { id: 42, title: 'JavaScript - Objets', icon: '🧍' },
      { id: 43, title: 'JavaScript - Tableaux', icon: '🗃️' },
      { id: 44, title: 'JavaScript - Sets', icon: '🔢' },
      { id: 45, title: 'JavaScript - Maps', icon: '🗺️' },
      { id: 46, title: 'JavaScript - Math', icon: '🧮' },
      { id: 47, title: 'JavaScript - Regex', icon: '🔍' },
      { id: 48, title: 'JavaScript - Events', icon: '🎯' },
    ]
  }
};

const Sidebar = ({ open = false, onClose = () => {} }: SidebarProps) => {
  const { isAuthenticated, user, refreshUser } = useAuth();
  const learningContext = useLearningContext();
  const [progress, setProgress] = useState<UserProgress | null>(null);
  const [loading, setLoading] = useState(true);
  const [isAdminMenuOpen, setIsAdminMenuOpen] = useState(false);
  const [synced, setSynced] = useState(false);
  const [expandedCategories, setExpandedCategories] = useState<Record<string, boolean>>({
    HTML: true,
    CSS: false,
    JavaScript: false
  });

  const toggleCategory = (category: string) => {
    setExpandedCategories(prev => ({
      ...prev,
      [category]: !prev[category]
    }));
  };

  useEffect(() => {
    const syncUserProfile = async () => {
      if (isAuthenticated && user && !synced) {
        try {
          console.log('🔄 Synchronisation du profil utilisateur...');
          const response = await api.get('/recommend/sync-profile');
          console.log('✅ Profil synchronisé:', response.data);
          await refreshUser();
          setSynced(true);
        } catch (error) {
          console.error('Erreur synchronisation:', error);
        }
      }
    };
    syncUserProfile();
  }, [isAuthenticated, user, refreshUser, synced]);

  useEffect(() => {
    if (isAuthenticated) {
      const loadProgress = async () => {
        try {
          const data = await courseService.getUserProgress();
          setProgress(data);
        } catch (error) {
          console.error('Failed to load progress:', error);
        } finally {
          setLoading(false);
        }
      };
      loadProgress();
    } else {
      setLoading(false);
    }
  }, [isAuthenticated]);

  const closeSidebar = () => onClose();

  if (!isAuthenticated) {
    return (
      <>
        <aside className="hidden lg:block w-72 bg-white shadow-lg min-h-screen sticky top-16 overflow-y-auto">
          <SidebarContentNotAuth />
        </aside>
      </>
    );
  }

  if (loading) {
    return (
      <aside className="hidden lg:block w-72 bg-white shadow-lg min-h-screen sticky top-16">
        <div className="p-6">
          <div className="text-center py-8">
            <div className="inline-block w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
            <p className="text-gray-500 mt-3 text-sm">Chargement...</p>
          </div>
        </div>
      </aside>
    );
  }

  const modeScores = progress?.stats_par_mode || {
    texte: { nb_cours: 0, score_moyen: 0 },
    audio: { nb_cours: 0, score_moyen: 0 },
    video: { nb_cours: 0, score_moyen: 0 },
  };

  const coursComplets = progress?.cours_complets ?? 0;
  const scoreMoyen = progress?.score_moyen ?? 0;
  const progressionNiveau = progress?.progression_niveau ?? 0;

  const getBestMode = () => {
    const entries = Object.entries(modeScores);
    let best = { mode: 'texte', score: 0 };
    for (const [mode, stats] of entries) {
      const score = stats?.score_moyen ?? 0;
      if (score > best.score) {
        best = { mode, score };
      }
    }
    return best;
  };

  const bestMode = getBestMode();
  const bestModeIcon = bestMode.mode === 'texte' ? '📖' : bestMode.mode === 'audio' ? '🎧' : '🎬';
  const bestModeLabel = bestMode.mode === 'texte' ? 'Texte' : bestMode.mode === 'audio' ? 'Audio' : 'Vidéo';

  const getLearnerTypeDisplay = () => {
    const type = user?.type_apprenant || 'mixte';
    const labels: Record<string, { icon: string; label: string }> = {
      'visuel': { icon: '🎨', label: 'Visuel' },
      'auditif': { icon: '🎧', label: 'Auditif' },
      'lecture': { icon: '📖', label: 'Lecture' },
      'mixte': { icon: '🔄', label: 'Mixte' }
    };
    return labels[type] || labels['mixte'];
  };

  const learnerType = getLearnerTypeDisplay();

  const sidebarContent = (
    <div className="p-5">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-bold">📊 Tableau de bord</h3>
        <button
          onClick={closeSidebar}
          className="lg:hidden p-2 rounded-lg hover:bg-gray-100 text-gray-500 transition"
          aria-label="Fermer"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

     
      <div className="mb-5 p-4 bg-gray-50 rounded-xl">
        <p className="font-semibold text-sm">
          👤 {user?.prenom} {user?.nom}
        </p>
        <p className="text-xs text-gray-500 mt-0.5">{user?.email}</p>
        <div className="flex flex-wrap gap-2 mt-2">
          <span className="text-xs px-2 py-1 bg-purple-100 text-purple-700 rounded-full">
            {learnerType.icon} {learnerType.label}
          </span>
          {user?.niveau_global && (
            <span className="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded-full">
              {user.niveau_global === 'débutant' && '🌱 Débutant'}
              {user.niveau_global === 'intermédiaire' && '📚 Intermédiaire'}
              {user.niveau_global === 'avancé' && '🚀 Avancé'}
            </span>
          )}
        </div>
      </div>

     
      {bestMode.score > 0 && (
        <div className="mb-5 p-3 bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl">
          <p className="text-xs text-gray-500 mb-1">Votre meilleur format</p>
          <div className="flex items-center gap-2">
            <span className="text-2xl">{bestModeIcon}</span>
            <div>
              <p className="font-semibold capitalize">{bestModeLabel}</p>
              <p className="text-sm font-bold text-green-600">{bestMode.score.toFixed(1)}%</p>
            </div>
          </div>
        </div>
      )}

      
      <div className="mb-5">
        <UserBehaviorAnalysis />
      </div>

      <div className="mb-5">
        <DropoutPrediction />
      </div>

      <div className="mb-5">
        <BehaviorRiskAnalysis />
      </div>

      
      {user?.role_id === 1 && (
        <div className="mb-5 p-3 bg-red-50 rounded-xl">
          <button
            onClick={() => setIsAdminMenuOpen(!isAdminMenuOpen)}
            className="w-full flex items-center justify-between text-left font-semibold text-red-700"
          >
            <span>⚙️ Administration</span>
            <span>{isAdminMenuOpen ? '▲' : '▼'}</span>
          </button>
          
          {isAdminMenuOpen && (
            <div className="mt-3 space-y-2">
              <Link
                to="/admin/risk-monitor"
                onClick={closeSidebar}
                className="flex items-center gap-2 px-3 py-2 text-sm text-red-600 hover:bg-red-100 rounded-lg transition"
              >
                <span>📊</span> Monitoring des risques
              </Link>
              <Link
                to="/admin"
                onClick={closeSidebar}
                className="flex items-center gap-2 px-3 py-2 text-sm text-red-600 hover:bg-red-100 rounded-lg transition"
              >
                <span>🛠️</span> Dashboard Admin
              </Link>
            </div>
          )}
        </div>
      )}

      
      <div className="grid grid-cols-2 gap-2.5 mb-5">
        <div className="text-center p-3 bg-blue-50 rounded-xl">
          <div className="text-xl font-bold text-primary-600">{coursComplets}</div>
          <div className="text-[11px] text-gray-500 uppercase tracking-wider">Cours</div>
        </div>
        <div className="text-center p-3 bg-green-50 rounded-xl">
          <div className="text-xl font-bold text-green-600">{scoreMoyen.toFixed(1)}%</div>
          <div className="text-[11px] text-gray-500 uppercase tracking-wider">Score</div>
        </div>
      </div>

     
      <div className="mb-5">
        <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">
          Scores par format
        </h4>
        <div className="space-y-3">
          {Object.entries(modeScores).map(([mode, stats]) => (
            <div key={mode}>
              <div className="flex justify-between text-sm mb-1">
                <span>
                  {mode === 'texte' && '📖 Texte'}
                  {mode === 'audio' && '🎧 Audio'}
                  {mode === 'video' && '🎬 Vidéo'}
                  <span className="text-gray-400 ml-1 text-xs">({stats.nb_cours})</span>
                </span>
                <span className="font-bold text-sm">{(stats.score_moyen ?? 0).toFixed(1)}%</span>
              </div>
              <div className="bg-gray-200 h-1.5 rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-500"
                  style={{
                    width: `${stats.score_moyen ?? 0}%`,
                    backgroundColor: mode === 'texte' ? '#8B5CF6' : mode === 'audio' ? '#10B981' : '#EF4444'
                  }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      
      {progressionNiveau > 0 && (
        <div className="mb-5">
          <div className="flex justify-between text-sm mb-1">
            <span className="text-gray-600">Progression</span>
            <span className="font-semibold text-primary-600">{progressionNiveau}%</span>
          </div>
          <div className="bg-gray-200 h-2 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-primary-500 to-purple-500 rounded-full transition-all duration-500"
              style={{ width: `${Math.min(progressionNiveau, 100)}%` }}
            />
          </div>
        </div>
      )}

      
      <div className="mb-5 border-t border-gray-100 pt-5">
        <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">
          📚 Cours par catégorie
        </h4>
        
        
        <div className="grid grid-cols-3 gap-2 mb-4">
          {Object.entries(COURSE_CATEGORIES).map(([key, cat]) => (
            <button
              key={key}
              onClick={() => toggleCategory(key)}
              className={`px-2 py-2 rounded-xl text-center text-xs font-medium transition-colors ${cat.bgColor} ${cat.color} hover:opacity-80 relative`}
            >
              <div className="text-lg">{cat.icon}</div>
              <div>{key}</div>
              <div className="text-[10px] opacity-60 mt-0.5">
                {cat.courses.length} cours
              </div>
            </button>
          ))}
        </div>

       
        <div className="space-y-3 max-h-[400px] overflow-y-auto pr-1">
          {Object.entries(COURSE_CATEGORIES).map(([key, cat]) => {
            const isExpanded = expandedCategories[key] || false;
            
            return (
              <div key={key} className={`border ${cat.borderColor} rounded-xl overflow-hidden`}>
                <button
                  onClick={() => toggleCategory(key)}
                  className={`w-full flex items-center justify-between px-3 py-2.5 ${cat.bgColor} hover:opacity-90 transition`}
                >
                  <div className="flex items-center gap-2">
                    <span className="text-lg">{cat.icon}</span>
                    <span className={`font-semibold text-sm ${cat.color}`}>
                      {key}
                    </span>
                    <span className="text-xs text-gray-400 font-normal">
                      ({cat.courses.length} cours)
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={`text-gray-400 transition-transform duration-200 ${isExpanded ? 'rotate-180' : ''}`}>
                      ▼
                    </span>
                  </div>
                </button>
                
                {isExpanded && (
                  <div className="p-2 space-y-0.5 bg-white">
                    {cat.courses.map((course) => (
                      <Link
                        key={course.id}
                        to={`/learning/text/${course.id}`}
                        onClick={closeSidebar}
                        className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-gray-600 hover:bg-gray-50 hover:text-gray-800 transition-colors"
                      >
                        <span className="text-base">{course.icon}</span>
                        <span className="truncate flex-1">{course.title}</span>
                      </Link>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      
      <Link
        to="/recommendation"
        onClick={closeSidebar}
        className="w-full mb-5 px-4 py-2.5 bg-purple-500 text-white rounded-xl hover:bg-purple-600 transition text-sm font-medium text-center block"
      >
        🔍 Recommandations IA
      </Link>

      
      <div className="border-t border-gray-100 pt-5">
        <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">
          Accès rapide
        </h4>

        <div className="grid grid-cols-3 gap-2 mb-4">
          {[
            { to: '/learning/text', icon: '📖', label: 'Texte', color: 'hover:bg-violet-50 hover:text-violet-700' },
            { to: '/learning/audio', icon: '🎧', label: 'Audio', color: 'hover:bg-emerald-50 hover:text-emerald-700' },
            { to: '/learning/video', icon: '🎬', label: 'Vidéo', color: 'hover:bg-rose-50 hover:text-rose-700' },
          ].map(item => (
            <Link
              key={item.to}
              to={item.to}
              onClick={closeSidebar}
              className={`px-2 py-2.5 bg-gray-50 rounded-xl text-center text-xs font-medium transition-colors ${item.color}`}
            >
              <div className="text-lg mb-0.5">{item.icon}</div>
              {item.label}
            </Link>
          ))}
        </div>

        <nav className="space-y-1">
          {[
            { to: '/courses', icon: '📚', label: 'Catalogue des cours' },
            { to: '/level-test', icon: '📋', label: 'Test de niveau' },
            { to: '/progress', icon: '📊', label: 'Statistiques' },
            { to: '/quiz', icon: '🎯', label: 'Quiz' },
            { to: '/profile', icon: '⚙️', label: 'Mon profil' },
          ].map(item => (
            <Link
              key={item.to}
              to={item.to}
              onClick={closeSidebar}
              className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm text-gray-600 hover:bg-gray-50 hover:text-gray-800 transition-colors"
            >
              <span>{item.icon}</span>
              <span>{item.label}</span>
            </Link>
          ))}
        </nav>
      </div>

      
      {isAuthenticated && learningContext && (
        <div className="mt-4 pt-4 border-t border-gray-200 space-y-2">
          <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
            🎯 Actions d'apprentissage
          </h4>
          
          <button
            onClick={learningContext.generatePersonalizedQuiz}
            disabled={learningContext.isGeneratingQuiz || !learningContext.selectedCourseId}
            className="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition disabled:opacity-50 text-sm flex items-center justify-center gap-2"
          >
            {learningContext.isGeneratingQuiz ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                Génération...
              </>
            ) : (
              '🎯 Quiz Personnalisé'
            )}
          </button>

          <button
            onClick={learningContext.showTutorRecommendations}
            disabled={!learningContext.hasMistakes}
            className="w-full px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition disabled:opacity-50 text-sm flex items-center justify-center gap-2"
          >
            🤖 Tuteur IA - Recommandations
          </button>

          <button
            onClick={learningContext.showMistakeStats}
            className="w-full px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition text-sm flex items-center justify-center gap-2"
          >
            📊 Statistiques d'erreurs
          </button>

          <button
            onClick={learningContext.generateBertQuiz}
            disabled={learningContext.isGeneratingQuiz || !learningContext.selectedCourseId}
            className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50 text-sm flex items-center justify-center gap-2"
          >
            {learningContext.isGeneratingQuiz ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                Génération...
              </>
            ) : (
              '🤖 Générer Quiz IA'
            )}
          </button>

          {!learningContext.isExamMode ? (
            <button
              onClick={learningContext.generateExam}
              disabled={learningContext.isGeneratingExam || !learningContext.selectedCourseId}
              className="w-full px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition disabled:opacity-50 text-sm flex items-center justify-center gap-2"
            >
              {learningContext.isGeneratingExam ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  Génération...
                </>
              ) : (
                '📝 Examen final'
              )}
            </button>
          ) : (
            <button
              onClick={learningContext.cancelExam}
              className="w-full px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition text-sm flex items-center justify-center gap-2"
            >
              ❌ Annuler l'examen
            </button>
          )}

         
          {learningContext.hasMistakes && (
            <div className="text-xs text-center text-orange-600 bg-orange-50 p-2 rounded-lg">
              📝 {learningContext.hasMistakes ? 'Erreurs enregistrées' : 'Aucune erreur'}
            </div>
          )}
          {learningContext.isExamMode && (
            <div className="text-xs text-center text-purple-600 bg-purple-50 p-2 rounded-lg">
              📝 Mode examen actif
            </div>
          )}
        </div>
      )}
    </div>
  );

  return (
    <>
      <aside className="hidden lg:block w-72 bg-white shadow-lg min-h-screen sticky top-16 overflow-y-auto">
        {sidebarContent}
      </aside>

      {open && (
        <div className="lg:hidden fixed inset-0 bg-black/30 backdrop-blur-sm z-40" onClick={closeSidebar} />
      )}

      <aside
        className={`lg:hidden fixed top-16 left-0 bottom-0 w-80 max-w-[85vw] bg-white shadow-2xl z-50 transform transition-transform duration-300 ease-in-out overflow-y-auto ${
          open ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {sidebarContent}
      </aside>
    </>
  );
};

const SidebarContentNotAuth = () => {
  return (
    <div className="p-6">
      <h3 className="text-lg font-semibold mb-4">🔐 Connexion requise</h3>
      <p className="text-gray-600 mb-5 text-sm">
        Connectez-vous pour accéder à votre tableau de bord
      </p>
      <Link
        to="/login"
        className="block w-full text-center px-4 py-2.5 bg-primary-500 text-white rounded-xl hover:bg-primary-600 mb-2 text-sm font-medium transition"
      >
        🔐 Connexion
      </Link>
      <Link
        to="/register"
        className="block w-full text-center px-4 py-2.5 bg-green-500 text-white rounded-xl hover:bg-green-600 text-sm font-medium transition"
      >
        📝 Inscription
      </Link>
      <div className="mt-8 pt-6 border-t border-gray-100">
        <h4 className="font-semibold mb-2 text-sm">🎮 Mode Démo</h4>
        <p className="text-gray-500 text-xs mb-3">
          Explorez la plateforme sans créer de compte
        </p>
        <button className="w-full px-4 py-2.5 bg-purple-500 text-white rounded-xl hover:bg-purple-600 text-sm font-medium transition">
          🚀 Essayer
        </button>
      </div>
    </div>
  );
};

export default Sidebar;