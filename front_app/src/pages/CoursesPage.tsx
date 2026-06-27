/* eslint-disable react-hooks/exhaustive-deps */

import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { courseService } from '../services/courseService';
import type { Course } from '../services/courseService';
import SearchBar from '../components/SearchBar';
import type { VoiceSearchResult } from '../services/voiceSearchService';

const CoursesPage = () => {
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [error, setError] = useState<string | null>(null);
  const [searchResults, setSearchResults] = useState<VoiceSearchResult[] | null>(null);
  const [isSearching, setIsSearching] = useState(false);

  useEffect(() => {
    loadCourses();
  }, []);

  const loadCourses = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await courseService.getAllCourses();
      
      
      const activeCourses = data.filter(course => course.est_actif !== false);
      
      
      const normalizedCourses = activeCourses.map(course => ({
        ...course,
        difficulte: normalizeDifficulty(course.difficulte)
      }));
      
      setCourses(normalizedCourses);
    } catch (error) {
      console.error('Erreur chargement cours:', error);
      setError('Impossible de charger les cours. Veuillez réessayer plus tard.');
      setCourses([
        { 
          id: 6, 
          titre: 'Formatage du Texte en HTML', 
          difficulte: 'débutant', 
          description: 'Apprenez les bases du formatage de texte en HTML', 
          duree: 15,
          tags: ['html', 'texte', 'debutant']
        },
        { 
          id: 11, 
          titre: 'Les Liens Hypertextes en HTML', 
          difficulte: 'débutant', 
          description: 'Maîtrisez la création de liens hypertextes', 
          duree: 25,
          tags: ['html', 'liens', 'navigation']
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  
  const normalizeDifficulty = (difficulte: string): string => {
    const difficultyMap: Record<string, string> = {
      'debutant': 'débutant',
      'débutant': 'débutant',
      'intermediaire': 'intermédiaire',
      'intermédiaire': 'intermédiaire',
      'avance': 'avancé',
      'avancé': 'avancé'
    };
    return difficultyMap[difficulte?.toLowerCase()] || 'débutant';
  };

  const handleSearch = (results: VoiceSearchResult[]) => {
    setSearchResults(results);
    setIsSearching(true);
  };

  const clearSearch = () => {
    setSearchResults(null);
    setIsSearching(false);
  };

  
  const getDisplayCourses = (): Course[] => {
    if (!searchResults) return courses;
    
    return searchResults.map(result => ({
      id: result.id,
      titre: result.titre,
      description: result.description,
      difficulte: normalizeDifficulty(result.difficulte),
      tags: result.tags,
      duree: result.duree || 0,
      est_actif: true
    }));
  };

  const displayedCourses = getDisplayCourses();
  
  
  const matchesFilter = (course: Course): boolean => {
    if (filter === 'all') return true;
    
    const courseDifficulty = course.difficulte?.toLowerCase() || '';
    const filterDifficulty = filter.toLowerCase();
    
    
    const difficultyMapping: Record<string, string[]> = {
      'débutant': ['débutant', 'debutant', 'facile', 'base'],
      'intermédiaire': ['intermédiaire', 'intermediaire', 'moyen'],
      'avancé': ['avancé', 'avance', 'difficile', 'expert']
    };
    
    const filterVariations = difficultyMapping[filterDifficulty] || [filterDifficulty];
    return filterVariations.some(variation => courseDifficulty.includes(variation));
  };
  
  const filteredCourses = displayedCourses.filter(course => matchesFilter(course));

  
  const countByDifficulty = (difficulty: string): number => {
    const variations: Record<string, string[]> = {
      'débutant': ['débutant', 'debutant', 'facile', 'base'],
      'intermédiaire': ['intermédiaire', 'intermediaire', 'moyen'],
      'avancé': ['avancé', 'avance', 'difficile', 'expert']
    };
    
    return displayedCourses.filter(course => {
      const courseDiff = course.difficulte?.toLowerCase() || '';
      return variations[difficulty].some(v => courseDiff.includes(v));
    }).length;
  };

  const getDifficultyColor = (difficulte: string) => {
    const colors = {
      'débutant': 'bg-green-100 text-green-800',
      'debutant': 'bg-green-100 text-green-800',
      'intermédiaire': 'bg-yellow-100 text-yellow-800',
      'intermediaire': 'bg-yellow-100 text-yellow-800',
      'avancé': 'bg-red-100 text-red-800',
      'avance': 'bg-red-100 text-red-800'
    };
    const key = difficulte?.toLowerCase() || '';
    return colors[key as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  };

  const getDifficultyLabel = (difficulte: string) => {
    const labels = {
      'débutant': '🟢 Débutant',
      'debutant': '🟢 Débutant',
      'intermédiaire': '🟡 Intermédiaire',
      'intermediaire': '🟡 Intermédiaire',
      'avancé': '🔴 Avancé',
      'avance': '🔴 Avancé'
    };
    const key = difficulte?.toLowerCase() || '';
    return labels[key as keyof typeof labels] || difficulte;
  };

  const formatDuration = (duree: number) => {
    if (!duree) return 'Durée non spécifiée';
    if (duree < 60) {
      return `${duree} min`;
    }
    const heures = Math.floor(duree / 60);
    const minutes = duree % 60;
    if (minutes === 0) {
      return `${heures} h`;
    }
    return `${heures} h ${minutes} min`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="text-4xl mb-4">📚</div>
          <div className="text-xl text-gray-600">Chargement des cours...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="text-4xl mb-4">⚠️</div>
          <div className="text-xl text-red-600 mb-4">{error}</div>
          <button
            onClick={loadCourses}
            className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600"
          >
            Réessayer
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
     
      <div className="flex flex-col items-center space-y-4">
        <SearchBar onSearch={handleSearch} placeholder="🔍 Rechercher un cours par texte ou par voix..." />
        {isSearching && searchResults && (
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-500">
              {searchResults.length} résultat(s) trouvé(s)
            </span>
            <button
              onClick={clearSearch}
              className="text-sm text-primary-500 hover:text-primary-700 transition-colors"
            >
              ✖ Effacer la recherche
            </button>
          </div>
        )}
      </div>

      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <h1 className="text-3xl font-bold text-primary-800">
          {isSearching ? '🔍 Résultats de recherche' : '📚 Catalogue des cours'}
        </h1>
        
        <div className="flex gap-2 flex-wrap">
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-2 rounded-lg transition ${filter === 'all' ? 'bg-primary-500 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'}`}
          >
            Tous ({displayedCourses.length})
          </button>
          <button
            onClick={() => setFilter('débutant')}
            className={`px-4 py-2 rounded-lg transition ${filter === 'débutant' ? 'bg-green-500 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'}`}
          >
            Débutant ({countByDifficulty('débutant')})
          </button>
          <button
            onClick={() => setFilter('intermédiaire')}
            className={`px-4 py-2 rounded-lg transition ${filter === 'intermédiaire' ? 'bg-yellow-500 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'}`}
          >
            Intermédiaire ({countByDifficulty('intermédiaire')})
          </button>
          <button
            onClick={() => setFilter('avancé')}
            className={`px-4 py-2 rounded-lg transition ${filter === 'avancé' ? 'bg-red-500 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'}`}
          >
            Avancé ({countByDifficulty('avancé')})
          </button>
        </div>
      </div>

      {filteredCourses.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-xl">
          {isSearching ? (
            <>
              <p className="text-gray-500">Aucun résultat trouvé pour votre recherche.</p>
              <p className="text-sm text-gray-400 mt-2">Essayez d'autres mots-clés</p>
            </>
          ) : (
            <p className="text-gray-500">Aucun cours disponible pour ce niveau.</p>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredCourses.map(course => (
            <div key={course.id} className="bg-white rounded-xl shadow-md overflow-hidden hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1">
              <div className="p-6">
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-xl font-semibold text-gray-800 line-clamp-2">{course.titre}</h3>
                  <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getDifficultyColor(course.difficulte)}`}>
                    {getDifficultyLabel(course.difficulte)}
                  </span>
                </div>
                <p className="text-gray-600 mb-4 line-clamp-3">{course.description || 'Aucune description disponible'}</p>
                {course.duree && course.duree > 0 && (
                  <p className="text-sm text-gray-500 mb-4 flex items-center gap-1">
                    <span>⏱️</span> {formatDuration(course.duree)}
                  </p>
                )}
                {course.tags && course.tags.length > 0 && (
                  <div className="flex flex-wrap gap-1 mb-4">
                    {course.tags.slice(0, 3).map((tag, idx) => (
                      <span key={idx} className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full">
                        {tag}
                      </span>
                    ))}
                    {course.tags.length > 3 && (
                      <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full">
                        +{course.tags.length - 3}
                      </span>
                    )}
                  </div>
                )}
                <Link
                  to={`/course/${course.id}`}
                  className="inline-block w-full text-center px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
                >
                  Commencer le cours
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default CoursesPage;