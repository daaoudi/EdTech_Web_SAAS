/* eslint-disable @typescript-eslint/no-unused-vars */
/* eslint-disable react-hooks/exhaustive-deps */
/* eslint-disable @typescript-eslint/no-explicit-any */
/* eslint-disable */

import { useState, useEffect ,useCallback} from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { courseService } from '../services/courseService';
import type { Course } from '../services/courseService';
import api from '../services/api';
import { bertQuizService, bertRecommendationService } from '../services/bertService';
import { mistakeService } from '../services/mistakeService';
import { LearningProvider, LearningContextType } from '../contexts/LearningContext';
import { useOutletContext } from 'react-router-dom';


const getCourseCategories = () => {
  return {
    HTML: {
      id: 'html',
      icon: '📄',
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
      borderColor: 'border-orange-200',
      courses: [
        { id: 6, title: 'Formatage du Texte en HTML' },
        { id: 11, title: 'Les Liens Hypertextes en HTML' },
        { id: 12, title: 'Images en HTML' },
        { id: 8, title: 'Formulaires HTML Avancés' },
        { id: 13, title: 'Les Tableaux en HTML' },
        { id: 14, title: 'HTML Head - Métadonnées' },
        { id: 15, title: 'HTML Multimédia' },
        { id: 9, title: 'HTML5 Sémantique' },
      ]
    },
    CSS: {
      id: 'css',
      icon: '🎨',
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-200',
      courses: [
        { id: 16, title: 'CSS Media Queries' },
        { id: 17, title: 'CSS - Sélecteurs' },
        { id: 18, title: 'CSS - Couleurs' },
        { id: 19, title: 'CSS - Arrière-plans' },
        { id: 20, title: 'CSS - Bordures' },
        { id: 22, title: 'CSS - Marges' },
        { id: 23, title: 'CSS - Padding' },
        { id: 24, title: 'CSS - Texte' },
        { id: 25, title: 'CSS - Polices' },
        { id: 26, title: 'CSS - Liens' },
        { id: 27, title: 'CSS - Listes' },
        { id: 28, title: 'CSS - Tableaux' },
        { id: 29, title: 'CSS - Display & Visibility' },
        { id: 30, title: 'CSS - Positionnement' },
        { id: 31, title: 'CSS - Overflow' },
        { id: 32, title: 'CSS - Float' },
        { id: 10, title: 'CSS Flexbox & Grid' },
      ]
    },
    JavaScript: {
      id: 'js',
      icon: '🚀',
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-50',
      borderColor: 'border-yellow-200',
      courses: [
        { id: 33, title: 'JavaScript - Introduction' },
        { id: 34, title: 'JavaScript - Variables' },
        { id: 35, title: 'JavaScript - Types de Données' },
        { id: 36, title: 'JavaScript - Opérateurs' },
        { id: 37, title: 'JavaScript - Conditions' },
        { id: 38, title: 'JavaScript - Boucles' },
        { id: 39, title: 'JavaScript - Chaînes' },
        { id: 40, title: 'JavaScript - Nombres' },
        { id: 41, title: 'JavaScript - Fonctions' },
        { id: 42, title: 'JavaScript - Objets' },
        { id: 43, title: 'JavaScript - Tableaux' },
        { id: 44, title: 'JavaScript - Sets' },
        { id: 45, title: 'JavaScript - Maps' },
        { id: 46, title: 'JavaScript - Math' },
        { id: 47, title: 'JavaScript - Regex' },
        { id: 48, title: 'JavaScript - Events' },
      ]
    }
  };
};


const getCourseIcon = (courseId: number): string => {
  const categories = getCourseCategories();
  for (const cat of Object.values(categories)) {
    for (const c of cat.courses) {
      if (c.id === courseId) {
        if (courseId === 6) return '📝';
        if (courseId === 11) return '🔗';
        if (courseId === 12) return '🖼️';
        if (courseId === 8) return '📝';
        if (courseId === 9) return '🏗️';
        if (courseId === 10) return '🎨';
        if (courseId >= 17 && courseId <= 32) return '🎨';
        if (courseId >= 33 && courseId <= 48) return '🚀';
        return '📖';
      }
    }
  }
  return '📖';
};


interface Question {
  id: number;
  question: string;
  options: Record<string, string>;
  reponse_correcte: string;
  points: number;
  difficulte: string;
  explication?: string;
  score?: number;
}

interface Recommendation {
  cours_id: string;
  cours_titre: string;
  score: number;
  description: string;
  direct_match: boolean;
  nb_erreurs: number;
}

interface ExamAnswer {
  questionId: number;
  questionText: string;
  selectedAnswer: string;
  isCorrect: boolean;
  correctAnswer: string;
  explanation: string;
}


const FALLBACK_OPTIONS: Record<string, Record<string, string>> = {
  "Quelle balise HTML5 est utilisée pour surligner du texte ?": {
    A: "<mark>", B: "<highlight>", C: "<strong>", D: "<em>"
  },
  "Quelles balises HTML5 permettent de créer du contenu pliable/dépliable ?": {
    A: "<details> et <summary>", B: "<collapse> et <expand>", 
    C: "<fold> et <unfold>", D: "<hide> et <show>"
  },
  "Quel est l'avantage principal des balises sémantiques HTML5 ?": {
    A: "Meilleur SEO et accessibilité", B: "Chargement plus rapide",
    C: "Design plus joli", D: "Compatibilité avec plus de navigateurs"
  },
  "Comment modifier le contenu texte d'un element HTML en JavaScript ?": {
    A: "element.value = nouveauTexte",
    B: "element.innerHTML = nouveauTexte",
    C: "element.text = nouveauTexte",
    D: "element.content = nouveauTexte"
  },
  "Quelle balise utiliser pour le titre principal d'une page HTML ?": {
    A: "<title>", B: "<h1>", C: "<head>", D: "<header>"
  },
  "Quelle balise HTML est utilisée pour créer un lien hypertexte ?": {
    A: "<link>", B: "<a>", C: "<href>", D: "<url>"
  },
  "Quel attribut spécifie l'URL d'un lien ?": {
    A: "src", B: "url", C: "href", D: "link"
  },
  "Comment créer un lien qui s'ouvre dans un nouvel onglet ?": {
    A: "target='_self'", B: "target='_blank'", C: "target='_new'", D: "target='_top'"
  }
};




function getDefaultOptionsForQuestion(question: string): Record<string, string> {
  if (!question || typeof question !== 'string') {
    return { A: "Option A", B: "Option B", C: "Option C", D: "Option D" };
  }
  
  if (question.includes("modifier le contenu texte") || question.includes("innerHTML") || question.includes("JavaScript")) {
    return {
      A: "element.value = nouveauTexte",
      B: "element.innerHTML = nouveauTexte",
      C: "element.text = nouveauTexte",
      D: "element.content = nouveauTexte"
    };
  }
  
  for (const [key, options] of Object.entries(FALLBACK_OPTIONS)) {
    if (question.includes(key.substring(0, 30)) || key.includes(question.substring(0, 30))) {
      return options;
    }
  }
  
  return { A: "Option A", B: "Option B", C: "Option C", D: "Option D" };
}

const TextLearningPage = () => {
  const { isAuthenticated, user } = useAuth();
  const [courses, setCourses] = useState<Course[]>([]);
  const [selectedCourse, setSelectedCourse] = useState<Course | null>(null);
  const [loading, setLoading] = useState(true);
  const [readingProgress, setReadingProgress] = useState(0);
  
  const { courseId } = useParams<{ courseId: string }>();
  const navigate = useNavigate();
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

const { setLearningContextValue } = useOutletContext<{ 
    setLearningContextValue: (value: LearningContextType) => void 
  }>();

  
  const [quizSubmitted, setQuizSubmitted] = useState(false);
  const [quizScore, setQuizScore] = useState(0);
  const [userAnswers, setUserAnswers] = useState<Record<number, string>>({});
  const [showExplanation, setShowExplanation] = useState<Record<number, boolean>>({});
  const [questions, setQuestions] = useState<Question[]>([]);
  const [loadingQuestions, setLoadingQuestions] = useState(false);
  const [generatingQuiz, setGeneratingQuiz] = useState(false);
  const [quizGenerationMode, setQuizGenerationMode] = useState<'default' | 'bert' | 'personalized'>('default');
  const [mistakeQuestions, setMistakeQuestions] = useState<string[]>([]);

  
  const [examMode, setExamMode] = useState(false);
  const [examQuestions, setExamQuestions] = useState<Question[]>([]);
  const [examSubmitted, setExamSubmitted] = useState(false);
  const [examResult, setExamResult] = useState<any>(null);
  const [examAnswers, setExamAnswers] = useState<Record<number, string>>({});

  
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [showRecommendations, setShowRecommendations] = useState(false);
  const [loadingRecommendations, setLoadingRecommendations] = useState(false);

  const [generatingExam, setGeneratingExam] = useState(false);
  
  const [error, setError] = useState<string | null>(null);

  const getFilteredCourses = () => {
  const categories = getCourseCategories();
  const allTextCourseIds = new Set<number>();
  
  
  Object.values(categories).forEach(cat => {
    cat.courses.forEach(c => allTextCourseIds.add(c.id));
  });

  if (selectedCategory === 'all') {
    return courses.filter(c => allTextCourseIds.has(c.id));
  }

  const categoryData = categories[selectedCategory as keyof typeof categories];
  if (!categoryData) return [];
  
  const categoryIds = new Set(categoryData.courses.map(c => c.id));
  return courses.filter(c => categoryIds.has(c.id));
};

  useEffect(() => {
    loadCourses();
    const savedProgress = localStorage.getItem('text_reading_progress');
    if (savedProgress) {
      setReadingProgress(parseInt(savedProgress));
    }
  }, []);

  
useEffect(() => {
  if (courses.length > 0) {
    
    if (courseId) {
      const course = courses.find(c => c.id === parseInt(courseId));
      if (course) {
        setSelectedCourse(course);
      } else {
        
        setSelectedCourse(courses[0]);
      }
    } else {
      
      setSelectedCourse(courses[0]);
    }
  }
}, [courses, courseId]);

  useEffect(() => {
  if (selectedCourse && selectedCourse.id && !examMode) {
    loadRegularQuiz();
    loadQuestionsForCourse(selectedCourse.id);
    
    if (user?.id) {
      loadMistakesFromDB(user.id, selectedCourse.id);
    }
  }
}, [selectedCourse, examMode, user?.id]);


const updateLearningContext = useCallback(() => {
    if (setLearningContextValue) {
      setLearningContextValue({
        generatePersonalizedQuiz: generatePersonalizedQuiz,
        showTutorRecommendations: () => {
          if (mistakeQuestions.length > 0) {
            analyzeMistakesAndRecommendFromTexts(mistakeQuestions);
          } else {
            alert('Aucune erreur enregistrée pour ce cours');
          }
        },
        showMistakeStats: showMistakeStats,
        generateBertQuiz: generateBertQuiz,
        generateExam: generateExam,
        cancelExam: cancelExam,
        isExamMode: examMode,
        hasMistakes: mistakeQuestions.length > 0,
        isGeneratingQuiz: generatingQuiz,
        isGeneratingExam: generatingExam,
        selectedCourseId: selectedCourse?.id
      });
    }
  }, [
    selectedCourse,
    mistakeQuestions,
    examMode,
    generatingQuiz,
    generatingExam,
    setLearningContextValue
  ]);

  
  useEffect(() => {
    updateLearningContext();
  }, [updateLearningContext]);

const saveMistakesToDB = async (userId: number, courseId: number, wrongQuestions: { question: string; questionId: number }[]) => {
  if (!userId || !courseId || wrongQuestions.length === 0) return;
  
  try {
    const mistakesToSave = wrongQuestions.map(q => ({
      cours_id: courseId,
      question_id: q.questionId,
      question_texte: q.question,
      reponse_utilisateur: userAnswers[q.questionId] || '',
      reponse_correcte: questions.find(qu => qu.id === q.questionId)?.reponse_correcte || '',
      mode_apprentissage: 'texte',
      points_possibles: 10
    }));
    
    await mistakeService.saveBatchMistakes(mistakesToSave);
    console.log('✅ Erreurs sauvegardées en DB');
  } catch (error) {
    console.error('❌ Erreur sauvegarde DB:', error);
  }
};

const loadMistakesFromDB = async (userId: number, courseId: number) => {
  if (!userId || !courseId) return [];
  
  try {
    const mistakes = await mistakeService.getMyMistakes(courseId, 'texte', 30);
    const mistakeTexts = mistakes.map((m: any) => m.question_texte);
    setMistakeQuestions(mistakeTexts);
    console.log(`✅ ${mistakeTexts.length} erreurs chargées depuis la DB`);
    return mistakeTexts;
  } catch (error) {
    console.error('❌ Erreur chargement erreurs:', error);
    return [];
  }
};

const showMistakeStats = async () => {
  if (!user?.id) return;
  
  try {
    const stats = await mistakeService.getMyMistakesStats();
    alert(`
📊 STATISTIQUES D'ERREURS:
━━━━━━━━━━━━━━━━━━━━━━━
📝 Total erreurs: ${stats.total_erreurs}
⚠️ Non révisées: ${stats.erreurs_non_revues}
🔴 Critiques: ${stats.erreurs_critiques}
📚 Cours avec + erreurs: ${stats.cours_plus_erreurs || 'N/A'}
📖 Mode avec + erreurs: ${stats.mode_plus_erreurs || 'N/A'}
    `);
  } catch (error) {
    console.error('Erreur stats:', error);
    alert('Impossible de charger les statistiques');
  }
};

  const loadCourses = async () => {
    try {
      setLoading(true);
      const allCourses = await courseService.getAllCourses();
      setCourses(allCourses);
      if (allCourses.length > 0 && !selectedCourse) {
        setSelectedCourse(allCourses[0]);
      }
    } catch (error) {
      console.error('Erreur chargement cours:', error);
      setError('Impossible de charger les cours');
    } finally {
      setLoading(false);
    }
  };

  const loadRegularQuiz = async () => {
    if (!selectedCourse) return;
    
    try {
      setLoadingQuestions(true);
      setQuizGenerationMode('default');
      
      const response = await api.get(`/courses/${selectedCourse.id}/questions?mode=texte`);
      const questionsData = response.data;
      
      if (questionsData && questionsData.length > 0) {
        const filteredQuestions = questionsData.filter((q: any) => 
          q.mode_specifique === 'texte' || q.mode_specifique === null || !q.mode_specifique
        );
        
        const formattedQuestions = filteredQuestions.map((q: any, idx: number) => ({
          id: idx + 1,
          question: q.question,
          options: q.options || {},
          reponse_correcte: q.reponse_correcte,
          points: q.points || 10,
          difficulte: q.difficulte || 'moyen',
          explication: q.explication
        }));
        
        setQuestions(formattedQuestions);
      } else {
        setQuestions(getDefaultQuestions());
      }
    } catch (error) {
      console.error('Erreur chargement quiz:', error);
      setQuestions(getDefaultQuestions());
    } finally {
      setLoadingQuestions(false);
    }
  };

  

  
  const generatePersonalizedQuiz = async () => {
  if (!selectedCourse || !user?.id) return;
  
  try {
    setGeneratingQuiz(true);
    setQuizGenerationMode('personalized');
    setQuizSubmitted(false);
    setUserAnswers({});
    setShowExplanation({});
    
    
    const mistakes = await loadMistakesFromDB(user.id, selectedCourse.id);
    
    if (mistakes.length === 0) {
      const toast = document.createElement('div');
      toast.className = 'fixed bottom-4 right-4 bg-yellow-500 text-white px-4 py-2 rounded-lg shadow-lg z-50';
      toast.textContent = '📝 Aucune erreur enregistrée. Génération d\'un quiz standard.';
      document.body.appendChild(toast);
      setTimeout(() => toast.remove(), 3000);
      await generateBertQuiz();
      return;
    }
    
    
    try {
      const response = await api.post('/bert/quiz-from-mistakes', {
        course_id: String(selectedCourse.id),
        mode: 'texte',
        num_questions: 5
      });
      
      if (response.data && response.data.quiz && response.data.quiz.questions && response.data.quiz.questions.length > 0) {
        const formattedQuestions = response.data.quiz.questions.map((q: any, idx: number) => ({
          id: idx + 1,
          question: q.question,
          options: q.options || {},
          reponse_correcte: q.correct_answer || 'A',
          points: q.points || 10,
          difficulte: q.difficulte || 'moyen',
          explication: q.explanation || ''
        }));
        
        setQuestions(formattedQuestions);
        
        const toast = document.createElement('div');
        toast.className = 'fixed bottom-4 right-4 bg-green-500 text-white px-4 py-2 rounded-lg shadow-lg z-50';
        toast.textContent = `🎯 Quiz personnalisé généré! Basé sur ${response.data.mistakes_count} erreur(s)`;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 3000);
        return;
      }
    } catch (apiError) {
      console.error('Erreur API quiz personnalisé:', apiError);
      
      await generateBertQuiz();
      return;
    }
    
    
    await generateBertQuiz();
    
  } catch (error) {
    console.error('Erreur génération quiz personnalisé:', error);
    await generateBertQuiz();
  } finally {
    setGeneratingQuiz(false);
  }
};

  
  const generateBertQuiz = async () => {
  if (!selectedCourse) return;
  
  try {
    setGeneratingQuiz(true);
    setQuizGenerationMode('bert');
    setQuizSubmitted(false);
    setUserAnswers({});
    setShowExplanation({});
    
    const bertResponse = await bertQuizService.generateQuiz(
      String(selectedCourse.id), 
      5
    );
    
    if (bertResponse && bertResponse.questions && bertResponse.questions.length > 0) {
      const formattedQuestions = bertResponse.questions.map((q: any, idx: number) => {
        let options = q.options || {};
        
        const isValidOptions = options && typeof options === 'object' && Object.keys(options).length > 0;
        let hasValidValues = false;
        
        if (isValidOptions) {
          const values = Object.values(options);
          hasValidValues = values.some(v => 
            typeof v === 'string' && 
            v && 
            v !== 'Option A' && 
            v !== 'Option B' && 
            v !== 'Option C' && 
            v !== 'Option D' &&
            v !== ': \'' && 
            v !== '"B' &&
            v !== 'B' &&
            v.length > 1
          );
        }
        
        const questionText = q.question || '';
        if (questionText.includes("modifier le contenu texte") || questionText.includes("innerHTML")) {
          options = {
            A: "element.value = nouveauTexte",
            B: "element.innerHTML = nouveauTexte",
            C: "element.text = nouveauTexte",
            D: "element.content = nouveauTexte"
          };
          hasValidValues = true;
        }
        
        if (!hasValidValues) {
          options = getDefaultOptionsForQuestion(q.question);
        }
        
        const cleanOptions: Record<string, string> = {};
        const optionKeys = ['A', 'B', 'C', 'D'];
        
        for (let i = 0; i < optionKeys.length; i++) {
          const key = optionKeys[i];
          const value = options[key] || `Option ${key}`;
          
          let cleanValue = String(value);
          cleanValue = cleanValue.replace(/^['"]+/, '').replace(/['"]+$/, '');
          cleanValue = cleanValue.replace(/''/g, "'");
          cleanValue = cleanValue.trim();
          
          if (!cleanValue || cleanValue.length < 1 || cleanValue === ':' || cleanValue === 'B') {
            const defaultValues = [
              "Première option",
              "Deuxième option", 
              "Troisième option",
              "Quatrième option"
            ];
            cleanValue = defaultValues[i];
          }
          
          cleanOptions[key] = cleanValue;
        }
        
        if (questionText.includes("modifier le contenu texte") || questionText.includes("innerHTML")) {
          cleanOptions.A = "element.value = nouveauTexte";
          cleanOptions.B = "element.innerHTML = nouveauTexte";
          cleanOptions.C = "element.text = nouveauTexte";
          cleanOptions.D = "element.content = nouveauTexte";
        }
        
        return {
          id: idx + 1,
          question: q.question,
          options: cleanOptions,
          reponse_correcte: q.correct_answer || 'A',
          points: q.points || 10,
          difficulte: q.difficulte || 'moyen',
          explication: q.explanation || '',
          score: q.score || 0
        };
      });
      
      setQuestions(formattedQuestions);
      
      const toast = document.createElement('div');
      toast.className = 'fixed bottom-4 right-4 bg-green-500 text-white px-4 py-2 rounded-lg shadow-lg z-50';
      toast.textContent = `✅ Quiz généré! ${formattedQuestions.length} questions.`;
      document.body.appendChild(toast);
      setTimeout(() => toast.remove(), 3000);
    } else {
      throw new Error('Aucune question générée');
    }
  } catch (error) {
    console.error('Erreur génération quiz BERT:', error);
    const toast = document.createElement('div');
    toast.className = 'fixed bottom-4 right-4 bg-red-500 text-white px-4 py-2 rounded-lg shadow-lg z-50';
    toast.textContent = '❌ Erreur, utilisation du quiz par défaut';
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
    await loadRegularQuiz();
  } finally {
    setGeneratingQuiz(false);
  }
};

  
  const generateBertExam = async () => {
  if (!selectedCourse) return;
  
  try {
    setGeneratingExam(true);
    setExamMode(true);
    setExamSubmitted(false);
    setExamResult(null);
    setExamAnswers({});
    
    const bertResponse = await bertQuizService.generateQuiz(
      String(selectedCourse.id), 
      12
    );
    
    let examQuestionsList: Question[] = [];
    
    if (bertResponse && bertResponse.questions && bertResponse.questions.length > 0) {
      examQuestionsList = bertResponse.questions.map((q: any, idx: number) => {
        let options = { A: "Option A", B: "Option B", C: "Option C", D: "Option D" };
        let correctAnswer = q.correct_answer || 'A';
        const questionText = q.question || '';
        
        
        if (questionText.includes("surligner")) {
          options = { A: "<mark>", B: "<highlight>", C: "<strong>", D: "<em>" };
          correctAnswer = "A";
        } else if (questionText.includes("pliable") || questionText.includes("dépliable")) {
          options = { A: "<details> et <summary>", B: "<collapse> et <expand>", C: "<fold> et <unfold>", D: "<hide> et <show>" };
          correctAnswer = "A";
        } else if (questionText.includes("sémantique")) {
          options = { A: "Meilleur SEO et accessibilité", B: "Chargement plus rapide", C: "Design plus joli", D: "Compatibilité avec plus de navigateurs" };
          correctAnswer = "A";
        } else if (questionText.includes("modifier le contenu texte") || questionText.includes("innerHTML")) {
          options = { A: "element.value = nouveauTexte", B: "element.innerHTML = nouveauTexte", C: "element.text = nouveauTexte", D: "element.content = nouveauTexte" };
          correctAnswer = "B";
        } else if (questionText.includes("titre principal")) {
          options = { A: "<title>", B: "<h1>", C: "<head>", D: "<header>" };
          correctAnswer = "B";
        } else if (questionText.includes("ligne dans un tableau")) {
          options = { A: "<td>", B: "<tr>", C: "</table>", D: "<th>" };
          correctAnswer = "B";
        } else if (questionText.includes("sélecteur CSS") && questionText.includes("paragraphes")) {
          options = { A: "p", B: "#paragraph", C: ".paragraph", D: "<p>" };
          correctAnswer = "A";
        } else if (questionText.includes("thématiquement lié")) {
          options = { A: "<div>", B: "<group>", C: "<section>", D: "<article>" };
          correctAnswer = "C";
        } else if (questionText.includes("structure suivante") || questionText.includes("liste.html")) {
          options = { A: "../index.html", B: "./index.html", C: "/index.html", D: "index.html" };
          correctAnswer = "A";
        } else if (questionText.includes("<main>")) {
          options = { A: "0 fois", B: "1 fois", C: "2 fois", D: "Autant qu'on veut" };
          correctAnswer = "B";
        } else if (questionText.includes("taille du texte") || questionText.includes("propriete CSS")) {
          options = { A: "text-size", B: "font-size", C: "size", D: "text-scale" };
          correctAnswer = "B";
        } else if (questionText.includes("méthode JavaScript") && questionText.includes("contenu HTML")) {
          options = { A: "element.value = nouveauTexte", B: "element.innerHTML = nouveauTexte", C: "element.text = nouveauTexte", D: "element.content = nouveauTexte" };
          correctAnswer = "B";
        } else {
          const defaultOpts = getDefaultOptionsForQuestion(questionText);
          options = { A: defaultOpts.A, B: defaultOpts.B, C: defaultOpts.C, D: defaultOpts.D };
        }
        
        const cleanOptions: Record<string, string> = {};
        const optionKeys = ['A', 'B', 'C', 'D'];
        
        for (let i = 0; i < optionKeys.length; i++) {
          const key = optionKeys[i];
          const value = options[key as keyof typeof options];
          let cleanValue = String(value);
          cleanValue = cleanValue.replace(/^['"]+/, '').replace(/['"]+$/, '');
          cleanValue = cleanValue.replace(/''/g, "'");
          cleanValue = cleanValue.trim();
          
          if (!cleanValue || cleanValue.length < 1 || cleanValue === ':' || cleanValue === 'B') {
            const defaultValues = ["Première option", "Deuxième option", "Troisième option", "Quatrième option"];
            cleanValue = defaultValues[i];
          }
          
          cleanOptions[key] = cleanValue;
        }
        
        return {
          id: idx + 1000,
          question: q.question,
          options: cleanOptions,
          reponse_correcte: correctAnswer,
          points: q.points || 10,
          difficulte: q.difficulte || 'moyen',
          explication: q.explanation || '',
          score: q.score || 0
        };
      });
    }
    
    if (examQuestionsList.length < 12) {
      const defaultQs = getDefaultQuestions();
      while (examQuestionsList.length < 12 && defaultQs.length > 0) {
        const qToAdd = { ...defaultQs[examQuestionsList.length % defaultQs.length] };
        qToAdd.id = 2000 + examQuestionsList.length;
        examQuestionsList.push(qToAdd);
      }
    }
    
    setExamQuestions(examQuestionsList.slice(0, 12));
    
    const toast = document.createElement('div');
    toast.className = 'fixed bottom-4 right-4 bg-green-500 text-white px-4 py-2 rounded-lg shadow-lg z-50';
    toast.textContent = `✅ Examen généré! ${Math.min(12, examQuestionsList.length)} questions.`;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
    
  } catch (error) {
    console.error('Erreur génération examen:', error);
    
    if (questions.length > 0) {
      const fallbackQuestions = [...questions];
      while (fallbackQuestions.length < 12 && fallbackQuestions.length > 0) {
        fallbackQuestions.push({...fallbackQuestions[fallbackQuestions.length % fallbackQuestions.length]});
      }
      setExamQuestions(fallbackQuestions.slice(0, 12));
    } else {
      const defaultQs = getDefaultQuestions();
      const examQs = [];
      for (let i = 0; i < 12; i++) {
        const qCopy = { ...defaultQs[i % defaultQs.length] };
        qCopy.id = 3000 + i;
        examQs.push(qCopy);
      }
      setExamQuestions(examQs);
    }
    
    const toast = document.createElement('div');
    toast.className = 'fixed bottom-4 right-4 bg-yellow-500 text-white px-4 py-2 rounded-lg shadow-lg z-50';
    toast.textContent = '⚠️ Utilisation des questions par défaut pour l\'examen';
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
    
  } finally {
    setGeneratingExam(false);
  }
};

  const getDefaultQuestions = (): Question[] => [
    {
      id: 1,
      question: "Quelle balise HTML est utilisée pour créer un lien hypertexte ?",
      options: { A: "<link>", B: "<a>", C: "<href>", D: "<url>" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "La balise <a> (anchor) est utilisée pour créer des liens hypertextes."
    },
    {
      id: 2,
      question: "Quel attribut spécifie l'URL d'un lien ?",
      options: { A: "src", B: "url", C: "href", D: "link" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "L'attribut href spécifie l'URL de destination du lien."
    },
    {
      id: 3,
      question: "Comment créer un lien qui s'ouvre dans un nouvel onglet ?",
      options: { A: "target='_self'", B: "target='_blank'", C: "target='_new'", D: "target='_top'" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "L'attribut target='_blank' ouvre le lien dans un nouvel onglet."
    },
    {
      id: 4,
      question: "Quelle balise HTML5 est utilisée pour surligner du texte ?",
      options: { A: "<mark>", B: "<highlight>", C: "<strong>", D: "<em>" },
      reponse_correcte: "A",
      points: 10,
      difficulte: "facile",
      explication: "La balise <mark> est utilisée pour surligner du texte."
    },
    {
      id: 5,
      question: "Quelle balise utiliser pour le titre principal d'une page HTML ?",
      options: { A: "<title>", B: "<h1>", C: "<head>", D: "<header>" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "<h1> est utilisé pour le titre principal."
    }
  ];

  const resetExamState = () => {
  setExamMode(false);  
  setExamSubmitted(false);
  setExamResult(null);
  setExamAnswers({});
  setExamQuestions([]);
  setRecommendations([]);
  setShowRecommendations(false);
  setGeneratingExam(false);
  
  setError(null);
};

  const generateExam = async () => {
    await generateBertExam();
  };

  const cancelExam = () => {
  resetExamState();
  
  if (selectedCourse) {
    loadQuestionsForCourse(selectedCourse.id);
  }
};

  const analyzeMistakesAndRecommend = async (answers: ExamAnswer[]) => {
  const wrongQuestions = answers.filter(a => !a.isCorrect);
  const wrongQuestionsList = wrongQuestions.map(a => ({ 
    question: a.questionText, 
    questionId: a.questionId 
  }));
  
  
  if (user?.id && selectedCourse?.id && wrongQuestionsList.length > 0) {
    await saveMistakesToDB(user.id, selectedCourse.id, wrongQuestionsList);
    await loadMistakesFromDB(user.id, selectedCourse.id);
  }
  
  setLoadingRecommendations(true);
  
  try {
    const wrongTexts = wrongQuestions.map(a => a.questionText);
    const recommendationsData = await bertRecommendationService.recommendCourses(wrongTexts, 0.5, 5);
    if (recommendationsData && recommendationsData.recommendations) {
      setRecommendations(recommendationsData.recommendations);
    } else {
      setRecommendations(generateFallbackRecommendations(answers));
    }
  } catch (error) {
    console.error('Erreur recommandations:', error);
    setRecommendations(generateFallbackRecommendations(answers));
  } finally {
    setLoadingRecommendations(false);
  }
};

  const generateFallbackRecommendations = (answers: ExamAnswer[]): Recommendation[] => {
    const wrongAnswers = answers.filter(a => !a.isCorrect);
    const courseCounts: Record<string, { count: number; title: string }> = {};
    
    wrongAnswers.forEach(answer => {
      const relatedCourse = courses.find(c => 
        c.titre.toLowerCase().includes(answer.questionText.toLowerCase().substring(0, 30))
      );
      if (relatedCourse) {
        const cid = String(relatedCourse.id);
        if (!courseCounts[cid]) {
          courseCounts[cid] = { count: 0, title: relatedCourse.titre };
        }
        courseCounts[cid].count++;
      }
    });
    
    return Object.entries(courseCounts).map(([cid, data]) => ({
      cours_id: cid,
      cours_titre: data.title,
      score: Math.min(0.95, 0.5 + data.count * 0.1),
      description: `Cours à réviser (${data.count} erreur(s))`,
      direct_match: true,
      nb_erreurs: data.count
    }));
  };

 const generateCertificate = async (examResultData: any, courseName: string) => {
  if (!user) return;

  try {
    
    const response = await api.post('/certificates/generate', {
      user_id: user.id,
      course_id: selectedCourse?.id,
      score: examResultData.percentage,
      course_name: 'Formation Complète HTML, CSS & JavaScript',  
      mode: 'texte',
      date: new Date().toISOString(),
      is_global: true  
    });

    if (response.data && response.data.certificate_url) {
      window.open(response.data.certificate_url, '_blank');
      
      const toast = document.createElement('div');
      toast.className = 'fixed bottom-4 right-4 bg-green-500 text-white px-4 py-2 rounded-lg shadow-lg z-50';
      toast.innerHTML = '🎓 Certificat global généré avec succès !';
      document.body.appendChild(toast);
      setTimeout(() => toast.remove(), 5000);
    }
  } catch (error) {
    console.error('Erreur génération certificat:', error);
    generateLocalCertificate(examResultData, 'Formation Complète HTML, CSS & JavaScript');
  }
};


const generateLocalCertificate = (examResultData: any, courseName: string) => {
  if (!user) return;

  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  canvas.width = 1200;
  canvas.height = 900;

  
  ctx.fillStyle = '#ffffff';
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  
  ctx.strokeStyle = '#c9a84c';
  ctx.lineWidth = 20;
  ctx.strokeRect(40, 40, canvas.width - 80, canvas.height - 80);

  ctx.strokeStyle = '#d4b85a';
  ctx.lineWidth = 4;
  ctx.strokeRect(60, 60, canvas.width - 120, canvas.height - 120);

  
  ctx.fillStyle = '#1a1a2e';
  ctx.font = 'bold 56px serif';
  ctx.textAlign = 'center';
  ctx.fillText('🎓 CERTIFICAT DE RÉUSSITE', canvas.width / 2, 140);

  
  ctx.fillStyle = '#4a4a6a';
  ctx.font = '28px sans-serif';
  ctx.fillText('Formation Complète en Développement Web', canvas.width / 2, 200);

  
  ctx.beginPath();
  ctx.moveTo(200, 225);
  ctx.lineTo(1000, 225);
  ctx.strokeStyle = '#c9a84c';
  ctx.lineWidth = 2;
  ctx.stroke();

  
  ctx.fillStyle = '#4a4a6a';
  ctx.font = '22px sans-serif';
  ctx.fillText('Ce certificat atteste que', canvas.width / 2, 270);

  
  ctx.fillStyle = '#c9a84c';
  ctx.font = 'bold 52px serif';
  ctx.fillText(`${user.prenom || ''} ${user.nom || ''}`.trim() || user.email, canvas.width / 2, 350);

  
  ctx.fillStyle = '#2d2d44';
  ctx.font = '22px sans-serif';
  ctx.fillText('a complété avec succès l\'ensemble des cours suivants :', canvas.width / 2, 420);

  
  const coursesCompleted = courses.filter(c => 
    c.id === 6 || c.id === 11 || c.id === 12 || c.id === 8 || c.id === 9 ||
    c.id === 10 || c.id === 13 || c.id === 14 || c.id === 15 || c.id === 16 ||
    c.id === 17 || c.id === 18 || c.id === 19 || c.id === 20 || c.id === 22 ||
    c.id === 23 || c.id === 24 || c.id === 25 || c.id === 26 || c.id === 27 ||
    c.id === 28 || c.id === 29 || c.id === 30 || c.id === 31 || c.id === 32 ||
    c.id === 33 || c.id === 34 || c.id === 35 || c.id === 36 || c.id === 37 ||
    c.id === 38 || c.id === 39 || c.id === 40 || c.id === 41 || c.id === 42 ||
    c.id === 43 || c.id === 44 || c.id === 45 || c.id === 46 || c.id === 47 ||
    c.id === 48
  );

  
  ctx.fillStyle = '#1a1a2e';
  ctx.font = '18px sans-serif';
  ctx.textAlign = 'left';
  
  const maxCourses = Math.min(coursesCompleted.length, 8);
  const coursesToShow = coursesCompleted.slice(0, maxCourses);
  
  
  ctx.fillStyle = '#4a4a6a';
  ctx.font = 'bold 20px sans-serif';
  ctx.textAlign = 'center';
  ctx.fillText('📚 Modules validés :', canvas.width / 2, 480);
  
  
  ctx.textAlign = 'left';
  const startY = 510;
  const col1X = 200;
  const col2X = 600;
  const rowHeight = 35;
  
  const half = Math.ceil(coursesToShow.length / 2);
  const col1Courses = coursesToShow.slice(0, half);
  const col2Courses = coursesToShow.slice(half);
  
  ctx.fillStyle = '#2d2d44';
  ctx.font = '16px sans-serif';
  
  col1Courses.forEach((course, idx) => {
    ctx.fillText(` ${course.titre.substring(0, 35)}${course.titre.length > 35 ? '...' : ''}`, col1X, startY + idx * rowHeight);
  });
  
  col2Courses.forEach((course, idx) => {
    ctx.fillText(` ${course.titre.substring(0, 35)}${course.titre.length > 35 ? '...' : ''}`, col2X, startY + idx * rowHeight);
  });

  
  ctx.textAlign = 'center';
  ctx.fillStyle = '#2d2d44';
  ctx.font = '20px sans-serif';
  ctx.fillText(`Score final : ${examResultData.percentage.toFixed(1)}%`, canvas.width / 2, 680);

  
  const date = new Date().toLocaleDateString('fr-FR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  });
  ctx.fillStyle = '#4a4a6a';
  ctx.font = '18px sans-serif';
  ctx.fillText(`Délivré le ${date}`, canvas.width / 2, 730);

  
  ctx.beginPath();
  ctx.moveTo(350, 770);
  ctx.lineTo(550, 770);
  ctx.strokeStyle = '#1a1a2e';
  ctx.lineWidth = 2;
  ctx.stroke();

  ctx.fillStyle = '#4a4a6a';
  ctx.font = '16px sans-serif';
  ctx.fillText('Signature du responsable pédagogique', 450, 800);

  
  ctx.fillStyle = '#c9a84c';
  ctx.font = '70px sans-serif';
  ctx.fillText('🎓', canvas.width / 2, 860);

  
  const link = document.createElement('a');
  link.download = `certificat_${user.prenom || 'utilisateur'}_${user.nom || ''}.png`;
  link.href = canvas.toDataURL('image/png');
  link.click();

  const toast = document.createElement('div');
  toast.className = 'fixed bottom-4 right-4 bg-green-500 text-white px-4 py-2 rounded-lg shadow-lg z-50';
  toast.innerHTML = '🎓 Certificat global généré avec succès !';
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 5000);
};


const submitExam = async () => {
  if (!selectedCourse || !isAuthenticated) {
    alert('Veuillez vous connecter');
    return;
  }

  if (!user?.id) {
    alert('Utilisateur non identifié');
    return;
  }

  const answeredCount = Object.keys(examAnswers).length;
  if (answeredCount !== examQuestions.length) {
    alert(`Veuillez répondre à toutes les questions (${answeredCount}/${examQuestions.length})`);
    return;
  }

  let totalScore = 0;
  let maxScore = 0;
  const answersList: ExamAnswer[] = [];

  
  console.log(`📝 Nombre de questions dans l'examen: ${examQuestions.length}`);
  
  
  examQuestions.forEach(q => {
    maxScore += q.points || 10;
  });
  console.log(` Total des points maximum: ${maxScore}`);

  for (const q of examQuestions) {
    const userAnswer = examAnswers[q.id];
    const isCorrect = userAnswer === q.reponse_correcte;
    if (isCorrect) {
      totalScore += q.points || 10;
    }

    answersList.push({
      questionId: q.id,
      questionText: q.question,
      selectedAnswer: userAnswer || '',
      isCorrect,
      correctAnswer: q.reponse_correcte,
      explanation: q.explication || ''
    });
  }

  const percentage = (totalScore / maxScore) * 100;
  const passed = percentage >= 70;

  console.log(`📊 Résultat: Score=${totalScore}/${maxScore}, Pourcentage=${percentage.toFixed(1)}%, Passé=${passed}`);
  console.log(`📊 Questions: ${answersList.length}, Points: ${maxScore}`);

  setExamResult({ 
    score: totalScore, 
    total: maxScore, 
    percentage, 
    passed, 
    answers: answersList 
  });
  setExamSubmitted(true);

  try {
    const resultData = {
      utilisateur_id: user.id,
      cours_id: Number(selectedCourse.id),
      mode: 'texte',
      score_quiz: Number(percentage.toFixed(2)),
      temps_passe: Math.max(1, Math.floor(readingProgress / 10) || 1),
      taux_completion: Number((readingProgress > 0 ? readingProgress : 100).toFixed(2)),
      feedback: passed 
        ? `Examen réussi! Score: ${percentage.toFixed(1)}%` 
        : `Score: ${percentage.toFixed(1)}%`
    };

    console.log('📤 Envoi des données:', resultData);

    const response = await api.post('/results', resultData);
    console.log('Résultat enregistré:', response.data);

    await analyzeMistakesAndRecommend(answersList);
    setShowRecommendations(true);

    

  } catch (error: any) {
    console.error('Erreur:', error);
    console.error(' Response:', error.response?.data);
    console.error(' Status:', error.response?.status);

    if (error.response?.data?.detail) {
      const detail = typeof error.response.data.detail === 'string' 
        ? error.response.data.detail 
        : JSON.stringify(error.response.data.detail);
      alert(`Erreur: ${detail}`);
    } else {
      alert('Erreur lors de l\'enregistrement de l\'examen. Veuillez réessayer.');
    }
  }
};

  const navigateToCourse = (courseId: string) => {
    const course = courses.find(c => String(c.id) === courseId);
    if (course) {
      setSelectedCourse(course);
      resetExamState();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const loadQuestionsForCourse = async (courseId: number) => {
    try {
      setLoadingQuestions(true);
      const response = await api.get(`/courses/${courseId}/questions`);
      const questionsData = response.data;
      
      if (questionsData && questionsData.length > 0) {
        const filteredQuestions = questionsData.filter((q: any) => 
          q.mode_specifique === 'texte' || q.mode_specifique === null || !q.mode_specifique
        );
        
        const formattedQuestions = filteredQuestions.map((q: any, idx: number) => ({
          id: idx + 1,
          question: q.question,
          options: q.options || {},
          reponse_correcte: q.reponse_correcte,
          points: q.points || 10,
          difficulte: q.difficulte || 'moyen',
          explication: q.explication
        }));
        
        setQuestions(formattedQuestions);
      } else {
        setQuestions([]);
      }
    } catch (error) {
      console.error('Erreur chargement questions:', error);
      setQuestions([]);
    } finally {
      setLoadingQuestions(false);
    }
  };

  const handleCourseSelect = (course: Course) => {
    setSelectedCourse(course);
    setQuizSubmitted(false);
    setUserAnswers({});
    setQuizScore(0);
    setShowExplanation({});
    resetExamState();
     navigate(`/learning/text/${course.id}`);
  };

  const handleProgressChange = (progress: number) => {
    setReadingProgress(progress);
    localStorage.setItem('text_reading_progress', progress.toString());
  };

  const handleAnswerSelect = (questionId: number, answer: string) => {
    setUserAnswers(prev => ({ ...prev, [questionId]: answer }));
  };

  const handleExamAnswerSelect = (questionId: number, answer: string) => {
  
  if (examSubmitted) return;
  setExamAnswers(prev => ({ ...prev, [questionId]: answer }));
};

  const toggleExplanation = (questionId: number) => {
    setShowExplanation(prev => ({ ...prev, [questionId]: !prev[questionId] }));
  };

  const handleSubmitQuiz = async () => {
  if (!selectedCourse || !isAuthenticated) {
    alert('Veuillez vous connecter pour enregistrer vos résultats');
    return;
  }

  if (!user?.id) {
    alert('Impossible de récupérer votre identifiant utilisateur');
    return;
  }

  if (questions.length === 0) {
    alert('Aucune question disponible pour ce cours');
    return;
  }

  const answeredCount = Object.keys(userAnswers).length;
  if (answeredCount !== questions.length) {
    alert(`Veuillez répondre à toutes les questions (${answeredCount}/${questions.length})`);
    return;
  }

  let totalScore = 0;
  let maxScore = 0;
  const wrongQuestions: { question: string; questionId: number }[] = [];
  const responses = [];

  for (const q of questions) {
    maxScore += q.points;
    const userAnswer = userAnswers[q.id];
    const isCorrect = userAnswer === q.reponse_correcte;
    if (isCorrect) {
      totalScore += q.points;
    } else {
      wrongQuestions.push({ 
        question: q.question, 
        questionId: q.id 
      });
      console.log(' Erreur enregistrée:', q.question);
    }
    
    responses.push({
      question_id: q.id,
      reponse_utilisateur: userAnswer || '',
      est_correcte: isCorrect,
      temps_reponse: 30
    });
  }
  
  console.log(' Total des erreurs:', wrongQuestions.length);

  
  if (wrongQuestions.length > 0) {
    await saveMistakesToDB(user.id, selectedCourse.id, wrongQuestions);
    await loadMistakesFromDB(user.id, selectedCourse.id);
  }

  const percentage = (totalScore / maxScore) * 100;
  const isSuccess = percentage >= 70;
  const timeSpent = Math.max(Math.floor(readingProgress / 10), 1);
  const completionRate = readingProgress;

  const resultData = {
    utilisateur_id: user.id,
    cours_id: Number(selectedCourse.id),
    mode: 'texte',
    score_quiz: Number(percentage.toFixed(2)),
    temps_passe: timeSpent,
    taux_completion: completionRate,
    est_reussi: isSuccess,
    feedback: isSuccess 
      ? `Félicitations ! Score: ${percentage.toFixed(1)}%` 
      : `Continuez à pratiquer. Score: ${percentage.toFixed(1)}%`
  };

  try {
    const resultResponse = await api.post('/results', resultData);
    const resultId = resultResponse.data.id;

    for (const response of responses) {
      const responseData = {
        resultat_id: resultId,
        question_id: response.question_id,
        reponse_utilisateur: response.reponse_utilisateur,
        est_correcte: response.est_correcte,
        temps_reponse: response.temps_reponse
      };
      await api.post('/reponses', responseData);
    }

    setQuizScore(percentage);
    setQuizSubmitted(true);
    
    const correctCount = responses.filter(r => r.est_correcte).length;
    alert(` Quiz soumis avec succès !\nScore: ${percentage.toFixed(1)}%\nRéponses correctes: ${correctCount}/${responses.length}`);
  } catch (error: any) {
    console.error(' Erreur:', error);
    if (error.response?.data?.detail) {
      alert(`Erreur: ${JSON.stringify(error.response.data.detail)}`);
    } else {
      alert('Erreur lors de l\'enregistrement du quiz.');
    }
  }
};

  const resetQuiz = () => {
    setUserAnswers({});
    setQuizSubmitted(false);
    setQuizScore(0);
    setShowExplanation({});
    loadRegularQuiz();
  };
  
const analyzeMistakesAndRecommendFromTexts = async (wrongQuestions: string[]) => {
  if (!user?.id || wrongQuestions.length === 0) {
    console.log('Aucune erreur à analyser');
    return;
  }
  
  setLoadingRecommendations(true);
  setShowRecommendations(true);
  
  try {
    console.log(` Tuteur IA analyse ${wrongQuestions.length} erreur(s)...`);
    
    const response = await bertRecommendationService.recommendCourses(wrongQuestions, 0.5, 5);
    
    if (response && response.recommendations && response.recommendations.length > 0) {
      setRecommendations(response.recommendations);
      
      const toast = document.createElement('div');
      toast.className = 'fixed bottom-4 right-4 bg-indigo-500 text-white px-4 py-2 rounded-lg shadow-lg z-50';
      toast.innerHTML = `🤖 Tuteur IA: ${response.recommendations.length} cours recommandés!`;
      document.body.appendChild(toast);
      setTimeout(() => toast.remove(), 5000);
    } else {
      
      const fallbackRecs = generateFallbackRecommendationsFromTexts(wrongQuestions);
      if (fallbackRecs.length > 0) {
        setRecommendations(fallbackRecs);
        
        const toast = document.createElement('div');
        toast.className = 'fixed bottom-4 right-4 bg-blue-500 text-white px-4 py-2 rounded-lg shadow-lg z-50';
        toast.innerHTML = `🤖 Tuteur IA: ${fallbackRecs.length} cours recommandés (mode secours)`;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 4000);
      }
    }
  } catch (error) {
    console.error('❌ Erreur recommandation IA:', error);
    
    const fallbackRecs = generateFallbackRecommendationsFromTexts(wrongQuestions);
    if (fallbackRecs.length > 0) {
      setRecommendations(fallbackRecs);
      
      const toast = document.createElement('div');
      toast.className = 'fixed bottom-4 right-4 bg-orange-500 text-white px-4 py-2 rounded-lg shadow-lg z-50';
      toast.innerHTML = `🤖 Tuteur IA: ${fallbackRecs.length} cours recommandés (connexion limitée)`;
      document.body.appendChild(toast);
      setTimeout(() => toast.remove(), 4000);
    }
  } finally {
    setLoadingRecommendations(false);
  }
};


const generateFallbackRecommendationsFromTexts = (wrongQuestions: string[]): Recommendation[] => {
  const recommendations: Recommendation[] = [];
  const matchedCourses = new Set<string>();
  
  const keywordToCourse: Record<string, { id: string; title: string; description: string }> = {
    "titre principal": { id: "6", title: "Formatage du Texte en HTML", description: "Maîtrisez les balises de titre" },
    "lien hypertexte": { id: "11", title: "Les Liens Hypertextes en HTML", description: "Créez des liens hypertextes" },
    "image": { id: "12", title: "Images en HTML", description: "Intégrez des images" },
    "formulaire": { id: "8", title: "Formulaires HTML Avancés", description: "Créez des formulaires" },
    "sémantique": { id: "9", title: "HTML5 Sémantique", description: "Structurez vos pages" },
    "flexbox": { id: "10", title: "CSS Flexbox & Grid", description: "Mises en page modernes" },
    "tableau": { id: "13", title: "Les Tableaux en HTML", description: "Organisez vos données" },
    "css": { id: "17", title: "CSS - Les Sélecteurs", description: "Ciblez les éléments" },
    "javascript": { id: "33", title: "JavaScript - Introduction", description: "Découvrez JavaScript" }
  };
  
  for (const question of wrongQuestions) {
    const lowerQuestion = question.toLowerCase();
    for (const [keyword, course] of Object.entries(keywordToCourse)) {
      if (lowerQuestion.includes(keyword) && !matchedCourses.has(course.id)) {
        matchedCourses.add(course.id);
        recommendations.push({
          cours_id: course.id,
          cours_titre: course.title,
          score: 0.85,
          description: course.description,
          direct_match: true,
          nb_erreurs: 1
        });
        break;
      }
    }
  }
  
  if (recommendations.length === 0 && wrongQuestions.length > 0) {
    recommendations.push({
      cours_id: String(selectedCourse?.id || "6"),
      cours_titre: selectedCourse?.titre || "Cours actuel",
      score: 0.7,
      description: "Révisez les concepts de base de ce cours",
      direct_match: false,
      nb_erreurs: wrongQuestions.length
    });
  }
  
  return recommendations.slice(0, 5);
};

  


  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="text-4xl mb-4">📖</div>
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
            className="px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600"
          >
            Réessayer
          </button>
        </div>
      </div>
    );
  }

 return (
  
  <div className="min-h-screen bg-gray-100">
    <div className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
      
      
      {examMode ? (
        <div className="max-w-4xl mx-auto space-y-8">
          
          <div className="bg-gradient-to-r from-indigo-500 to-indigo-700 rounded-2xl p-6 text-white">
            <div className="flex justify-between items-center">
              <div>
                <h1 className="text-3xl font-bold mb-2">📝 Examen Final</h1>
                <p className="opacity-90">Évaluez vos connaissances sur {selectedCourse?.titre}</p>
              </div>
              <button
                onClick={cancelExam}
                className="px-4 py-2 bg-white/20 rounded-lg hover:bg-white/30 transition"
              >
                ✕ Retour à l'apprentissage
              </button>
            </div>
          </div>

          
        {generatingExam ? (
  <div className="bg-white rounded-xl shadow-md p-12 text-center">
    <div className="text-5xl mb-4">⏳</div>
    <div className="inline-block w-8 h-8 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mb-4" />
    <p className="text-gray-600">Génération de votre examen personnalisé...</p>
  </div>
) : examSubmitted && examResult ? (
  
  <div className="space-y-6">
    
    <div className={`rounded-xl shadow-md p-8 text-center ${
      examResult.passed 
        ? 'bg-gradient-to-r from-green-500 to-green-700 text-white' 
        : 'bg-gradient-to-r from-red-500 to-red-700 text-white'
    }`}>
      <div className="text-7xl mb-4">{examResult.passed ? '🎓' : '📚'}</div>
      <h2 className="text-3xl font-bold mb-2">
        {examResult.passed ? 'Félicitations !' : 'Continuez à vous entraîner !'}
      </h2>
      <p className="text-6xl font-bold mb-2">{examResult.percentage.toFixed(1)}%</p>
      <p className="text-lg opacity-90">
        {examResult.passed 
          ? '✅ Vous avez réussi l\'examen avec succès !' 
          : '⚠️ Vous n\'avez pas atteint le seuil de réussite (70%).'}
      </p>
      <p className="text-sm opacity-75 mt-2">
        Score: {examResult.score} / {examResult.total} points
      </p>
    </div>

    
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <div className="bg-white rounded-xl shadow-md p-4 text-center">
        <div className="text-3xl font-bold text-green-600">
          {examResult.answers.filter((a: ExamAnswer) => a.isCorrect).length}
        </div>
        <div className="text-sm text-gray-500">✅ Réponses correctes</div>
        <div className="text-xs text-gray-400">
          ({examResult.answers.filter((a: ExamAnswer) => a.isCorrect).length} / {examResult.answers.length} questions)
        </div>
      </div>
      <div className="bg-white rounded-xl shadow-md p-4 text-center">
        <div className="text-3xl font-bold text-red-600">
          {examResult.answers.filter((a: ExamAnswer) => !a.isCorrect).length}
        </div>
        <div className="text-sm text-gray-500">❌ Réponses incorrectes</div>
        <div className="text-xs text-gray-400">
          ({examResult.answers.filter((a: ExamAnswer) => !a.isCorrect).length} / {examResult.answers.length} questions)
        </div>
      </div>
      <div className="bg-white rounded-xl shadow-md p-4 text-center">
        <div className="text-3xl font-bold text-purple-600">
          {examResult.answers.length}
        </div>
        <div className="text-sm text-gray-500">📝 Total questions</div>
        <div className="text-xs text-gray-400">
          ({examResult.total} points au total)
        </div>
      </div>
    </div>

    
    {examResult.answers.filter((a: ExamAnswer) => !a.isCorrect).length > 0 && (
      <div className="bg-yellow-50 rounded-xl shadow-md p-6">
        <h3 className="text-xl font-bold text-yellow-800 mb-4 flex items-center gap-2">
          <span>📊</span> Analyse des erreurs 
          <span className="text-sm font-normal bg-yellow-200 px-3 py-1 rounded-full">
            {examResult.answers.filter((a: ExamAnswer) => !a.isCorrect).length} erreur(s)
          </span>
        </h3>
        <div className="space-y-3 max-h-80 overflow-y-auto">
          {examResult.answers.filter((a: ExamAnswer) => !a.isCorrect).map((answer: ExamAnswer, idx: number) => (
            <div key={idx} className="bg-white rounded-lg p-4 border border-yellow-200 hover:shadow-md transition">
              <p className="font-semibold text-gray-800">❌ {answer.questionText}</p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mt-2">
                <div className="bg-red-50 p-2 rounded">
                  <span className="text-xs text-gray-500">Votre réponse</span>
                  <p className="font-mono text-red-600">{answer.selectedAnswer || 'Non répondue'}</p>
                </div>
                <div className="bg-green-50 p-2 rounded">
                  <span className="text-xs text-gray-500">Bonne réponse</span>
                  <p className="font-mono text-green-600">{answer.correctAnswer}</p>
                </div>
              </div>
              {answer.explanation && (
                <p className="text-sm text-gray-600 mt-2 bg-blue-50 p-2 rounded">
                  💡 {answer.explanation}
                </p>
              )}
            </div>
          ))}
        </div>
      </div>
    )}

    
    <div className="flex flex-col sm:flex-row gap-3">
      <button
        onClick={cancelExam}
        className="flex-1 px-6 py-3 bg-gray-200 text-gray-700 rounded-lg font-semibold hover:bg-gray-300 transition"
      >
        🔄 Retour à l'apprentissage
      </button>
      <button
        onClick={() => {
          setExamSubmitted(false);
          setExamResult(null);
          setExamAnswers({});
          generateExam();
        }}
        className="flex-1 px-6 py-3 bg-purple-600 text-white rounded-lg font-semibold hover:bg-purple-700 transition"
      >
        🔁 Recommencer l'examen
      </button>
    </div>

    
    {examResult.passed && (
      <div className="mt-4 p-4 bg-gradient-to-r from-yellow-50 to-amber-50 rounded-xl border-2 border-yellow-300">
        <p className="text-center text-sm text-gray-600 mb-3">
          🎉 Félicitations ! Vous avez réussi l'examen. Vous pouvez maintenant générer votre certificat.
        </p>
        <button
          onClick={() => generateCertificate(examResult, selectedCourse?.titre || 'Cours')}
          className="w-full px-6 py-4 bg-gradient-to-r from-yellow-400 via-yellow-500 to-yellow-600 text-white rounded-lg font-bold hover:from-yellow-500 hover:via-yellow-600 hover:to-yellow-700 transition-all duration-300 shadow-lg hover:shadow-xl flex items-center justify-center gap-3 text-lg"
        >
          <span className="text-3xl animate-bounce">🎓</span>
          Générer mon certificat de réussite
          <span className="text-sm opacity-80">📄</span>
        </button>
        <p className="text-xs text-gray-500 text-center mt-2">
          Votre certificat sera téléchargé au format PNG
        </p>
      </div>
    )}
  </div>
) : (
  
  <div className="bg-white rounded-xl shadow-md p-6 sm:p-8">
    
    <div className="mb-6 pb-4 border-b">
      <div className="flex justify-between items-center">
        <div>
          <p className="text-gray-600">L'examen contient <strong>{examQuestions.length}</strong> questions</p>
          <p className="text-sm text-gray-500 mt-1">
            Score minimum requis: <strong className="text-purple-600">70%</strong>
          </p>
        </div>
        <div className="text-right">
          <span className="text-sm text-gray-500">Progression</span>
          <p className="text-lg font-bold text-purple-600">
            {Object.keys(examAnswers).length} / {examQuestions.length}
          </p>
        </div>
      </div>
      
      <div className="w-full bg-gray-200 rounded-full h-2 mt-3">
        <div 
          className="bg-purple-600 h-2 rounded-full transition-all duration-500"
          style={{ width: `${(Object.keys(examAnswers).length / examQuestions.length) * 100}%` }}
        />
      </div>
    </div>
    
    
    <div className="space-y-6 max-h-[60vh] overflow-y-auto pr-2">
      {examQuestions.map((q, idx) => (
        <div 
          key={q.id} 
          className={`border rounded-lg p-4 transition-all duration-300 ${
            examAnswers[q.id] 
              ? 'border-purple-300 bg-purple-50' 
              : 'border-gray-200 hover:border-purple-200 hover:shadow-md'
          }`}
        >
          <div className="flex justify-between items-start mb-3">
            <p className="font-semibold text-gray-800">
              Question {idx + 1}
            </p>
            <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full">
              {q.points} points • {q.difficulte}
            </span>
          </div>
          <p className="mb-4 text-gray-700">{q.question}</p>
          <div className="space-y-2">
            {Object.entries(q.options).map(([key, value]) => (
              <label 
                key={key} 
                className={`flex items-center gap-3 p-3 rounded-lg cursor-pointer transition-all duration-200 ${
                  examAnswers[q.id] === key
                    ? 'bg-purple-100 border-2 border-purple-500'
                    : 'hover:bg-gray-50 border-2 border-transparent'
                }`}
              >
                <input
                  type="radio"
                  name={`exam_question_${q.id}`}
                  value={key}
                  checked={examAnswers[q.id] === key}
                  onChange={() => handleExamAnswerSelect(q.id, key)}
                  className="w-4 h-4 text-purple-600 focus:ring-purple-500"
                />
                <span className="text-sm font-medium">
                  <span className="font-bold text-purple-600">{key}.</span> {value}
                </span>
              </label>
            ))}
          </div>
        </div>
      ))}
    </div>
    
    
    <button
      onClick={submitExam}
      disabled={Object.keys(examAnswers).length !== examQuestions.length}
      className={`w-full mt-6 px-6 py-4 rounded-lg font-semibold transition-all duration-300 ${
        Object.keys(examAnswers).length === examQuestions.length
          ? 'bg-gradient-to-r from-purple-600 to-purple-700 text-white hover:from-purple-700 hover:to-purple-800 shadow-lg hover:shadow-xl'
          : 'bg-gray-200 text-gray-400 cursor-not-allowed'
      }`}
    >
      {Object.keys(examAnswers).length === examQuestions.length 
        ? '📤 Soumettre l\'examen' 
        : `📝 ${Object.keys(examAnswers).length}/${examQuestions.length} questions répondues`}
    </button>
    
    {Object.keys(examAnswers).length !== examQuestions.length && (
      <p className="text-sm text-yellow-600 mt-3 text-center">
        ⚠️ Veuillez répondre à toutes les questions avant de soumettre
      </p>
    )}
  </div>
)}
        </div>
      ) : (
        
        <div className="space-y-8">
          
          
          <div className="bg-gradient-to-r from-purple-500 to-purple-700 rounded-2xl p-6 text-white">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
              <div>
                <h1 className="text-2xl sm:text-3xl font-bold mb-2">
                  {examMode ? '📝 Examen Final' : '📖 Apprentissage par Texte'}
                </h1>
                <p className="opacity-90 text-sm sm:text-base">
                  {examMode 
                    ? `Évaluez vos connaissances sur ${selectedCourse?.titre}`
                    : 'Apprenez HTML à travers des leçons écrites détaillées'}
                </p>
              </div>
              {!examMode && (
                <div className="flex gap-2 w-full sm:w-auto">
                  <button
                    onClick={generatePersonalizedQuiz}
                    disabled={generatingQuiz || !selectedCourse}
                    className="flex-1 sm:flex-none px-3 py-2 bg-green-600 rounded-lg hover:bg-green-700 transition text-sm flex items-center justify-center gap-1"
                  >
                    {generatingQuiz ? '⏳' : '🎯'} Perso
                  </button>
                  <button
                    onClick={generateBertQuiz}
                    disabled={generatingQuiz || !selectedCourse}
                    className="flex-1 sm:flex-none px-3 py-2 bg-blue-600 rounded-lg hover:bg-blue-700 transition text-sm flex items-center justify-center gap-1"
                  >
                    {generatingQuiz ? '⏳' : '🤖'} IA
                  </button>
                </div>
              )}
            </div>
          </div>

          
          <div className="bg-white rounded-xl shadow-md p-4 sm:p-6">
            <h3 className="text-sm font-semibold text-gray-500 mb-3">📚 Sélectionner un cours texte</h3>
            
            
            <div className="flex flex-wrap gap-2 mb-4">
              <button
                onClick={() => setSelectedCategory('all')}
                className={`px-3 py-1.5 rounded-full text-xs font-medium transition ${
                  selectedCategory === 'all'
                    ? 'bg-gray-800 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                📚 Tous
              </button>
              {Object.entries(getCourseCategories()).map(([key, cat]) => (
                <button
                  key={key}
                  onClick={() => setSelectedCategory(key)}
                  className={`px-3 py-1.5 rounded-full text-xs font-medium transition ${
                    selectedCategory === key
                      ? `${cat.bgColor} ${cat.color} ring-2 ring-offset-1`
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  {cat.icon} {key}
                </button>
              ))}
            </div>

            
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-2 max-h-[300px] overflow-y-auto p-2">
              {getFilteredCourses().map((course) => {
                const isSelected = selectedCourse?.id === course.id;
                const icon = getCourseIcon(course.id);
                
                let categoryColor = 'text-gray-600';
                const categories = getCourseCategories();
                for (const [key, cat] of Object.entries(categories)) {
                  if (cat.courses.some(c => c.id === course.id)) {
                    categoryColor = cat.color;
                    break;
                  }
                }
                
                return (
                  <button
                    key={course.id}
                    onClick={() => handleCourseSelect(course)}
                    className={`p-2 rounded-lg text-center transition-all duration-200 ${
                      isSelected 
                        ? 'bg-purple-100 border-2 border-purple-500 text-purple-700' 
                        : 'bg-gray-50 hover:bg-gray-100 text-gray-700 border-2 border-transparent'
                    }`}
                  >
                    <div className="text-2xl">{icon}</div>
                    <div className={`text-xs font-medium truncate mt-1 ${isSelected ? 'text-purple-700' : categoryColor}`}>
                      {course.titre}
                    </div>
                    {isSelected && (
                      <div className="text-[10px] text-purple-500 mt-0.5">▶ En cours</div>
                    )}
                  </button>
                );
              })}
            </div>
            
            {getFilteredCourses().length === 0 && (
              <div className="text-center py-4 text-gray-500 text-sm">
                Aucun cours disponible dans cette catégorie
              </div>
            )}
          </div>

          
          {!examMode && selectedCourse && (
            <div className="bg-white rounded-xl shadow-md p-4 sm:p-6">
              <div className="flex flex-col sm:flex-row items-start justify-between gap-4">
                <div className="w-full">
                  <h2 className="text-lg sm:text-xl font-bold text-gray-800">{selectedCourse.titre}</h2>
                  <p className="text-gray-600 mt-1 text-sm sm:text-base">{selectedCourse.description || 'Aucune description disponible'}</p>
                  <div className="flex flex-wrap gap-3 sm:gap-4 mt-3">
                    <span className="text-xs sm:text-sm text-gray-500">📊 Niveau: {selectedCourse.difficulte || 'Débutant'}</span>
                    <span className="text-xs sm:text-sm text-gray-500">⏱️ Durée: {selectedCourse.duree || 25} min</span>
                  </div>
                </div>
                {readingProgress === 100 && (
                  <div className="text-green-500 text-xs sm:text-sm bg-green-50 px-3 py-1 rounded-full whitespace-nowrap">
                    ✅ Terminé
                  </div>
                )}
              </div>
            </div>
          )}

          
          {!examMode && (
            <div className="bg-white rounded-xl shadow-md p-4 sm:p-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-base sm:text-lg font-semibold">📊 Progression de lecture</h3>
                <span className="text-sm text-gray-500">{readingProgress}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                value={readingProgress}
                onChange={(e) => handleProgressChange(parseInt(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              />
              {readingProgress < 100 && (
                <button
                  onClick={() => handleProgressChange(100)}
                  className="mt-4 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition text-sm w-full sm:w-auto"
                >
                  ✅ Marquer comme terminé
                </button>
              )}
            </div>
          )}

          
          {!examMode && selectedCourse && (
            <div className="bg-white rounded-xl shadow-md p-6 md:p-10 w-full">
              <div className="w-full text-justify max-w-7xl mx-auto">
                {selectedCourse.contenu ? (
                  <div
                    className="w-full text-justify leading-relaxed"
                    dangerouslySetInnerHTML={{
                      __html: selectedCourse.contenu,
                    }}
                  />
                ) : (
                  <div className="text-gray-500 italic text-center py-8">
                    Le contenu de ce cours sera bientôt disponible.
                  </div>
                )}
              </div>
            </div>
          )}

          
          {!examMode && (
            <div className="bg-gradient-to-r from-purple-500 to-purple-700 rounded-xl p-4 sm:p-6 md:p-8 text-white">
              <div className="flex flex-wrap justify-between items-center gap-2 mb-4">
                <h3 className="text-xl sm:text-2xl font-bold">🎯 Quiz de révision</h3>
                <div className="flex flex-wrap gap-2">
                  {quizGenerationMode === 'bert' && (
                    <span className="text-xs bg-blue-500 px-3 py-1 rounded-full">Généré par IA</span>
                  )}
                  {quizGenerationMode === 'personalized' && (
                    <span className="text-xs bg-green-500 px-3 py-1 rounded-full">Personnalisé</span>
                  )}
                </div>
              </div>
              <p className="mb-6 text-sm sm:text-base">Testez vos connaissances sur {selectedCourse?.titre}</p>

              {loadingQuestions ? (
                <div className="text-center py-8">
                  <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-white mb-2"></div>
                  <p>Chargement des questions...</p>
                </div>
              ) : questions.length > 0 ? (
                !quizSubmitted ? (
                  <>
                    {questions.map((q, idx) => (
                      <div key={q.id} className="bg-white/10 rounded-lg p-4 mb-4">
                        <p className="font-semibold mb-3 text-sm sm:text-base">
                          Question {idx + 1} ({q.points} points - {q.difficulte})
                        </p>
                        <p className="mb-3 text-sm sm:text-base">{q.question}</p>
                        <div className="space-y-2">
                          {Object.entries(q.options).map(([key, value]) => (
                            <label key={key} className="flex items-start gap-3 cursor-pointer text-sm sm:text-base">
                              <input
                                type="radio"
                                name={`question_${q.id}`}
                                value={key}
                                checked={userAnswers[q.id] === key}
                                onChange={() => handleAnswerSelect(q.id, key)}
                                className="w-4 h-4 mt-1 flex-shrink-0"
                              />
                              <span className="break-words">{key}: {value}</span>
                            </label>
                          ))}
                        </div>
                        <button
                          onClick={() => toggleExplanation(q.id)}
                          className="mt-3 text-sm text-purple-200 hover:text-white"
                        >
                          💡 Voir l'explication
                        </button>
                        {showExplanation[q.id] && (
                          <div className="mt-2 p-2 bg-white/20 rounded text-sm">
                            {q.explication}
                          </div>
                        )}
                      </div>
                    ))}
                    <button
                      onClick={handleSubmitQuiz}
                      disabled={Object.keys(userAnswers).length !== questions.length || !isAuthenticated}
                      className="w-full mt-4 px-6 py-3 bg-white text-purple-600 rounded-lg font-semibold hover:bg-gray-100 transition disabled:opacity-50 text-sm sm:text-base"
                    >
                      📤 Soumettre le quiz
                    </button>
                  </>
                ) : (
                  <div className="bg-white/10 rounded-lg p-6 text-center">
                    <div className="text-5xl mb-4">🎉</div>
                    <h4 className="text-xl sm:text-2xl font-bold mb-2">Résultats du quiz</h4>
                    <p className="text-2xl sm:text-3xl font-bold mb-2">{quizScore.toFixed(1)}%</p>
                    <p className="mb-4 text-sm sm:text-base">
                      {quizScore >= 70 ? '✅ Félicitations !' : '⚠️ Revoyez la leçon et réessayez.'}
                    </p>
                    <div className="flex flex-wrap gap-2 justify-center">
                      <button
                        onClick={resetQuiz}
                        className="px-4 sm:px-6 py-2 bg-white text-purple-600 rounded-lg hover:bg-gray-100 text-sm sm:text-base"
                      >
                        🔄 Recommencer
                      </button>
                      <button
                        onClick={generateBertQuiz}
                        disabled={generatingQuiz}
                        className="px-4 sm:px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 text-sm sm:text-base"
                      >
                        {generatingQuiz ? '⏳...' : '🤖 Nouveau quiz IA'}
                      </button>
                      <button
                        onClick={generatePersonalizedQuiz}
                        disabled={generatingQuiz}
                        className="px-4 sm:px-6 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 text-sm sm:text-base"
                      >
                        {generatingQuiz ? '⏳...' : '🎯 Quiz personnalisé'}
                      </button>
                    </div>
                  </div>
                )
              ) : (
                <div className="text-center py-8 bg-white/10 rounded-lg">
                  <p>📝 Aucune question disponible.</p>
                  <div className="flex flex-wrap gap-2 justify-center mt-4">
                    <button
                      onClick={generateBertQuiz}
                      disabled={generatingQuiz}
                      className="px-4 sm:px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 text-sm sm:text-base"
                    >
                      🤖 Générer quiz IA
                    </button>
                    <button
                      onClick={generatePersonalizedQuiz}
                      disabled={generatingQuiz}
                      className="px-4 sm:px-6 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 text-sm sm:text-base"
                    >
                      🎯 Quiz personnalisé
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}

          
          {showRecommendations && !examMode && (
            <div className="bg-gradient-to-r from-indigo-500 to-purple-600 rounded-xl p-4 sm:p-6 text-white">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="text-2xl sm:text-3xl">🤖</div>
                  <div>
                    <h3 className="text-lg sm:text-xl font-bold">Tuteur IA</h3>
                    <p className="text-xs sm:text-sm opacity-90">Recommandations personnalisées basées sur vos erreurs</p>
                  </div>
                </div>
                <button
                  onClick={() => setShowRecommendations(false)}
                  className="text-white/70 hover:text-white transition text-xl"
                >
                  ✕
                </button>
              </div>
              
              {loadingRecommendations ? (
                <div className="flex items-center justify-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
                  <span className="ml-3 text-sm">Analyse de vos résultats en cours...</span>
                </div>
              ) : recommendations.length > 0 ? (
                <div className="space-y-3">
                  <p className="text-sm mb-2">
                    🎯 Basé sur vos erreurs, voici les cours recommandés par notre IA :
                  </p>
                  {recommendations.map((rec, idx) => (
                    <div 
                      key={idx}
                      onClick={() => navigateToCourse(rec.cours_id)}
                      className="bg-white/10 rounded-lg p-3 sm:p-4 cursor-pointer hover:bg-white/20 transition-all duration-200 group"
                    >
                      <div className="flex flex-col sm:flex-row justify-between items-start gap-2">
                        <div className="flex-1 w-full">
                          <div className="flex items-center gap-2">
                            <span className="text-lg sm:text-xl">
                              {rec.direct_match ? '🎯' : '📚'}
                            </span>
                            <h4 className="font-semibold group-hover:underline text-sm sm:text-base">
                              {rec.cours_titre}
                            </h4>
                          </div>
                          <p className="text-xs sm:text-sm opacity-80 mt-1">{rec.description}</p>
                          {rec.nb_erreurs > 0 && (
                            <div className="flex flex-wrap items-center gap-2 mt-2">
                              <span className="text-xs bg-yellow-500/30 px-2 py-0.5 rounded-full">
                                🔴 {rec.nb_erreurs} erreur(s) liée(s)
                              </span>
                              <span className="text-xs bg-green-500/30 px-2 py-0.5 rounded-full">
                                Score: {(rec.score * 100).toFixed(0)}%
                              </span>
                            </div>
                          )}
                        </div>
                        <div className="text-right self-end sm:self-center">
                          <div className="bg-white/20 rounded-full w-8 h-8 flex items-center justify-center group-hover:bg-white/30 transition">
                            ➡️
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-6">
                  <p className="text-sm">Aucune recommandation disponible pour le moment.</p>
                  <p className="text-xs opacity-70 mt-1">Continuez à faire des quiz pour obtenir des suggestions personnalisées.</p>
                </div>
              )}
            </div>
          )}

          
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4">
            <button
              onClick={() => navigate('/courses')}
              className="px-3 sm:px-4 py-2 bg-gray-100 rounded-lg hover:bg-gray-200 transition text-xs sm:text-sm"
            >
              📚 Catalogue
            </button>
            <button
              onClick={() => {
                if (selectedCourse) {
                  navigate(`/learning/video/${selectedCourse.id}`);
                } else {
                  navigate('/learning/video');
                }
              }}
              className="px-3 sm:px-4 py-2 bg-gray-100 rounded-lg hover:bg-gray-200 transition text-xs sm:text-sm"
            >
              🎬 Vidéo
            </button>
            <button
              onClick={() => {
                if (selectedCourse) {
                  navigate(`/learning/audio/${selectedCourse.id}`);
                } else {
                  navigate('/learning/audio');
                }
              }}
              className="px-3 sm:px-4 py-2 bg-gray-100 rounded-lg hover:bg-gray-200 transition text-xs sm:text-sm"
            >
              🔊 Audio
            </button>
            <button
              onClick={() => navigate('/')}
              className="px-3 sm:px-4 py-2 bg-gray-100 rounded-lg hover:bg-gray-200 transition text-xs sm:text-sm"
            >
              🏠 Accueil
            </button>
          </div>
        </div>
      )}
    </div>
  </div>
  
);
};

export default TextLearningPage;
