/* eslint-disable @typescript-eslint/no-unused-vars */
/* eslint-disable react-hooks/immutability */
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { courseService } from '../services/courseService';
import type { Course } from '../services/courseService';

const HomePage = () => {
  const { isAuthenticated } = useAuth();
  const [courses, setCourses] = useState<Course[]>([]);
  const [apiStatus, setApiStatus] = useState<'loading' | 'connected' | 'disconnected'>('loading');

  useEffect(() => {
    checkApiHealth();
    loadCourses();
  }, []);

  const checkApiHealth = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8001/health');
      if (response.ok) {
        setApiStatus('connected');
      } else {
        setApiStatus('disconnected');
      }
    } catch {
      setApiStatus('disconnected');
    }
  };

  const loadCourses = async () => {
    try {
      const data = await courseService.getAllCourses();
      setCourses(data.slice(0, 3));
    } catch (error) {
      
      setCourses([
        { id: 1, titre: 'Introduction au HTML', difficulte: 'débutant', description: 'Apprenez les bases du HTML' },
        { id: 2, titre: 'Formulaires HTML', difficulte: 'intermédiaire', description: 'Créez des formulaires interactifs' },
        { id: 3, titre: 'HTML5 Avancé', difficulte: 'avancé', description: 'Maîtrisez les nouvelles fonctionnalités HTML5' },
      ]);
    }
  };

  const getDifficultyBadge = (difficulte: string) => {
    const badges = {
      débutant: 'badge-beginner',
      intermédiaire: 'badge-intermediate',
      avancé: 'badge-advanced',
    };
    return badges[difficulte as keyof typeof badges] || 'badge-beginner';
  };

  return (
    <div className="space-y-12 animate-fade-in">
      
      {apiStatus === 'disconnected' && (
        <div className="bg-yellow-100 border-l-4 border-yellow-500 p-4 rounded">
          <p className="text-yellow-700">
            ⚠️ L'API backend n'est pas accessible. Assurez-vous que le backend est en cours d'exécution sur http://127.0.0.1:8001
          </p>
        </div>
      )}
      
      {apiStatus === 'connected' && (
        <div className="bg-green-100 border-l-4 border-green-500 p-4 rounded">
          <p className="text-green-700">✅ API connectée</p>
        </div>
      )}

      
      <div className="feature-card">
        <h2 className="text-3xl font-bold mb-4">📖 Bienvenue sur la Plateforme d'Apprentissage HTML Intelligente</h2>
        <p className="text-lg opacity-90 mb-6">
          Découvrez une nouvelle façon d'apprendre le HTML grâce à notre plateforme adaptative qui s'ajuste 
          à votre style d'apprentissage préféré : texte, audio ou vidéo.
        </p>
        <div className="flex gap-2 flex-wrap">
          <span className="badge badge-intelligent">IA Intelligente</span>
          <span className="badge badge-personnalise">Personnalisation</span>
          <span className="badge bg-purple-500">Innovation</span>
          <span className="badge bg-blue-500">Facile à utiliser</span>
        </div>
      </div>

      
      <div>
        <h2 className="text-2xl font-bold text-primary-800 mb-6 border-b-2 border-primary-800 pb-2">
          📊 Aperçu de la Plateforme
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="stat-box">
            <div className="stat-number">{courses.length}+</div>
            <div className="stat-label">Cours HTML</div>
          </div>
          <div className="stat-box">
            <div className="stat-number">3</div>
            <div className="stat-label">Modes d'Apprentissage</div>
          </div>
          <div className="stat-box">
            <div className="stat-number">100+</div>
            <div className="stat-label">Quiz Interactifs</div>
          </div>
          <div className="stat-box">
            <div className="stat-number">{apiStatus === 'connected' ? '✅' : '❌'}</div>
            <div className="stat-label">API {apiStatus === 'connected' ? 'Connectée' : 'Déconnectée'}</div>
          </div>
        </div>
      </div>

      
      <div>
        <h2 className="text-2xl font-bold text-primary-800 mb-6 border-b-2 border-primary-800 pb-2">
          ✨ Fonctionnalités Principales
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="learning-card">
            <h3 className="text-xl font-semibold mb-3">🎯 Apprentissage Adaptatif</h3>
            <p className="text-gray-300">Notre IA analyse vos performances et recommande le mode d'apprentissage optimal pour vous.</p>
            <div className="mt-4 flex gap-2">
              <span className="badge badge-intelligent">Intelligent</span>
              <span className="badge badge-personnalise">Personnalisé</span>
            </div>
          </div>
          <div className="learning-card">
            <h3 className="text-xl font-semibold mb-3">🔍 Multi-modes</h3>
            <p className="text-gray-300">Choisissez entre texte, audio ou vidéo selon vos préférences d'apprentissage.</p>
            <div className="mt-4 flex gap-2">
              <span className="badge bg-purple-500">Innovant</span>
              <span className="badge bg-blue-500">Flexible</span>
            </div>
          </div>
          <div className="learning-card">
            <h3 className="text-xl font-semibold mb-3">📈 Suivi Intelligent</h3>
            <p className="text-gray-300">Visualisez votre progression avec des statistiques détaillées et des recommandations.</p>
            <div className="mt-4 flex gap-2">
              <span className="badge bg-indigo-500">Analytique</span>
              <span className="badge bg-pink-500">Motivant</span>
            </div>
          </div>
        </div>
      </div>

      
      <div>
        <h2 className="text-2xl font-bold text-primary-800 mb-6 border-b-2 border-primary-800 pb-2">
          🎯 Nos 3 Approches d'Apprentissage HTML
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-gradient-to-br from-green-500 to-green-700 rounded-2xl p-6 text-white text-center transform transition hover:scale-105">
            <div className="text-6xl mb-4">📝</div>
            <h3 className="text-xl font-bold mb-3">Mode Texte</h3>
            <p className="mb-4">Pour les apprenants visuels/lecteurs</p>
            <ul className="text-left text-sm space-y-2">
              <li>✓ Contenu écrit structuré</li>
              <li>✓ Exemples de code interactifs</li>
              <li>✓ Exercices pratiques</li>
              <li>✓ Références complètes</li>
            </ul>
          </div>
          <div className="bg-gradient-to-br from-blue-500 to-blue-700 rounded-2xl p-6 text-white text-center transform transition hover:scale-105">
            <div className="text-6xl mb-4">🎧</div>
            <h3 className="text-xl font-bold mb-3">Mode Audio</h3>
            <p className="mb-4">Pour les apprenants auditifs</p>
            <ul className="text-left text-sm space-y-2">
              <li>✓ Narration vocale des cours</li>
              <li>✓ Podcasts éducatifs</li>
              <li>✓ Explications audio</li>
              <li>✓ Écoute en déplacement</li>
            </ul>
          </div>
          <div className="bg-gradient-to-br from-purple-500 to-purple-700 rounded-2xl p-6 text-white text-center transform transition hover:scale-105">
            <div className="text-6xl mb-4">📹</div>
            <h3 className="text-xl font-bold mb-3">Mode Vidéo</h3>
            <p className="mb-4">Pour les apprenants visuels</p>
            <ul className="text-left text-sm space-y-2">
              <li>✓ Tutoriels vidéo</li>
              <li>✓ Démonstrations en direct</li>
              <li>✓ Animations explicatives</li>
              <li>✓ Screen casting</li>
            </ul>
          </div>
        </div>
      </div>

      
      <div>
        <h2 className="text-2xl font-bold text-primary-800 mb-6 border-b-2 border-primary-800 pb-2">
          📚 Cours Disponibles
        </h2>
        <div className="space-y-4">
          {courses.map(course => (
            <div key={course.id} className="course-card flex justify-between items-center">
              <div>
                <h3 className="text-xl font-semibold mb-2">{course.titre}</h3>
                <p className="text-gray-600 mb-2">{course.description}</p>
                <span className={`badge ${getDifficultyBadge(course.difficulte)}`}>
                  {course.difficulte}
                </span>
              </div>
              <Link
                to={isAuthenticated ? `/course/${course.id}` : '/login'}
                className="px-6 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600"
              >
                Voir
              </Link>
            </div>
          ))}
        </div>
        {courses.length > 0 && (
          <Link
            to={isAuthenticated ? '/courses' : '/login'}
            className="block w-full mt-4 text-center px-6 py-3 bg-gray-800 text-white rounded-lg hover:bg-gray-900"
          >
            Voir tous les cours
          </Link>
        )}
      </div>

      
      <div>
        <h2 className="text-2xl font-bold text-primary-800 mb-6 border-b-2 border-primary-800 pb-2">
          💬 Témoignages d'Étudiants
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[
            { name: "Hanane Jaadi", role: "Développeuse frontend", comment: "Grâce au mode vidéo, j'ai enfin compris les concepts complexes du HTML5. La plateforme s'adapte vraiment à mon rythme !", stars: 5 },
            { name: "Bilal Baadi", role: "Étudiant en informatique", comment: "Le mode texte est parfait pour moi qui préfère lire. Les exemples de code interactifs sont géniaux !", stars: 5 },
            { name: "Hakim Jardi", role: "Designer UI/UX", comment: "J'écoute les cours en audio pendant mes trajets. C'est révolutionnaire pour apprendre en multitâche !", stars: 4 },
          ].map((t, idx) => (
            <div key={idx} className="learning-card">
              <h4 className="font-semibold">{t.name}</h4>
              <p className="text-gray-400 text-sm mb-3">{t.role}</p>
              <p className="text-gray-300 mb-3">"{t.comment}"</p>
              <p className="text-yellow-500 text-lg">{'⭐'.repeat(t.stars)}</p>
            </div>
          ))}
        </div>
      </div>

      
      <div className="bg-gradient-to-r from-primary-800 to-primary-500 rounded-2xl p-8 text-white text-center">
        <h2 className="text-2xl font-bold mb-4">🎯 Prêt à commencer votre apprentissage HTML ?</h2>
        <p className="text-lg mb-6">
          Rejoignez des milliers d'étudiants qui ont transformé leur façon d'apprendre le développement web.
        </p>
        <Link
          to={isAuthenticated ? '/courses' : '/register'}
          className="inline-block px-8 py-3 bg-white text-primary-600 rounded-lg font-semibold hover:bg-gray-100 transition"
        >
          {isAuthenticated ? '📚 Continuer l\'apprentissage' : '🚀 Commencer gratuitement'}
        </Link>
      </div>
    </div>
  );
};

export default HomePage;