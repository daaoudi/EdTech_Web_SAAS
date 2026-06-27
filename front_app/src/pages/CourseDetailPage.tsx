/* eslint-disable react-hooks/exhaustive-deps */
 
import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { courseService } from '../services/courseService';
import type { Course } from '../services/courseService';
import { useAuth } from '../contexts/AuthContext';

const CourseDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [course, setCourse] = useState<Course | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (id) {
      loadCourse();
    } else {
      setError("ID du cours non spécifié");
      setLoading(false);
    }
  }, [id]);

  const loadCourse = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await courseService.getCourseById(Number(id));
      
      if (data && Object.keys(data).length > 0) {
        setCourse(data);
      } else {
        setError("Cours non trouvé");
        
        setCourse({
          id: Number(id),
          titre: 'Cours HTML',
          description: 'Contenu du cours à venir',
          difficulte: 'débutant',
          contenu: '<p>Le contenu de ce cours sera bientôt disponible.</p>',
          duree: 60,
        });
      }
    } catch (error) {
      console.error('Error loading course:', error);
      setError("Impossible de charger le cours");
      
      setCourse({
        id: Number(id),
        titre: 'Introduction au HTML',
        description: 'Ce cours vous apprendra les bases du HTML, la structure d\'une page web, et les balises essentielles.',
        difficulte: 'débutant',
        contenu: `
          <h2>Chapitre 1: Introduction</h2>
          <p>HTML (HyperText Markup Language) est le langage standard pour créer des pages web.</p>
          <h2>Chapitre 2: Structure de base</h2>
          <p>Une page HTML commence par une déclaration DOCTYPE, suivie des balises html, head et body.</p>
          <h2>Chapitre 3: Balises essentielles</h2>
          <p>Les balises les plus importantes sont: h1 à h6 pour les titres, p pour les paragraphes, a pour les liens, img pour les images.</p>
          <h2>Exemple de code</h2>
          <pre><code>&lt;!DOCTYPE html&gt;
&lt;html&gt;
&lt;head&gt;
    &lt;title&gt;Ma première page&lt;/title&gt;
&lt;/head&gt;
&lt;body&gt;
    &lt;h1&gt;Bonjour le monde !&lt;/h1&gt;
    &lt;p&gt;Ceci est mon premier paragraphe en HTML.&lt;/p&gt;
&lt;/body&gt;
&lt;/html&gt;</code></pre>
        `,
        duree: 120,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleStartLearning = (mode: string) => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    
    
    localStorage.setItem('currentCourse', JSON.stringify({
      id: course?.id,
      titre: course?.titre,
      mode: mode
    }));
    
    
    navigate(`/learning/${mode}`);
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="text-4xl mb-4">📚</div>
          <div className="text-xl text-gray-600">Chargement du cours...</div>
        </div>
      </div>
    );
  }

  if (error && !course) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="text-4xl mb-4">⚠️</div>
          <div className="text-xl text-red-600 mb-4">{error}</div>
          <button
            onClick={() => navigate('/courses')}
            className="px-6 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600"
          >
            Retour aux cours
          </button>
        </div>
      </div>
    );
  }

  if (!course) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="text-4xl mb-4">📖</div>
          <div className="text-xl text-gray-600 mb-4">Cours non trouvé</div>
          <button
            onClick={() => navigate('/courses')}
            className="px-6 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600"
          >
            Voir tous les cours
          </button>
        </div>
      </div>
    );
  }

  
  const getDifficultyColor = (difficulte: string) => {
    const colors = {
      débutant: 'bg-green-100 text-green-800',
      intermédiaire: 'bg-yellow-100 text-yellow-800',
      avancé: 'bg-red-100 text-red-800',
    };
    return colors[difficulte as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  };

  
  const getDifficultyText = (difficulte: string) => {
    const texts = {
      débutant: '🟢 Débutant',
      intermédiaire: '🟡 Intermédiaire',
      avancé: '🔴 Avancé',
    };
    return texts[difficulte as keyof typeof texts] || difficulte;
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-fade-in">
      <button
        onClick={() => navigate('/courses')}
        className="flex items-center text-primary-500 hover:text-primary-700 transition-colors mb-4"
      >
        ← Retour aux cours
      </button>

      <div className="bg-white rounded-xl shadow-lg overflow-hidden">
        
        <div className="bg-gradient-to-r from-primary-600 to-primary-800 px-8 py-6 text-white">
          <span className={`inline-block px-3 py-1 rounded-full text-sm font-semibold mb-4 ${getDifficultyColor(course.difficulte)}`}>
            {getDifficultyText(course.difficulte)}
          </span>
          <h1 className="text-3xl font-bold mb-4">{course.titre}</h1>
          <p className="text-white/90 text-lg">{course.description}</p>
          {course.duree && (
            <div className="flex items-center gap-4 mt-4 text-white/80 text-sm">
              <span>⏱️ Durée: {Math.floor(course.duree / 60)}h{course.duree % 60 > 0 ? `${course.duree % 60}min` : ''}</span>
              <span>📚 Niveau: {course.difficulte}</span>
            </div>
          )}
        </div>

        
        <div className="p-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-4 flex items-center gap-2">
            <span>📖</span> Contenu du cours
          </h2>
          <div 
            className="prose prose-lg max-w-none prose-headings:text-gray-800 prose-p:text-gray-600 prose-strong:text-gray-800 prose-code:bg-gray-100 prose-code:p-1 prose-code:rounded"
            dangerouslySetInnerHTML={{ __html: course.contenu || '<p>Le contenu de ce cours sera bientôt disponible.</p>' }}
          />
        </div>

        
        <div className="bg-gray-50 px-8 py-6 border-t">
          <h2 className="text-xl font-bold text-gray-800 mb-4 text-center">
            Choisissez votre mode d'apprentissage
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button
              onClick={() => handleStartLearning('text')}
              className="flex flex-col items-center gap-2 px-6 py-4 bg-gradient-to-r from-green-500 to-green-600 text-white rounded-xl hover:from-green-600 hover:to-green-700 transition-all transform hover:scale-105"
            >
              <span className="text-3xl">📖</span>
              <span className="font-semibold">Mode Texte</span>
              <span className="text-sm opacity-90">Apprentissage par la lecture</span>
            </button>
            <button
              onClick={() => handleStartLearning('audio')}
              className="flex flex-col items-center gap-2 px-6 py-4 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-xl hover:from-blue-600 hover:to-blue-700 transition-all transform hover:scale-105"
            >
              <span className="text-3xl">🎧</span>
              <span className="font-semibold">Mode Audio</span>
              <span className="text-sm opacity-90">Apprentissage par l'écoute</span>
            </button>
            <button
              onClick={() => handleStartLearning('video')}
              className="flex flex-col items-center gap-2 px-6 py-4 bg-gradient-to-r from-purple-500 to-purple-600 text-white rounded-xl hover:from-purple-600 hover:to-purple-700 transition-all transform hover:scale-105"
            >
              <span className="text-3xl">🎬</span>
              <span className="font-semibold">Mode Vidéo</span>
              <span className="text-sm opacity-90">Apprentissage par la vidéo</span>
            </button>
          </div>
          {!isAuthenticated && (
            <p className="text-center text-amber-600 text-sm mt-4">
              ⚠️ Vous devez être connecté pour commencer l'apprentissage
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

export default CourseDetailPage;