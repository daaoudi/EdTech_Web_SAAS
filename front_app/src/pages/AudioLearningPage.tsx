/* eslint-disable @typescript-eslint/no-unused-vars */
/* eslint-disable react-hooks/exhaustive-deps */
/* eslint-disable @typescript-eslint/no-explicit-any */
/* eslint-disable */

import { useState, useRef, useEffect, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { courseService } from '../services/courseService';
import type { Course } from '../services/courseService';
import api from '../services/api';
import { bertQuizService , bertRecommendationService } from '../services/bertService';
import { mistakeService } from '../services/mistakeService';


interface Recommendation {
  cours_id: string;
  cours_titre: string;
  score: number;
  description: string;
  direct_match: boolean;
  nb_erreurs: number;
}

interface Question {
  id: number;
  question: string;
  options: Record<string, string>;
  reponse_correcte: string;
  points: number;
  difficulte: string;
  explication?: string;
}

interface AudioContent {
  title: string;
  description: string;
  audioFile: string;
  chapters: { time: number; timeStr: string; title: string }[];
  transcript: { time: number; timeStr: string; text: string }[];
}

interface AudioFile {
  name: string;
  path: string;
  size: number;
  url: string;
}




const AudioLearningPage = () => {
  const { isAuthenticated, user } = useAuth();
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [selectedCourse, setSelectedCourse] = useState<Course | null>(null);
  const [loading, setLoading] = useState(true);
  const [quizSubmitted, setQuizSubmitted] = useState(false);
  const [quizScore, setQuizScore] = useState(0);
  const [userAnswers, setUserAnswers] = useState<Record<number, string>>({});
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
const [showRecommendations, setShowRecommendations] = useState(false);
const [loadingRecommendations, setLoadingRecommendations] = useState(false);
  
  const [showExplanation, setShowExplanation] = useState<Record<number, boolean>>({});
  const [notes, setNotes] = useState('');
  const [currentAudioFile, setCurrentAudioFile] = useState('');
  const [audioError, setAudioError] = useState<string | null>(null);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [loadingQuestions, setLoadingQuestions] = useState(false);
  const [quizResultId, setQuizResultId] = useState<number | null>(null);
  const [audioContent, setAudioContent] = useState<AudioContent | null>(null);
  const [courses, setCourses] = useState<Course[]>([]);
  const [audioFiles, setAudioFiles] = useState<AudioFile[]>([]);
  const [loadingAudio, setLoadingAudio] = useState(false);
  const [generatingQuiz, setGeneratingQuiz] = useState(false);
  const [quizGenerationMode, setQuizGenerationMode] = useState<'default' | 'bert' | 'personalized'>('default');
  const [mistakeQuestions, setMistakeQuestions] = useState<string[]>([]);
  const [examMode, setExamMode] = useState(false);
const [examQuestions, setExamQuestions] = useState<Question[]>([]);
const [examSubmitted, setExamSubmitted] = useState(false);
const [examResult, setExamResult] = useState<any>(null);
const [examAnswers, setExamAnswers] = useState<Record<number, string>>({});
const [generatingExam, setGeneratingExam] = useState(false);

  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');


  const filteredCourses = courses.filter(course =>
  course.titre.toLowerCase().includes(searchTerm.toLowerCase())
);

const saveMistakesToDB = async (userId: number, courseId: number, wrongQuestions: { question: string; questionId: number }[]) => {
  if (!userId || !courseId || wrongQuestions.length === 0) return;
  
  try {
    const mistakesToSave = wrongQuestions.map(q => {
      
      const foundQuestion = questions.find(qu => qu.id === q.questionId);
      return {
        cours_id: courseId,
        question_id: q.questionId,
        question_texte: q.question,
        reponse_utilisateur: userAnswers[q.questionId] || '',
        reponse_correcte: foundQuestion?.reponse_correcte || '',
        mode_apprentissage: 'audio',
        points_possibles: 10
      };
    });
    
    await mistakeService.saveBatchMistakes(mistakesToSave);
    console.log('✅ Erreurs sauvegardées en DB');
  } catch (error) {
    console.error('❌ Erreur sauvegarde DB:', error);
  }
};

const loadMistakesFromDB = async (userId: number, courseId: number) => {
  if (!userId || !courseId) return [];
  
  try {
    const mistakes = await mistakeService.getMyMistakes(courseId, 'audio', 30);
    const mistakeTexts = mistakes.map((m: any) => m.question_texte);
    setMistakeQuestions(mistakeTexts);
    return mistakeTexts;
  } catch (error) {
    console.error('❌ Erreur chargement erreurs:', error);
    return [];
  }
};



const analyzeMistakesAndRecommend = async (wrongQuestions: string[]) => {
  if (!user?.id || wrongQuestions.length === 0) {
    console.log('Aucune erreur à analyser');
    return;
  }
  
  setLoadingRecommendations(true);
  
  try {
    console.log(`🤖 Tuteur IA analyse ${wrongQuestions.length} erreur(s)...`);
    
   
    const response = await bertRecommendationService.recommendCourses(
      wrongQuestions, 
      0.5,  
      5     
    );
    
    if (response && response.recommendations && response.recommendations.length > 0) {
      setRecommendations(response.recommendations);
      setShowRecommendations(true);
      
      
      const toast = document.createElement('div');
      toast.className = 'fixed bottom-4 right-4 bg-indigo-500 text-white px-4 py-2 rounded-lg shadow-lg z-50';
      toast.innerHTML = `🤖 Tuteur IA: ${response.recommendations.length} cours recommandés pour réviser vos erreurs!`;
      document.body.appendChild(toast);
      setTimeout(() => toast.remove(), 5000);
      
      console.log('✅ Recommandations générées:', response.recommendations);
    } else {
      console.log('⚠️ Aucune recommandation trouvée');
      
      
      const fallbackRecs = generateFallbackRecommendations(wrongQuestions);
      if (fallbackRecs.length > 0) {
        setRecommendations(fallbackRecs);
        setShowRecommendations(true);
        
        const toast = document.createElement('div');
        toast.className = 'fixed bottom-4 right-4 bg-blue-500 text-white px-4 py-2 rounded-lg shadow-lg z-50';
        toast.innerHTML = `🤖 Tuteur IA: ${fallbackRecs.length} cours recommandés (mode secours)`;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 4000);
      }
    }
  } catch (error) {
    console.error('❌ Erreur recommandation IA:', error);
    
    
    const fallbackRecs = generateFallbackRecommendations(wrongQuestions);
    if (fallbackRecs.length > 0) {
      setRecommendations(fallbackRecs);
      setShowRecommendations(true);
      
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


const generateFallbackRecommendations = (wrongQuestions: string[]): Recommendation[] => {
  const recommendations: Recommendation[] = [];
  const matchedCourses = new Set<string>();
  
  
  const keywordToCourse: Record<string, { id: string; title: string; description: string }> = {
    "titre principal": {
      id: "6",
      title: "Formatage du Texte en HTML",
      description: "Maîtrisez les balises de titre et de formatage de texte"
    },
    "lien hypertexte": {
      id: "11",
      title: "Les Liens Hypertextes en HTML",
      description: "Apprenez à créer et styliser des liens hypertextes"
    },
    "image": {
      id: "12",
      title: "Images en HTML",
      description: "Intégrez et optimisez des images sur vos pages web"
    },
    "formulaire": {
      id: "8",
      title: "Formulaires HTML Avancés",
      description: "Créez des formulaires interactifs avec validation"
    },
    "sémantique": {
      id: "9",
      title: "HTML5 Sémantique",
      description: "Structurez vos pages avec les balises sémantiques"
    },
    "flexbox": {
      id: "10",
      title: "CSS Flexbox & Grid",
      description: "Maîtrisez les mises en page modernes"
    },
    "tableau": {
      id: "13",
      title: "Les Tableaux en HTML",
      description: "Organisez vos données avec les tableaux"
    },
    "head": {
      id: "14",
      title: "HTML Head - Métadonnées",
      description: "Découvrez la balise <head> et son importance pour le SEO"
    },
    "multimédia": {
      id: "15",
      title: "HTML Multimédia",
      description: "Intégrez vidéo et audio avec les balises HTML5"
    },
    "media query": {
      id: "16",
      title: "CSS Media Queries",
      description: "Créez des sites responsives avec les media queries"
    },
    "sélecteur": {
      id: "17",
      title: "CSS - Les Sélecteurs",
      description: "Apprenez à cibler les éléments avec les sélecteurs CSS"
    },
    "couleur": {
      id: "18",
      title: "CSS - Couleurs",
      description: "Maîtrisez les différentes notations de couleurs en CSS"
    },
    "background": {
      id: "19",
      title: "CSS - Arrière-plans",
      description: "Utilisez les images et couleurs d'arrière-plan"
    },
    "bordure": {
      id: "20",
      title: "CSS - Bordures",
      description: "Stylisez les bordures de vos éléments"
    },
    "margin": {
      id: "22",
      title: "CSS - Marges",
      description: "Contrôlez l'espacement extérieur des éléments"
    },
    "padding": {
      id: "23",
      title: "CSS - Padding",
      description: "Gérez l'espacement intérieur des éléments"
    },
    "javascript": {
      id: "33",
      title: "JavaScript - Introduction",
      description: "Découvrez les bases du JavaScript"
    },
    "variable": {
      id: "34",
      title: "JavaScript - Variables",
      description: "Apprenez à déclarer et utiliser des variables"
    },
    "fonction": {
      id: "41",
      title: "JavaScript - Fonctions",
      description: "Maîtrisez les fonctions JavaScript"
    }
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


const navigateToRecommendedCourse = (courseId: string) => {
  const course = courses.find(c => String(c.id) === courseId);
  if (course) {
    setSelectedCourse(course);
    setShowRecommendations(false);
    window.scrollTo({ top: 0, behavior: 'smooth' });
    
    setTimeout(() => loadQuestions(course.id), 100);
    
    const toast = document.createElement('div');
    toast.className = 'fixed bottom-4 right-4 bg-green-500 text-white px-4 py-2 rounded-lg shadow-lg z-50';
    toast.textContent = `📚 Chargement du cours: ${course.titre}`;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 2000);
  }
};
  
  
  const audioRef = useRef<HTMLAudioElement>(null);
  const AUDIO_BASE_URL = 'http://127.0.0.1:8001/static/audio';


  const generateFallbackQuestionsFromMistakes = (mistakes: string[]): Question[] => {
  const questions: Question[] = [];
  
  
  const mistakeToQuestion: Record<string, Question> = {
    "Quelle balise utiliser pour le titre principal d'une page HTML ?": {
      id: 9991,
      question: "Quelle est la différence entre <title> et <h1> en HTML ?",
      options: {
        A: "<title> apparaît dans l'onglet, <h1> est le titre visible sur la page",
        B: "<h1> apparaît dans l'onglet, <title> est le titre visible",
        C: "Ils font la même chose",
        D: "<title> est déprécié, utilisez <h1> uniquement"
      },
      reponse_correcte: "A",
      points: 15,
      difficulte: "moyen",
      explication: "<title> définit le titre dans l'onglet du navigateur, tandis que <h1> est le titre principal visible sur la page."
    },
    "Quelle balise HTML est utilisée pour créer un lien hypertexte ?": {
      id: 9992,
      question: "Quel attribut est utilisé avec la balise <a> pour spécifier l'URL de destination ?",
      options: {
        A: "src",
        B: "url",
        C: "href",
        D: "link"
      },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "L'attribut href (Hypertext REFerence) spécifie l'URL de destination du lien."
    }
  };
  
  for (const mistake of mistakes) {
    if (mistakeToQuestion[mistake]) {
      questions.push({ ...mistakeToQuestion[mistake], id: questions.length + 1 });
    } else {
      
      questions.push({
        id: questions.length + 1,
        question: `Révision: ${mistake.substring(0, 80)}`,
        options: {
          A: "Révisez ce concept dans la leçon",
          B: "Consultez la documentation officielle",
          C: "Pratiquez avec des exercices supplémentaires",
          D: "Regardez la vidéo explicative"
        },
        reponse_correcte: "A",
        points: 10,
        difficulte: "moyen",
        explication: `Pour maîtriser ce concept, nous vous recommandons de revoir la section concernant: ${mistake}`
      });
    }
  }
  
  return questions.slice(0, 5);
};

const generatePersonalizedQuiz = async () => {
  if (!selectedCourse || !user?.id) {
    console.log('❌ Pas de cours sélectionné ou utilisateur non connecté');
    return;
  }
  
  try {
    setGeneratingQuiz(true);
    setQuizGenerationMode('personalized');
    setQuizSubmitted(false);
    setUserAnswers({});
    setShowExplanation({});
    
    
    const response = await api.post('/bert/quiz-from-mistakes', {
      course_id: String(selectedCourse.id),
      mode: 'audio',
      num_questions: 5
    });
    
    if (response.data && response.data.quiz && response.data.quiz.questions && response.data.quiz.questions.length > 0) {
      const formattedQuestions = response.data.quiz.questions.map((q: any, idx: number) => ({
        id: idx + 1,
        question: q.question,
        options: q.options || { A: "Option A", B: "Option B", C: "Option C", D: "Option D" },
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
    } else {
      throw new Error('Aucune question générée');
    }
    
  } catch (error) {
    console.error('❌ Erreur génération quiz personnalisé:', error);
    
    
    const toast = document.createElement('div');
    toast.className = 'fixed bottom-4 right-4 bg-orange-500 text-white px-4 py-2 rounded-lg shadow-lg z-50';
    toast.textContent = '⚠️ Génération du quiz standard...';
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
    
    await generateBertQuiz();
  } finally {
    setGeneratingQuiz(false);
  }
};

useEffect(() => {
  if (selectedCourse && selectedCourse.id && user?.id) {
    loadMistakesFromDB(user.id, selectedCourse.id);
  }
}, [selectedCourse, user?.id]);


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
🎧 Mode avec + erreurs: ${stats.mode_plus_erreurs || 'N/A'}
    `);
  } catch (error) {
    console.error('Erreur stats:', error);
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
        const questionText = q.question || '';
        
        if (questionText.includes("modifier le contenu texte") || questionText.includes("innerHTML")) {
          options = {
            A: "element.value = nouveauTexte",
            B: "element.innerHTML = nouveauTexte",
            C: "element.text = nouveauTexte",
            D: "element.content = nouveauTexte"
          };
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
            const defaultValues = ["Première option", "Deuxième option", "Troisième option", "Quatrième option"];
            cleanValue = defaultValues[i];
          }
          cleanOptions[key] = cleanValue;
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
      toast.textContent = `✅ Quiz IA généré! ${formattedQuestions.length} questions.`;
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
    await loadQuestions(selectedCourse.id);
  } finally {
    setGeneratingQuiz(false);
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
  
  
  if (question.includes("surligner")) {
    return { A: "<mark>", B: "<highlight>", C: "<strong>", D: "<em>" };
  }
  if (question.includes("pliable") || question.includes("dépliable")) {
    return { A: "<details> et <summary>", B: "<collapse> et <expand>", 
             C: "<fold> et <unfold>", D: "<hide> et <show>" };
  }
  if (question.includes("sémantique")) {
    return { A: "Meilleur SEO et accessibilité", B: "Chargement plus rapide",
             C: "Design plus joli", D: "Compatibilité avec plus de navigateurs" };
  }
  if (question.includes("titre principal")) {
    return { A: "<title>", B: "<h1>", C: "<head>", D: "<header>" };
  }
  if (question.includes("ligne dans un tableau")) {
    return { A: "<td>", B: "<tr>", C: "</table>", D: "<th>" };
  }
  if (question.includes("sélecteur CSS") && question.includes("paragraphes")) {
    return { A: "p", B: "#paragraph", C: ".paragraph", D: "<p>" };
  }
  if (question.includes("<main>")) {
    return { A: "0 fois", B: "1 fois", C: "2 fois", D: "Autant qu'on veut" };
  }
  if (question.includes("taille du texte") || question.includes("propriete CSS")) {
    return { A: "text-size", B: "font-size", C: "size", D: "text-scale" };
  }
  
  return { A: "Option A", B: "Option B", C: "Option C", D: "Option D" };
}

const generateFinalExam = async () => {
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
          options = { A: "<details> et <summary>", B: "<collapse> et <expand>", 
                      C: "<fold> et <unfold>", D: "<hide> et <show>" };
          correctAnswer = "A";
        } else if (questionText.includes("sémantique")) {
          options = { A: "Meilleur SEO et accessibilité", B: "Chargement plus rapide",
                      C: "Design plus joli", D: "Compatibilité avec plus de navigateurs" };
          correctAnswer = "A";
        } else if (questionText.includes("modifier le contenu texte") || questionText.includes("innerHTML")) {
          options = { A: "element.value = nouveauTexte", B: "element.innerHTML = nouveauTexte",
                      C: "element.text = nouveauTexte", D: "element.content = nouveauTexte" };
          correctAnswer = "B";
        } else if (questionText.includes("titre principal")) {
          options = { A: "<title>", B: "<h1>", C: "<head>", D: "<header>" };
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
      const defaultQs = getDefaultQuestionsForCourse(selectedCourse.id);
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
    const toast = document.createElement('div');
    toast.className = 'fixed bottom-4 right-4 bg-yellow-500 text-white px-4 py-2 rounded-lg shadow-lg z-50';
    toast.textContent = '⚠️ Utilisation des questions par défaut pour l\'examen';
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
    
    
    if (questions.length > 0) {
      const fallbackQuestions = [...questions];
      while (fallbackQuestions.length < 12) {
        fallbackQuestions.push({...fallbackQuestions[fallbackQuestions.length % fallbackQuestions.length]});
      }
      setExamQuestions(fallbackQuestions.slice(0, 12));
    }
  } finally {
    setGeneratingExam(false);
  }
};


const submitExam = async () => {
  if (!selectedCourse || !isAuthenticated) {
    alert('Veuillez vous connecter');
    return;
  }
  
  const answeredCount = Object.keys(examAnswers).length;
  if (answeredCount !== examQuestions.length) {
    alert(`Veuillez répondre à toutes les questions (${answeredCount}/${examQuestions.length})`);
    return;
  }
  
  let totalScore = 0;
  let maxScore = 0;
  const answersList: any[] = [];
  const wrongQuestionsList: { question: string; questionId: number }[] = [];

  for (const q of examQuestions) {
    maxScore += q.points;
    const userAnswer = examAnswers[q.id];
    const isCorrect = userAnswer === q.reponse_correcte;
    if (isCorrect) {
      totalScore += q.points;
    } else {
      wrongQuestionsList.push({
        question: q.question,
        questionId: q.id
      });
      console.log('❌ Erreur examen:', q.question);
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
  
  setExamResult({ score: totalScore, total: maxScore, percentage, passed, answers: answersList });
  setExamSubmitted(true);
  
  
  if (wrongQuestionsList.length > 0 && user?.id && selectedCourse?.id) {
    await saveMistakesToDB(user.id, selectedCourse.id, wrongQuestionsList);
    await loadMistakesFromDB(user.id, selectedCourse.id);
    
    
    const wrongQuestionTexts = wrongQuestionsList.map(w => w.question);
    await analyzeMistakesAndRecommend(wrongQuestionTexts);
  }
  
  try {
    await api.post('/results', {
      utilisateur_id: user?.id,
      cours_id: selectedCourse.id,
      mode: 'audio_exam',
      score_quiz: percentage,
      temps_passe: Math.floor(currentTime),
      taux_completion: progress,
      est_reussi: passed,
      feedback: passed ? `Examen réussi! Score: ${percentage.toFixed(1)}%` : `Score: ${percentage.toFixed(1)}%`
    });
    
    let examMessage = `📝 Examen terminé!\nScore: ${percentage.toFixed(1)}%\n${passed ? '✅ Félicitations!' : '📚 Continuez à pratiquer!'}`;
    if (wrongQuestionsList.length > 0) {
      examMessage += `\n\n🤖 Tuteur IA: ${wrongQuestionsList.length} erreur(s) analysée(s).\nDes cours de révision vous sont recommandés.`;
    }
    alert(examMessage);
  } catch (error) {
    console.error('Erreur sauvegarde examen:', error);
    alert('Erreur lors de l\'enregistrement de l\'examen. Veuillez réessayer.');
  }
};




const cancelExam = () => {
  setExamMode(false);
  setExamSubmitted(false);
  setExamResult(null);
  setExamAnswers({});
  setExamQuestions([]);
  setGeneratingExam(false);
};
  

  
  const getAudioContentForCourse = useCallback((course: Course, audioFileName: string): AudioContent => {
    
    const contentMap: Record<number, Partial<AudioContent>> = {
      6: {
        title: "Formatage du Texte en HTML",
        description: "Apprenez à formater le texte avec les balises HTML",
        chapters: [
          { time: 0, timeStr: "00:00", title: "Introduction au formatage texte" },
          { time: 120, timeStr: "02:00", title: "Les balises de base (h1-h6, p)" },
          { time: 240, timeStr: "04:00", title: "La balise strong et em" },
          { time: 360, timeStr: "06:00", title: "Les listes (ul, ol, li)" }
        ],
        transcript: [
          { time: 0, timeStr: "00:00", text: "Bienvenue dans ce cours sur le formatage du texte en HTML." },
          { time: 120, timeStr: "02:00", text: "Les balises de titre h1 à h6 permettent de structurer votre contenu." },
          { time: 240, timeStr: "04:00", text: "Utilisez strong pour le texte important et em pour l'emphase." }
        ]
      },
      11: {
        title: "Les Liens Hypertextes en HTML",
        description: "Maîtrisez la création de liens hypertextes",
        chapters: [
          { time: 0, timeStr: "00:00", title: "Introduction aux liens hypertextes" },
          { time: 150, timeStr: "02:30", title: "Création de la page d'accueil index.html" },
          { time: 240, timeStr: "04:00", title: "Introduction à la balise <a>" },
          { time: 360, timeStr: "06:00", title: "Travail avec les sous-dossiers" },
          { time: 600, timeStr: "10:00", title: "Liens externes et attribut target" }
        ],
        transcript: [
          { time: 0, timeStr: "00:00", text: "Bienvenue dans ce cours sur les liens hypertextes en HTML." },
          { time: 150, timeStr: "02:30", text: "La page d'accueil se nomme traditionnellement index.html." },
          { time: 240, timeStr: "04:00", text: "La balise <a> avec l'attribut href crée des liens." },
          { time: 360, timeStr: "06:00", text: "Utilisez ../ pour remonter d'un niveau." }
        ]
      }
    };

    
    const fileContentMap: Record<string, Partial<AudioContent>> = {
      'html_js_events.mp3': {
    title: "JavaScript Events - Handlers vs Listeners",
    description: "Apprenez la différence entre les gestionnaires d'événements et les écouteurs d'événements en JavaScript",
    chapters: [
      { time: 0, timeStr: "00:00", title: "Introduction aux événements" },
      { time: 12, timeStr: "00:12", title: "Les événements : clics, survols, etc." },
      { time: 43, timeStr: "00:43", title: "Utilisation des gestionnaires d'événements (onclick)" },
      { time: 109, timeStr: "01:49", title: "Utilisation des écouteurs d'événements (addEventListener)" },
      { time: 180, timeStr: "03:00", title: "Différence clé démontrée" },
      { time: 258, timeStr: "04:18", title: "Bonne pratique : préférer les écouteurs" },
      { time: 286, timeStr: "04:46", title: "Conclusion - Handlers vs Listeners" }
    ],
    transcript: [
      { time: 0, timeStr: "00:00", text: "Bienvenue dans ce cours sur les événements en JavaScript. Les événements permettent de réagir aux actions de l'utilisateur comme les clics de bouton ou les survols de souris." },
      { time: 12, timeStr: "00:12", text: "Les événements incluent des actions comme les clics de bouton ou les survols de souris. Il existe deux façons principales de les gérer." },
      { time: 43, timeStr: "00:43", text: "Les gestionnaires d'événements comme onclick ne permettent qu'une seule fonction par événement. Exemple avec un bouton qui affiche un message dans la console." },
      { time: 109, timeStr: "01:49", text: "Les écouteurs d'événements avec addEventListener permettent d'attacher plusieurs fonctions au même événement, ce qui les rend plus flexibles." },
      { time: 180, timeStr: "03:00", text: "La différence clé : avec deux handlers onclick, le second remplace le premier. Avec deux addEventListener, les deux s'exécutent. C'est démontré avec des exemples concrets." },
      { time: 258, timeStr: "04:18", text: "Bonne pratique : préférez les écouteurs d'événements aux gestionnaires. Ils sont plus flexibles et évolutifs pour les applications complexes." },
      { time: 286, timeStr: "04:46", text: "En conclusion, les handlers permettent une seule fonction par événement, les listeners permettent plusieurs fonctions. Les écouteurs d'événements sont recommandés pour le développement JavaScript moderne." }
    ]
  },
      'html_js_regex.mp3': {
    title: "JavaScript Regular Expressions - Les Regex",
    description: "Apprenez à utiliser les expressions régulières en JavaScript pour rechercher et manipuler du texte",
    chapters: [
      { time: 0, timeStr: "00:00", title: "Introduction aux expressions régulières" },
      { time: 20, timeStr: "00:20", title: "Qu'est-ce qu'une expression régulière ?" },
      { time: 65, timeStr: "01:05", title: "Créer une expression régulière" },
      { time: 130, timeStr: "02:10", title: "Les flags (g, i, m)" },
      { time: 180, timeStr: "03:00", title: "Classes de caractères" },
      { time: 255, timeStr: "04:15", title: "Exemples pratiques : validation email" },
      { time: 350, timeStr: "05:50", title: "Méthodes match, search, replace" },
      { time: 390, timeStr: "06:30", title: "Conclusion - Regex pour le traitement de texte" }
    ],
    transcript: [
      { time: 0, timeStr: "00:00", text: "Bienvenue dans ce cours sur les expressions régulières en JavaScript. Les expressions régulières sont des séquences de caractères qui définissent des motifs de recherche." },
      { time: 20, timeStr: "00:20", text: "Une expression régulière permet de rechercher, extraire ou remplacer du texte dans une chaîne. C'est un outil puissant pour la manipulation de texte." },
      { time: 65, timeStr: "01:05", text: "On peut créer une regex de deux façons : avec le littéral /pattern/ ou avec le constructeur new RegExp. Le littéral est recommandé pour sa simplicité." },
      { time: 130, timeStr: "02:10", text: "Les flags modifient le comportement de la recherche. g pour global (trouve toutes les occurrences), i pour insensible à la casse, m pour multiligne." },
      { time: 180, timeStr: "03:00", text: "Les classes de caractères : [a-z] pour les lettres minuscules, [0-9] pour les chiffres, \\d pour les chiffres, \\w pour les caractères alphanumériques, \\s pour les espaces." },
      { time: 255, timeStr: "04:15", text: "Exemple pratique : validation d'email. Une regex peut vérifier qu'un email contient @ et un domaine valide. On utilise la méthode test() pour valider." },
      { time: 350, timeStr: "05:50", text: "match() retourne un tableau des correspondances. search() retourne l'index de la première correspondance. replace() remplace les correspondances par un nouveau texte." },
      { time: 390, timeStr: "06:30", text: "En conclusion, les regex sont un outil puissant pour le traitement de texte. Utilisez-les pour la validation, la recherche et le formatage de données." }
    ]
  },
      'html_js_math_objects.mp3': {
    title: "JavaScript Math Object - L'Objet Math",
    description: "Apprenez à utiliser l'objet Math en JavaScript pour les opérations mathématiques",
    chapters: [
      { time: 0, timeStr: "00:00", title: "Introduction à l'objet Math" },
      { time: 6, timeStr: "00:06", title: "Constantes Mathématiques (PI, E)" },
      { time: 62, timeStr: "01:02", title: "Méthodes d'arrondi (round, floor, ceil, trunc)" },
      { time: 138, timeStr: "02:18", title: "Puissances et racines (pow, sqrt)" },
      { time: 173, timeStr: "02:53", title: "Logarithmes (log, log10, log2)" },
      { time: 186, timeStr: "03:06", title: "Fonctions trigonométriques" },
      { time: 224, timeStr: "03:44", title: "Valeur absolue et signe (abs, sign)" },
      { time: 267, timeStr: "04:27", title: "Maximum et Minimum (max, min)" },
      { time: 314, timeStr: "05:14", title: "Conclusion - Outil puissant pour les maths" }
    ],
    transcript: [
      { time: 0, timeStr: "00:00", text: "Bienvenue dans ce cours sur l'objet Math en JavaScript. Math est un objet intégré qui fournit des constantes et méthodes pour les opérations mathématiques." },
      { time: 6, timeStr: "00:06", text: "L'objet Math fournit des constantes utiles comme Math.PI pour le nombre pi et Math.E pour la constante d'Euler. Ces constantes évitent de les définir manuellement." },
      { time: 62, timeStr: "01:02", text: "Les méthodes d'arrondi : Math.round arrondit à l'entier le plus proche. Math.floor arrondit toujours vers le bas. Math.ceil arrondit toujours vers le haut. Math.trunc supprime la partie décimale." },
      { time: 138, timeStr: "02:18", text: "Math.pow permet d'élever un nombre à une puissance. Math.sqrt calcule la racine carrée. Par exemple, Math.pow(2,3) donne 8, Math.sqrt(16) donne 4." },
      { time: 173, timeStr: "02:53", text: "Math.log calcule le logarithme naturel. Math.log10 et Math.log2 calculent les logarithmes en base 10 et base 2." },
      { time: 186, timeStr: "03:06", text: "Les fonctions trigonométriques comme Math.sin, Math.cos, Math.tan travaillent avec des radians. Par exemple, pour 45 degrés, on convertit d'abord en radians." },
      { time: 224, timeStr: "03:44", text: "Math.abs retourne la valeur absolue d'un nombre. Math.sign indique si un nombre est positif, négatif ou nul, retournant 1, -1 ou 0." },
      { time: 267, timeStr: "04:27", text: "Math.max trouve la plus grande valeur parmi les arguments. Math.min trouve la plus petite. On peut aussi les utiliser avec l'opérateur spread sur un tableau." },
      { time: 314, timeStr: "05:14", text: "En conclusion, l'objet Math est un outil puissant pour les opérations mathématiques. Il fournit des constantes et méthodes essentielles pour les arrondis, puissances, racines, trigonométrie et comparaisons." }
    ]
  },
      'html_js_maps.mp3': {
    title: "JavaScript Maps - Les Dictionnaires",
    description: "Apprenez à utiliser les Maps en JavaScript pour stocker des paires clé-valeur avec n'importe quel type de clé",
    chapters: [
      { time: 0, timeStr: "00:00", title: "Introduction à Map" },
      { time: 30, timeStr: "00:30", title: "Map stocke des paires clé-valeur" },
      { time: 72, timeStr: "01:12", title: "Créer une Map avec new Map()" },
      { time: 125, timeStr: "02:05", title: "Ajouter des entrées avec set" },
      { time: 180, timeStr: "03:00", title: "Récupérer des valeurs avec get" },
      { time: 225, timeStr: "03:45", title: "Vérifier des clés avec has" },
      { time: 260, timeStr: "04:20", title: "Parcourir une Map avec forEach et for...of" },
      { time: 370, timeStr: "06:10", title: "Conclusion - Map vs Object" }
    ],
    transcript: [
      { time: 0, timeStr: "00:00", text: "Bienvenue dans ce cours sur les Maps en JavaScript. Map est une structure de données qui stocke des paires clé-valeur, introduite avec ES6." },
      { time: 30, timeStr: "00:30", text: "Map stocke des paires clé-valeur. Contrairement aux objets, les clés peuvent être de n'importe quel type : chaînes, nombres, objets. L'ordre d'insertion est préservé." },
      { time: 72, timeStr: "01:12", text: "Pour créer une Map, on utilise le constructeur new Map. On peut aussi l'initialiser avec un tableau de paires clé-valeur, par exemple pour stocker des codes de pays." },
      { time: 125, timeStr: "02:05", text: "La méthode set permet d'ajouter de nouvelles paires clé-valeur. On peut enchaîner les appels set car il retourne la Map elle-même." },
      { time: 180, timeStr: "03:00", text: "Pour récupérer une valeur, on utilise get avec la clé. Si la clé n'existe pas, get retourne undefined. C'est très utile pour accéder aux données stockées." },
      { time: 225, timeStr: "03:45", text: "has permet de vérifier si une clé existe dans la Map. Elle retourne true ou false. C'est utile avant d'appeler get pour éviter les undefined." },
      { time: 260, timeStr: "04:20", text: "Pour parcourir une Map, on peut utiliser forEach qui reçoit la valeur puis la clé. On peut aussi utiliser for...of qui déstructure chaque entrée en [clé, valeur]." },
      { time: 370, timeStr: "06:10", text: "En conclusion, Map est flexible et puissant. Différence clé avec Object : Map accepte tout type de clé, a une propriété size, et est directement itérable. Utilisez Map pour des dictionnaires avancés." }
    ]
  },
      'html_js_sets.mp3': {
    title: "JavaScript Sets - Les Ensembles",
    description: "Apprenez à utiliser les Sets en JavaScript pour stocker des valeurs uniques",
    chapters: [
      { time: 0, timeStr: "00:00", title: "Introduction aux Sets" },
      { time: 43, timeStr: "00:43", title: "Pourquoi utiliser les Sets ?" },
      { time: 86, timeStr: "01:26", title: "Créer un Set (new Set)" },
      { time: 157, timeStr: "02:37", title: "Suppression automatique des doublons" },
      { time: 189, timeStr: "03:09", title: "Ajouter des valeurs avec add" },
      { time: 246, timeStr: "04:06", title: "Parcourir un Set avec forEach" },
      { time: 358, timeStr: "05:58", title: "Vérifier des valeurs avec has" },
      { time: 394, timeStr: "06:34", title: "Conclusion - Set vs Array" }
    ],
    transcript: [
      { time: 0, timeStr: "00:00", text: "Bienvenue dans ce cours sur les Sets en JavaScript. Set est une structure de données qui stocke des valeurs uniques. Contrairement aux tableaux, les Sets ne permettent pas les doublons." },
      { time: 43, timeStr: "00:43", text: "Les tableaux autorisent les doublons, mais Set impose l'unicité. C'est très utile pour filtrer les valeurs répétées dans une collection de données." },
      { time: 86, timeStr: "01:26", text: "Pour créer un Set, on utilise le constructeur new Set. Par exemple, en utilisant le mot 'bookkeeper', on obtient un Set de lettres uniques comme b, o, k, e, p, r." },
      { time: 157, timeStr: "02:37", text: "Le mot 'bookkeeper' a 10 caractères, mais Set ne stocke que 6 lettres uniques. Les doublons sont automatiquement ignorés lors de la création du Set." },
      { time: 189, timeStr: "03:09", text: "La méthode add permet d'insérer de nouvelles valeurs. Si on essaie d'ajouter un doublon, il est simplement ignoré. Set fonctionne avec différents types de données." },
      { time: 246, timeStr: "04:06", text: "Pour parcourir un Set, on utilise la méthode forEach. Il n'y a pas d'indices, l'itération se concentre uniquement sur les valeurs. On peut aussi utiliser la boucle for...of." },
      { time: 358, timeStr: "05:58", text: "La méthode has vérifie si une valeur existe dans le Set et retourne true ou false. Attention, la vérification est sensible à la casse, donc 'Pomme' et 'pomme' sont différents." },
      { time: 394, timeStr: "06:34", text: "En conclusion, Set stocke des valeurs uniques, préserve l'ordre d'insertion, et fournit des méthodes simples comme add, has, delete, clear et la propriété size. Contrairement aux tableaux, Set n'a pas d'indices." }
    ]
  },
      'html_js_arrays.mp3': {
    title: "JavaScript Arrays - Les Tableaux",
    description: "Apprenez à utiliser les tableaux en JavaScript pour stocker et manipuler plusieurs valeurs",
    chapters: [
      { time: 0, timeStr: "00:00", title: "Introduction aux tableaux" },
      { time: 1, timeStr: "00:01", title: "Les tableaux stockent plusieurs valeurs dans une variable" },
      { time: 66, timeStr: "01:06", title: "Accéder aux éléments avec les indices" },
      { time: 136, timeStr: "02:16", title: "Méthodes : push, pop, unshift, shift" },
      { time: 192, timeStr: "03:12", title: "La propriété length" },
      { time: 243, timeStr: "04:03", title: "Trouver des éléments avec indexOf" },
      { time: 301, timeStr: "05:01", title: "Parcourir un tableau avec for...of" },
      { time: 440, timeStr: "07:20", title: "Trier avec sort et inverser avec reverse" },
      { time: 468, timeStr: "07:48", title: "Conclusion - Tableaux pour organiser les données" }
    ],
    transcript: [
      { time: 0, timeStr: "00:00", text: "Bienvenue dans ce cours sur les tableaux en JavaScript. Les tableaux sont des variables spéciales qui peuvent stocker plusieurs valeurs." },
      { time: 1, timeStr: "00:01", text: "Les valeurs sont placées entre crochets et séparées par des virgules. Les tableaux aident à organiser des collections de données." },
      { time: 66, timeStr: "01:06", text: "Pour accéder aux éléments, on utilise des indices qui commencent à 0. Par exemple, fruits[0] donne la première valeur du tableau." },
      { time: 136, timeStr: "02:16", text: "Les méthodes importantes : push ajoute à la fin, pop retire de la fin, unshift ajoute au début, shift retire du début." },
      { time: 192, timeStr: "03:12", text: "La propriété length donne le nombre d'éléments dans le tableau. Elle se met à jour dynamiquement quand on ajoute ou retire des éléments." },
      { time: 243, timeStr: "04:03", text: "indexOf retourne la position d'un élément dans le tableau. Si l'élément n'est pas trouvé, il retourne -1." },
      { time: 301, timeStr: "05:01", text: "Pour parcourir un tableau, on peut utiliser une boucle for classique ou la boucle for...of qui offre une syntaxe plus propre." },
      { time: 440, timeStr: "07:20", text: "sort permet de trier les éléments alphabétiquement, et reverse inverse l'ordre du tableau." },
      { time: 468, timeStr: "07:48", text: "En conclusion, les tableaux sont des structures polyvalentes pour gérer plusieurs valeurs. Ils sont essentiels en JavaScript." }
    ]
  },
      'html_js_objects.mp3': {
    title: "JavaScript Objects - Les Objets",
    description: "Apprenez à créer et utiliser des objets en JavaScript pour modéliser des entités du monde réel",
    chapters: [
      { time: 0, timeStr: "00:00", title: "Introduction - Qu'est-ce qu'un objet ?" },
      { time: 6, timeStr: "00:06", title: "Les objets : collections de propriétés et méthodes" },
      { time: 42, timeStr: "00:42", title: "Créer un objet personne (SpongeBob)" },
      { time: 107, timeStr: "01:47", title: "Accéder aux propriétés avec dot notation" },
      { time: 148, timeStr: "02:28", title: "Ajouter un deuxième objet (Patrick)" },
      { time: 245, timeStr: "04:05", title: "Ajouter des méthodes (sayHello, eat)" },
      { time: 329, timeStr: "05:29", title: "Les objets exécutent des actions" },
      { time: 391, timeStr: "06:31", title: "Conclusion - Objets pour modéliser le réel" }
    ],
    transcript: [
      { time: 0, timeStr: "00:00", text: "Bienvenue dans ce cours sur les objets en JavaScript. Les objets sont des collections de propriétés et de méthodes associées." },
      { time: 6, timeStr: "00:06", text: "Les propriétés décrivent les attributs comme le nom et l'âge. Les méthodes sont des fonctions liées à l'objet qui représentent des actions." },
      { time: 42, timeStr: "00:42", text: "Exemple avec SpongeBob : prénom, nom de famille, âge, statut d'emploi. Les propriétés sont définies comme des paires clé-valeur." },
      { time: 107, timeStr: "01:47", text: "Pour accéder aux propriétés, on utilise la notation pointée comme personnage.prenom. Cela fonctionne pour tous les attributs." },
      { time: 148, timeStr: "02:28", text: "On crée un objet Patrick avec des propriétés similaires. Chaque objet a besoin d'un nom unique comme personnage1, personnage2." },
      { time: 245, timeStr: "04:05", text: "On ajoute des méthodes comme direBonjour à SpongeBob et Patrick. On peut utiliser des expressions de fonction ou des fonctions fléchées." },
      { time: 329, timeStr: "05:29", text: "On ajoute une méthode manger avec des messages personnalisés pour chaque personnage. Les méthodes représentent les comportements." },
      { time: 391, timeStr: "06:31", text: "En conclusion, les objets combinent propriétés et méthodes. Ils sont utiles pour modéliser des entités du monde réel en JavaScript." }
    ]
  },
       'html_js_functions.mp3': {
    title: "JavaScript Functions - Les Fonctions",
    description: "Apprenez à créer et utiliser des fonctions en JavaScript pour organiser votre code",
    chapters: [
      { time: 0, timeStr: "00:00", title: "Introduction - Qu'est-ce qu'une fonction ?" },
      { time: 7, timeStr: "00:07", title: "Les fonctions comme blocs de code réutilisables" },
      { time: 76, timeStr: "01:16", title: "Appeler (invoquer) une fonction" },
      { time: 124, timeStr: "02:04", title: "Paramètres et arguments" },
      { time: 284, timeStr: "04:44", title: "Le mot-clé return" },
      { time: 400, timeStr: "06:40", title: "Fonctions mathématiques (addition, soustraction, multiplication, division)" },
      { time: 457, timeStr: "07:37", title: "Vérifier si un nombre est pair" },
      { time: 576, timeStr: "09:36", title: "Validation d'email avec includes()" },
      { time: 730, timeStr: "12:10", title: "Conclusion - Réutilisez vos fonctions" }
    ],
    transcript: [
      { time: 0, timeStr: "00:00", text: "Bienvenue dans ce cours sur les fonctions en JavaScript. Les fonctions sont des blocs de code réutilisables qui effectuent des tâches spécifiques." },
      { time: 7, timeStr: "00:07", text: "Une fonction est déclarée une fois et peut être exécutée plusieurs fois quand on en a besoin. Exemple : une fonction 'Joyeux Anniversaire' qui affiche des paroles." },
      { time: 76, timeStr: "01:16", text: "Pour appeler une fonction, on utilise son nom suivi de parenthèses. Les fonctions peuvent être exécutées plusieurs fois. Les parenthèses sont essentielles." },
      { time: 124, timeStr: "02:04", text: "Les fonctions peuvent accepter des valeurs appelées arguments. Les paramètres sont des placeholders dans la fonction. Exemple : passer un nom et un âge pour personnaliser le message." },
      { time: 284, timeStr: "04:44", text: "Le mot-clé return permet à une fonction de renvoyer une valeur. Exemple : une fonction addition(x, y) retourne la somme. On peut stocker le résultat dans une variable." },
      { time: 400, timeStr: "06:40", text: "Les fonctions mathématiques : soustraction retourne la différence, multiplication retourne le produit, division retourne le quotient." },
      { time: 457, timeStr: "07:37", text: "Pour vérifier si un nombre est pair, on utilise l'opérateur modulo. On peut utiliser un if/else ou un opérateur ternaire pour une syntaxe plus concise." },
      { time: 576, timeStr: "09:36", text: "Pour valider un email, on crée une fonction qui vérifie si la chaîne contient le caractère '@' avec la méthode includes(). On peut utiliser un opérateur ternaire." },
      { time: 730, timeStr: "12:10", text: "En conclusion, les fonctions sont des blocs de code réutilisables. Les paramètres et arguments permettent la flexibilité, et return permet de produire des résultats." }
    ]
  },
      'html_js_numbers_methods.mp3': {
    title: "JavaScript Numbers - Nombres et Méthodes",
    description: "Apprenez à manipuler les nombres en JavaScript : entiers, décimaux, méthodes et NaN",
    chapters: [
      { time: 0, timeStr: "00:00", title: "Introduction aux nombres" },
      { time: 8, timeStr: "00:08", title: "Entiers et décimaux" },
      { time: 85, timeStr: "01:25", title: "Comparaison de nombres" },
      { time: 125, timeStr: "02:05", title: "Convertir des chaînes en nombres" },
      { time: 175, timeStr: "02:55", title: "Conversion booléenne" },
      { time: 191, timeStr: "03:11", title: "Méthodes Number : isInteger, parseFloat, toFixed, parseInt" },
      { time: 259, timeStr: "04:19", title: "Enchaînement de méthodes" },
      { time: 309, timeStr: "05:09", title: "Comprendre NaN (isNaN vs Number.isNaN)" },
      { time: 346, timeStr: "05:46", title: "Conclusion" }
    ],
    transcript: [
      { time: 0, timeStr: "00:00", text: "Bienvenue dans ce cours sur les nombres en JavaScript. Les nombres sont l'un des types de données les plus fondamentaux." },
      { time: 8, timeStr: "00:08", text: "JavaScript gère deux types de nombres : les entiers (nombres sans virgule) et les décimaux (nombres avec virgule). Le langage ignore les zéros finaux sauf si le nombre contient des décimales." },
      { time: 85, timeStr: "01:25", text: "La comparaison entre entiers et décimaux montre des différences. Comparer un nombre et une chaîne avec la même valeur retourne false en raison de la différence de type." },
      { time: 125, timeStr: "02:05", text: "La fonction Number() convertit une chaîne en nombre. Si la conversion échoue, elle retourne NaN, ce qui signifie 'Not a Number'." },
      { time: 175, timeStr: "02:55", text: "Number(true) retourne 1, Number(false) retourne 0. Cela montre que true équivaut à 1 et false à 0 en JavaScript." },
      { time: 191, timeStr: "03:11", text: "Les méthodes importantes : Number.isInteger() vérifie si une valeur est un entier, parseFloat() convertit en décimal, toFixed() limite les décimales et retourne une chaîne, parseInt() extrait un entier." },
      { time: 259, timeStr: "04:19", text: "On peut chaîner les méthodes pour plus d'efficacité. Notez que toFixed() retourne déjà une chaîne, donc toString() est souvent redondant." },
      { time: 309, timeStr: "05:09", text: "NaN est une valeur spéciale. Number.isNaN() vérifie si la valeur est NaN ET de type number. isNaN() globale vérifie seulement si la valeur n'est pas un nombre, ce qui peut être trompeur." },
      { time: 346, timeStr: "05:46", text: "En conclusion, apprenez à manipuler les nombres avec ces méthodes. Utilisez Number.isNaN() plutôt que isNaN() pour éviter les confusions." }
    ]
  },
      'html_js_strings_methods.mp3': {
    title: "JavaScript Strings - Chaînes de Caractères",
    description: "Apprenez à manipuler les chaînes de caractères en JavaScript et leurs méthodes essentielles",
    chapters: [
      { time: 0, timeStr: "00:00", title: "Introduction aux chaînes de caractères" },
      { time: 22, timeStr: "00:22", title: "Définition et importance des strings" },
      { time: 105, timeStr: "01:45", title: "Pourquoi les méthodes des chaînes sont importantes" },
      { time: 188, timeStr: "03:08", title: "Méthodes de base : length, toUpperCase, includes" },
      { time: 257, timeStr: "04:17", title: "Exemple pratique : trim()" },
      { time: 356, timeStr: "05:56", title: "Exemple pratique : includes()" },
      { time: 435, timeStr: "07:15", title: "Exemple pratique : split()" },
      { time: 636, timeStr: "10:36", title: "Conclusion - Maîtriser les méthodes des chaînes" }
    ],
    transcript: [
      { time: 0, timeStr: "00:00", text: "Bienvenue dans ce cours sur les chaînes de caractères en JavaScript. Les chaînes sont des séquences de caractères utilisées pour stocker et traiter du texte." },
      { time: 22, timeStr: "00:22", text: "Les chaînes sont délimitées par des guillemets simples ou doubles. Elles sont immuables, ce qui signifie que toute modification crée une nouvelle chaîne." },
      { time: 105, timeStr: "01:45", text: "Les méthodes des chaînes sont essentielles pour valider les entrées comme les emails et mots de passe, extraire des hashtags, formater des numéros de téléphone, et nettoyer des données." },
      { time: 188, timeStr: "03:08", text: "length compte le nombre de caractères. toUpperCase convertit tout en majuscules. includes vérifie si une sous-chaîne existe et retourne true ou false." },
      { time: 257, timeStr: "04:17", text: "trim supprime les espaces au début et à la fin d'une chaîne. C'est très utile pour nettoyer les entrées utilisateur dans les formulaires." },
      { time: 356, timeStr: "05:56", text: "includes recherche des mots spécifiques dans un texte. Elle retourne un booléen, ce qui est utile pour analyser des avis ou des commentaires." },
      { time: 435, timeStr: "07:15", text: "split convertit une chaîne CSV en tableau en découpant au niveau des virgules. On peut aussi l'utiliser pour extraire le nom d'utilisateur d'un email." },
      { time: 636, timeStr: "10:36", text: "Pour maîtriser les chaînes, apprenez la syntaxe, les arguments et les types de retour des méthodes. Pratiquez avec au moins 10 méthodes essentielles." }
    ]
  },
      'html_js_loops.mp3': {
    title: "JavaScript Loops - Les Boucles (for loop)",
    description: "Apprenez à utiliser les boucles en JavaScript pour répéter des actions efficacement",
    chapters: [
      { time: 0, timeStr: "00:00", title: "Introduction - Pourquoi utiliser des boucles" },
      { time: 4, timeStr: "00:04", title: "Pourquoi les boucles sont importantes" },
      { time: 54, timeStr: "00:54", title: "Structure de la boucle for" },
      { time: 136, timeStr: "02:16", title: "Déroulement d'une boucle for" },
      { time: 224, timeStr: "03:44", title: "Suivi des itérations" },
      { time: 278, timeStr: "04:38", title: "Variations de boucles" },
      { time: 354, timeStr: "05:54", title: "Conclusion - Flexibilité des boucles" }
    ],
    transcript: [
      { time: 0, timeStr: "00:00", text: "Bienvenue dans ce cours sur les boucles en JavaScript. Les boucles permettent de répéter des actions efficacement sans écrire de code répétitif." },
      { time: 4, timeStr: "00:04", text: "Répéter du code manuellement est inefficace. Les boucles automatisent la répétition avec une syntaxe plus propre et plus lisible." },
      { time: 54, timeStr: "00:54", text: "Une boucle for comporte trois parties : l'initialisation avec let i = 0, la condition avec i < 5, et l'incrément avec i++. Le code s'exécute tant que la condition est vraie." },
      { time: 136, timeStr: "02:16", text: "La boucle s'exécute tant que la condition est vraie. i s'incrémente après chaque itération. Par exemple, elle peut afficher Hello World cinq fois." },
      { time: 224, timeStr: "03:44", text: "La console affiche les valeurs de i de 0 à 4. La condition devient fausse quand i atteint 5, et la boucle s'arrête." },
      { time: 278, timeStr: "04:38", text: "On peut commencer à 1 et continuer tant que i <= 5. On peut utiliser if à l'intérieur pour n'afficher que les nombres impairs. On peut aussi faire une boucle inversée en commençant à 5 et en décrémentant." },
      { time: 354, timeStr: "05:54", text: "Les boucles sont flexibles pour différents scénarios. Les boucles inversées sont moins courantes mais utiles dans certains problèmes. Expérimentez avec les boucles." }
    ]
  },
      'html_js_if_conditions.mp3': {
    title: "JavaScript Conditions - If, Else, Else If",
    description: "Apprenez à utiliser les conditions en JavaScript pour prendre des décisions dans votre code",
    chapters: [
      { time: 0, timeStr: "00:00", title: "Introduction aux conditions" },
      { time: 10, timeStr: "00:10", title: "Pourquoi les programmes ont besoin de prendre des décisions" },
      { time: 38, timeStr: "00:38", title: "L'instruction if de base" },
      { time: 72, timeStr: "01:12", title: "Ajouter else (bloc alternatif)" },
      { time: 105, timeStr: "01:45", title: "Utiliser else if (multiples conditions)" },
      { time: 150, timeStr: "02:30", title: "Exemple pratique : système de notation" },
      { time: 185, timeStr: "03:05", title: "Conclusion - Résumé des conditions" },
      { time: 210, timeStr: "03:30", title: "Opérateurs de comparaison (>, <, ==, ===)" },
      { time: 270, timeStr: "04:30", title: "Opérateurs logiques (&&, ||, !)" },
      { time: 330, timeStr: "05:30", title: "Conditions imbriquées" },
      { time: 450, timeStr: "07:30", title: "L'opérateur ternaire" },
      { time: 600, timeStr: "10:00", title: "Exemples avancés" },
      { time: 900, timeStr: "15:00", title: "Bonnes pratiques et récapitulatif" }
    ],
    transcript: [
      { time: 0, timeStr: "00:00", text: "Bienvenue dans ce cours sur les conditions en JavaScript. Les conditions permettent aux programmes de prendre des décisions en fonction de différentes situations." },
      { time: 10, timeStr: "00:10", text: "Les programmes ont souvent besoin de faire des choix. Par exemple, vérifier si un utilisateur est majeur avant de lui donner accès à un contenu." },
      { time: 38, timeStr: "00:38", text: "L'instruction if est l'outil de base. Exemple : if (nombre > autreNombre) { console.log('Condition vraie'); }. Le code s'exécute seulement si la condition est vraie." },
      { time: 72, timeStr: "01:12", text: "else fournit un bloc alternatif. Si la condition est fausse, le bloc else s'exécute. Exemple : if (majeur) { accès } else { refus }." },
      { time: 105, timeStr: "01:45", text: "else if permet de vérifier plusieurs conditions à la suite. Par exemple, pour un système de notation : note >= 90 pour Excellent, note >= 80 pour Très bien, etc." },
      { time: 150, timeStr: "02:30", text: "Dans un système de notation réel, on utilise plusieurs conditions pour couvrir toutes les fourchettes de notes, du A+ au F." },
      { time: 185, timeStr: "03:05", text: "if, else if et else sont les fondations de la prise de décision en JavaScript. Entraînez-vous avec différentes conditions." },
      { time: 210, timeStr: "03:30", text: "Les opérateurs de comparaison incluent > (plus grand), < (plus petit), >= (plus grand ou égal), <= (plus petit ou égal), == (égalité en valeur), === (égalité en valeur et type)." },
      { time: 270, timeStr: "04:30", text: "Les opérateurs logiques sont && (ET), || (OU) et ! (NON). Ils permettent de combiner plusieurs conditions. Exemple : if (age >= 18 && aPermis)." },
      { time: 330, timeStr: "05:30", text: "Les conditions imbriquées placent un if à l'intérieur d'un autre if. Cela permet de vérifier des conditions dépendantes." },
      { time: 450, timeStr: "07:30", text: "L'opérateur ternaire est une forme raccourcie de if/else : condition ? valeur_si_vrai : valeur_si_faux. Exemple : let statut = (age >= 18) ? 'Majeur' : 'Mineur'." },
      { time: 600, timeStr: "10:00", text: "Exemples avancés : validation de formulaires, contrôle d'accès, jeux, calcul de prix avec promotions." },
      { time: 900, timeStr: "15:00", text: "Bonnes pratiques : utilisez des noms de variables clairs, évitez les conditions trop complexes, testez toujours les cas limites, et préférez === à == pour éviter les conversions implicites." }
    ]
  },
      'html_js_operators.mp3': {
    title: "JavaScript Operators - Les Opérateurs",
    description: "Apprenez à utiliser les opérateurs JavaScript : arithmétiques, d'assignation, de comparaison et logiques",
    chapters: [
      { time: 0, timeStr: "00:00", title: "Introduction aux opérateurs JavaScript" },
      { time: 15, timeStr: "00:15", title: "L'opérateur d'assignation (=)" },
      { time: 45, timeStr: "00:45", title: "Opérateurs arithmétiques (+, -, *, /, %, **)" },
      { time: 75, timeStr: "01:15", title: "Opérateurs d'assignation composés (+=, -=, *=, /=)" },
      { time: 105, timeStr: "01:45", title: "Opérateurs de comparaison (==, ===, !=, >, <)" },
      { time: 135, timeStr: "02:15", title: "Opérateurs logiques (&&, ||, !)" },
      { time: 165, timeStr: "02:45", title: "Concaténation de chaînes avec +" },
      { time: 195, timeStr: "03:15", title: "Conclusion - Bonnes pratiques" }
    ],
    transcript: [
      { time: 0, timeStr: "00:00", text: "Bienvenue dans ce cours sur les opérateurs JavaScript. Les opérateurs permettent d'effectuer des calculs mathématiques, des comparaisons et des opérations logiques." },
      { time: 15, timeStr: "00:15", text: "L'opérateur d'assignation = assigne une valeur à une variable. Par exemple, let x = 10 assigne la valeur 10 à la variable x." },
      { time: 45, timeStr: "00:45", text: "Les opérateurs arithmétiques incluent + pour l'addition, - pour la soustraction, * pour la multiplication, / pour la division, % pour le modulo (reste), et ** pour l'exponentiation." },
      { time: 75, timeStr: "01:15", text: "Les opérateurs d'assignation composés comme +=, -=, *=, /= permettent de combiner une opération arithmétique avec une assignation. x += 5 équivaut à x = x + 5." },
      { time: 105, timeStr: "01:45", text: "Les opérateurs de comparaison comparent deux valeurs. == compare la valeur, === compare la valeur et le type. >, <, >=, <= comparent les grandeurs." },
      { time: 135, timeStr: "02:15", text: "Les opérateurs logiques sont && (ET), || (OU) et ! (NON). Ils sont utilisés pour combiner des conditions et retournent true ou false." },
      { time: 165, timeStr: "02:45", text: "L'opérateur + sert aussi à concaténer des chaînes. 'Bonjour' + ' ' + 'monde' donne 'Bonjour monde'. Attention: 5 + '5' donne '55', pas 10." },
      { time: 195, timeStr: "03:15", text: "En conclusion, utilisez === plutôt que == pour éviter les conversions de type implicites. Les opérateurs sont essentiels pour manipuler les données." }
    ]
  },
      'html_js_datatypes.mp3': {
    title: "JavaScript Data Types - Types de Données",
    description: "Découvrez les 7 types de données fondamentaux en JavaScript",
    chapters: [
      { time: 0, timeStr: "00:00", title: "Introduction aux types de données" },
      { time: 12, timeStr: "00:12", title: "Boolean - Vrai ou Faux" },
      { time: 63, timeStr: "01:03", title: "Null - La valeur nulle" },
      { time: 97, timeStr: "01:37", title: "Undefined - Variable non assignée" },
      { time: 152, timeStr: "02:32", title: "Number - Nombres" },
      { time: 191, timeStr: "03:11", title: "String - Chaînes de caractères" },
      { time: 227, timeStr: "03:47", title: "Symbol - Identifiants uniques (ES6)" },
      { time: 334, timeStr: "05:34", title: "Object - Collections clé-valeur" },
      { time: 385, timeStr: "06:25", title: "Conclusion - Résumé des types" }
    ],
    transcript: [
      { time: 0, timeStr: "00:00", text: "Bienvenue dans ce cours sur les types de données en JavaScript. JavaScript possède sept types de données fondamentaux." },
      { time: 12, timeStr: "00:12", text: "Boolean représente une valeur logique, vrai ou faux. Par exemple, true pour 'les booléens règnent', false pour 'les booléens sont ennuyeux'." },
      { time: 63, timeStr: "01:03", text: "Null est une valeur d'assignation signifiant 'aucune valeur'. Dans les opérations mathématiques, null se comporte comme 0." },
      { time: 97, timeStr: "01:37", text: "Undefined signifie qu'une variable a été déclarée mais non assignée. Les opérations avec undefined donnent NaN, 'Not a Number'." },
      { time: 152, timeStr: "02:32", text: "Number représente n'importe quelle valeur numérique, entière ou décimale. Par exemple, 3.6 plus 6.4 donne 10." },
      { time: 191, timeStr: "03:11", text: "String représente du texte entre guillemets. Les chaînes peuvent être concaténées, par exemple 'Bonjour ' + 'monde'." },
      { time: 227, timeStr: "03:47", text: "Symbol est un type introduit en ES6 pour créer des identifiants uniques et immuables. Deux symboles avec la même description ne sont pas égaux." },
      { time: 334, timeStr: "05:34", text: "Object est une collection de paires clé-valeur. Par exemple, on peut créer une voiture avec les propriétés make, model et year." },
      { time: 385, timeStr: "06:25", text: "En conclusion, maîtrisez ces types pour mieux comprendre comment les valeurs sont stockées. Pratiquez et utilisez votre code pour le bien." }
    ]
  },
      'html_js_variables.mp3': {
    title: "JavaScript Variables - Les Variables",
    description: "Apprenez à utiliser les variables en JavaScript : déclaration avec var, let, const, et règles de nommage",
    chapters: [
      { time: 0, timeStr: "00:00", title: "Introduction - Que sont les variables ?" },
      { time: 6, timeStr: "00:06", title: "Les variables comme conteneurs de données" },
      { time: 33, timeStr: "00:33", title: "Déclaration des variables (var, let, const)" },
      { time: 83, timeStr: "01:23", title: "Règles de nommage (identifiants)" },
      { time: 119, timeStr: "01:59", title: "L'opérateur d'assignation (=)" },
      { time: 150, timeStr: "02:30", title: "Types de données (nombres et chaînes)" },
      { time: 188, timeStr: "03:08", title: "Conclusion - let vs const vs var" }
    ],
    transcript: [
      { time: 0, timeStr: "00:00", text: "Bienvenue dans ce cours sur les variables en JavaScript. Les variables sont des conteneurs qui permettent de stocker des données en mémoire." },
      { time: 6, timeStr: "00:06", text: "On peut imaginer une variable comme une boîte dans laquelle on met une valeur. Par exemple, goldCoins = 5, diamonds = 6, pizzaCoupons = 0." },
      { time: 33, timeStr: "00:33", text: "Il existe trois façons de déclarer une variable. var est l'ancienne méthode à éviter. let est pour les variables dont la valeur peut changer. const est pour les valeurs qui ne changent pas." },
      { time: 83, timeStr: "01:23", text: "Les noms de variables peuvent contenir des lettres, chiffres, $ et _. Ils doivent commencer par une lettre, $ ou _. Les mots réservés comme let ou const sont interdits." },
      { time: 119, timeStr: "01:59", text: "L'opérateur d'assignation = assigne une valeur à une variable. Ce n'est pas un signe d'égalité. Par exemple, x = x + 3 met à jour la valeur de x." },
      { time: 150, timeStr: "02:30", text: "Les nombres s'écrivent sans guillemets. Les chaînes de texte s'écrivent entre guillemets. Attention : '5' + 10 donne 510 (concaténation), pas 15." },
      { time: 188, timeStr: "03:08", text: "En conclusion, utilisez const par défaut. Si la valeur doit changer, utilisez let. Évitez var qui est déprécié. Les variables sont des conteneurs flexibles." }
    ]
  },
      'html_js_introduction.mp3': {
    title: "JavaScript Introduction - Les Bases",
    description: "Découvrez JavaScript, le langage de programmation du web, et apprenez à manipuler HTML et CSS",
    chapters: [
      { time: 0, timeStr: "00:00", title: "Qu'est-ce que JavaScript ?" },
      { time: 15, timeStr: "00:15", title: "JavaScript peut modifier le contenu HTML" },
      { time: 45, timeStr: "00:45", title: "JavaScript peut modifier les attributs HTML" },
      { time: 75, timeStr: "01:15", title: "JavaScript peut modifier les styles CSS" },
      { time: 105, timeStr: "01:45", title: "JavaScript peut masquer des éléments" },
      { time: 135, timeStr: "02:15", title: "JavaScript peut afficher des éléments masqués" },
      { time: 160, timeStr: "02:40", title: "Conclusion - JavaScript donne vie au web" }
    ],
    transcript: [
      { time: 0, timeStr: "00:00", text: "Bienvenue dans ce cours d'introduction à JavaScript. JavaScript est le langage de programmation du web. Il permet de rendre les pages web interactives et dynamiques." },
      { time: 15, timeStr: "00:15", text: "JavaScript peut modifier le contenu HTML. La méthode getElementById permet de trouver un élément HTML et de modifier son contenu avec innerHTML. Par exemple, on peut changer le texte d'un paragraphe." },
      { time: 45, timeStr: "00:45", text: "JavaScript peut également modifier les attributs HTML. On peut changer l'attribut src d'une image pour allumer ou éteindre une lampe, ou modifier n'importe quel autre attribut." },
      { time: 75, timeStr: "01:15", text: "JavaScript peut modifier les styles CSS. En changeant la propriété style.color, on peut changer la couleur du texte. style.fontSize permet d'agrandir le texte." },
      { time: 105, timeStr: "01:45", text: "JavaScript peut masquer des éléments HTML en modifiant la propriété display. Avec element.style.display = 'none', l'élément disparaît de la page." },
      { time: 135, timeStr: "02:15", text: "Pour réafficher un élément masqué, on utilise element.style.display = 'block'. Cela permet de créer des boutons pour afficher ou masquer du contenu." },
      { time: 160, timeStr: "02:40", text: "En conclusion, JavaScript est le langage qui donne vie aux pages web. Il peut tout modifier : contenu HTML, attributs, styles CSS, masquer et afficher des éléments." }
    ]
  },

      'html_css_float.mp3': {
    title: "CSS Float - Positionner les Éléments",
    description: "Apprenez à utiliser la propriété CSS float pour positionner des éléments à gauche ou à droite",
    chapters: [
      { time: 0, timeStr: "00:00", title: "Introduction à float" },
      { time: 7, timeStr: "00:07", title: "Flotter des éléments à gauche ou à droite" },
      { time: 39, timeStr: "00:39", title: "Flotter des images avec texte" },
      { time: 72, timeStr: "01:12", title: "Galeries d'images avec float" },
      { time: 113, timeStr: "01:53", title: "Interaction avec les éléments texte" },
      { time: 144, timeStr: "02:24", title: "La propriété clear" },
      { time: 184, timeStr: "03:04", title: "Conclusion - Clearfix et bonnes pratiques" }
    ],
    transcript: [
      { time: 0, timeStr: "00:00", text: "Bienvenue dans ce cours sur la propriété CSS float. Float permet de positionner un élément à gauche ou à droite, permettant au texte et aux autres éléments de s'enrouler autour." },
      { time: 7, timeStr: "00:07", text: "Les éléments peuvent flotter à gauche ou à droite. Les autres éléments s'enroulent autour de l'élément flottant. C'est très utile pour les images dans du texte." },
      { time: 39, timeStr: "00:39", text: "Par exemple, une image flottante à droite avec le texte qui s'enroule à gauche. Si on change float de droite à gauche, l'image se déplace mais le texte continue de s'enrouler." },
      { time: 72, timeStr: "01:12", text: "Avec plusieurs éléments flottants, ils s'alignent les uns à côté des autres si l'espace le permet. C'est idéal pour créer des galeries d'images qui s'adaptent au redimensionnement." },
      { time: 113, timeStr: "01:53", text: "Lorsqu'on ajoute un titre entre des images flottantes, le texte s'enroule à côté d'elles. Cela montre comment les flottants affectent les éléments suivants." },
      { time: 144, timeStr: "02:24", text: "La propriété clear empêche les éléments flottants d'apparaître sur le côté gauche, droit, ou les deux. Cela garantit que les titres ne se retrouvent pas coincés à côté des images." },
      { time: 184, timeStr: "03:04", text: "En conclusion, float permet un contrôle précis de l'alignement. Pour les conteneurs parents d'éléments flottants, utilisez la technique clearfix. Consultez W3Schools pour plus d'exemples." }
    ]
  },

      'html_css_overflow.mp3': {
    title: "CSS Overflow - Gérer le Dépassement de Contenu",
    description: "Apprenez à maîtriser la propriété CSS overflow pour gérer le contenu qui dépasse de son conteneur",
    chapters: [
      { time: 0, timeStr: "00:00", title: "Introduction à overflow" },
      { time: 7, timeStr: "00:07", title: "Qu'est-ce que le dépassement de contenu" },
      { time: 69, timeStr: "01:09", title: "overflow: visible (valeur par défaut)" },
      { time: 81, timeStr: "01:21", title: "overflow: hidden" },
      { time: 105, timeStr: "01:45", title: "overflow: clip" },
      { time: 145, timeStr: "02:25", title: "overflow: scroll" },
      { time: 172, timeStr: "02:52", title: "overflow: auto" },
      { time: 187, timeStr: "03:07", title: "Conclusion - Comment choisir" }
    ],
    transcript: [
      { time: 0, timeStr: "00:00", text: "Bienvenue dans ce cours sur la propriété CSS overflow. Overflow se produit lorsque le contenu dépasse les limites de son conteneur parent." },
      { time: 7, timeStr: "00:07", text: "CSS offre différentes façons de gérer cette situation. Les valeurs principales sont visible, hidden, clip, scroll et auto." },
      { time: 69, timeStr: "01:09", text: "visible est la valeur par défaut. Le contenu qui dépasse s'affiche en dehors de la boîte, sans aucune restriction." },
      { time: 81, timeStr: "01:21", text: "hidden coupe et cache le contenu qui dépasse. Il reste accessible, par exemple par copier-coller, même s'il n'est pas visible." },
      { time: 105, timeStr: "01:45", text: "clip est similaire à hidden mais fonctionne avec overflow-clip-margin. Cela permet un dépassement partiel jusqu'à une certaine marge avant de cacher le reste." },
      { time: 145, timeStr: "02:25", text: "scroll ajoute des barres de défilement verticales et horizontales, quel que soit le contenu. Les barres apparaissent même si elles ne sont pas nécessaires." },
      { time: 172, timeStr: "02:52", text: "auto ajoute des barres de défilement uniquement lorsque c'est nécessaire. C'est la solution la plus propre et recommandée." },
      { time: 187, timeStr: "03:07", text: "En conclusion, utilisez visible pour le comportement normal, hidden pour masquer les débordements, clip pour un contrôle précis, scroll pour des barres permanentes, et auto pour des barres conditionnelles." }
    ]
  },

      'html_css_positioning.mp3': {
    title: "CSS Positioning - Positionnement d'Éléments",
    description: "Apprenez à maîtriser le positionnement CSS : static, relative, absolute, fixed et sticky",
    chapters: [
      { time: 0, timeStr: "00:00", title: "Introduction au positionnement CSS" },
      { time: 5, timeStr: "00:05", title: "Les différentes valeurs de position" },
      { time: 42, timeStr: "00:42", title: "Position relative" },
      { time: 83, timeStr: "01:23", title: "Position absolute" },
      { time: 131, timeStr: "02:11", title: "Position fixed" },
      { time: 178, timeStr: "02:58", title: "Position sticky" },
      { time: 225, timeStr: "03:45", title: "Exemples pratiques" },
      { time: 276, timeStr: "04:36", title: "Conclusion - Résumé et bonnes pratiques" },
      { time: 300, timeStr: "05:00", title: "Propriétés top, right, bottom, left" },
      { time: 340, timeStr: "05:40", title: "z-index - Ordre d'empilement" },
      { time: 396, timeStr: "06:36", title: "Récapitulatif final" }
    ],
    transcript: [
      { time: 0, timeStr: "00:00", text: "Bienvenue dans ce cours sur le positionnement CSS. Le positionnement définit comment les éléments sont placés sur la page. Il existe cinq valeurs principales : static, relative, absolute, fixed et sticky." },
      { time: 5, timeStr: "00:05", text: "Par défaut, tous les éléments ont position: static. Cela signifie qu'ils suivent le flux normal de la page, dans l'ordre où ils apparaissent dans le HTML." },
      { time: 42, timeStr: "00:42", text: "position: relative permet de déplacer un élément par rapport à sa position normale. L'espace d'origine reste réservé. Utile pour des ajustements fins." },
      { time: 83, timeStr: "01:23", text: "position: absolute retire l'élément du flux normal. Il est positionné par rapport à son ancêtre positionné le plus proche. Sans ancêtre, il se positionne par rapport au body." },
      { time: 131, timeStr: "02:11", text: "position: fixed fixe l'élément par rapport à la fenêtre du navigateur. Il reste à la même place lors du défilement. Idéal pour les menus de navigation fixes." },
      { time: 178, timeStr: "02:58", text: "position: sticky alterne entre relative et fixed selon le défilement. L'élément reste collé à un seuil défini, par exemple en haut de la fenêtre." },
      { time: 225, timeStr: "03:45", text: "En pratique, on utilise relative pour créer un conteneur pour des éléments absolus, fixed pour les barres de navigation, et sticky pour les en-têtes de section." },
      { time: 276, timeStr: "04:36", text: "Les propriétés top, right, bottom, left permettent de déplacer les éléments positionnés. Fixed et sticky créent des éléments qui restent visibles pendant le défilement." },
      { time: 300, timeStr: "05:00", text: "top, right, bottom, left définissent le décalage par rapport à la référence. Pour absolute, la référence est l'ancêtre positionné. Pour fixed, c'est la fenêtre." },
      { time: 340, timeStr: "05:40", text: "z-index contrôle l'ordre d'empilement. Plus la valeur est élevée, plus l'élément apparaît au-dessus. Cela fonctionne uniquement sur les éléments positionnés." },
      { time: 396, timeStr: "06:36", text: "En conclusion, maîtrisez ces valeurs pour créer des mises en page complexes. Utilisez relative pour les conteneurs, absolute pour les tooltips, fixed pour les menus, sticky pour les en-têtes." }
    ]
  }
  ,
      'html_css_display_visibility.mp3': {
    title: "CSS Display & Visibility - Contrôler l'Affichage",
    description: "Apprenez la différence entre display et visibility pour contrôler l'affichage des éléments HTML",
    chapters: [
      { time: 0, timeStr: "00:00", title: "Introduction à Display et Visibility" },
      { time: 8, timeStr: "00:08", title: "Différence entre display et visibility" },
      { time: 29, timeStr: "00:29", title: "Masquer les éléments - visibility: hidden vs display: none" },
      { time: 113, timeStr: "01:53", title: "Éléments block vs inline" },
      { time: 163, timeStr: "02:43", title: "Exemple pratique: menu de navigation" },
      { time: 185, timeStr: "03:05", title: "Changer inline en block" },
      { time: 266, timeStr: "04:26", title: "Note importante - Sémantique vs Affichage" },
      { time: 292, timeStr: "04:52", title: "Conclusion - Résumé des différences" }
    ],
    transcript: [
      { time: 0, timeStr: "00:00", text: "Bienvenue dans ce cours sur les propriétés CSS display et visibility. Ces propriétés contrôlent comment les éléments sont affichés ou cachés sur la page." },
      { time: 8, timeStr: "00:08", text: "display contrôle comment et si un élément est rendu. visibility contrôle si un élément est visible mais conserve sa place dans la mise en page." },
      { time: 29, timeStr: "00:29", text: "visibility: hidden cache l'élément mais conserve l'espace qu'il occupe. display: none supprime complètement l'élément, comme s'il n'existait pas. Les autres éléments se repositionnent." },
      { time: 113, timeStr: "01:53", text: "Les éléments block prennent toute la largeur disponible et forcent un saut de ligne. Les éléments inline ne prennent que la largeur nécessaire et restent sur la même ligne." },
      { time: 163, timeStr: "02:43", text: "Pour créer un menu horizontal, on utilise display: inline sur les éléments li. Sans cette propriété, le menu s'affiche verticalement par défaut." },
      { time: 185, timeStr: "03:05", text: "On peut transformer des éléments inline comme span ou a en éléments block. Ils prennent alors toute la largeur et forcent des sauts de ligne." },
      { time: 266, timeStr: "04:26", text: "Note importante : changer display affecte le rendu visuel, pas la signification sémantique. Un élément inline transformé en block ne peut toujours pas contenir d'autres éléments block." },
      { time: 292, timeStr: "04:52", text: "En conclusion, utilisez visibility: hidden pour masquer en conservant l'espace, display: none pour supprimer complètement un élément, et display: inline pour créer des menus horizontaux." }
    ]
  }
  ,
      'html_css_tables.mp3': {
    title: "CSS Tables - Styliser les Tableaux en CSS",
    description: "Apprenez à styliser les tableaux HTML en CSS : bordures, collapse, alignement, espacement et couleurs",
    chapters: [
      { time: 0, timeStr: "00:00", title: "Introduction aux tableaux CSS" },
      { time: 7, timeStr: "00:07", title: "Améliorer l'apparence des tableaux avec CSS" },
      { time: 19, timeStr: "00:19", title: "Bordures des tableaux" },
      { time: 47, timeStr: "00:47", title: "Fusion des bordures (border-collapse: collapse)" },
      { time: 76, timeStr: "01:16", title: "Dimensions du tableau (width, height)" },
      { time: 121, timeStr: "02:01", title: "Alignement du texte (text-align, vertical-align)" },
      { time: 199, timeStr: "03:19", title: "Espacement intérieur (padding)" },
      { time: 232, timeStr: "03:52", title: "Couleurs et arrière-plans" },
      { time: 313, timeStr: "05:13", title: "Conclusion - Bonnes pratiques" }
    ],
    transcript: [
      { time: 0, timeStr: "00:00", text: "Bienvenue dans ce cours sur le stylage des tableaux en CSS. Les tableaux HTML peuvent être améliorés avec CSS pour les rendre plus attrayants et plus faciles à lire." },
      { time: 7, timeStr: "00:07", text: "CSS offre de nombreuses propriétés pour améliorer l'apparence des tableaux : bordures, fusion des bordures, dimensions, alignement, espacement, couleurs." },
      { time: 19, timeStr: "00:19", text: "La propriété border permet d'ajouter des bordures aux tableaux et aux cellules. Mais attention, lorsque les bordures sont appliquées au tableau ET aux cellules, des bordures doubles apparaissent." },
      { time: 47, timeStr: "00:47", text: "La propriété border-collapse: collapse résout ce problème en fusionnant les bordures doubles en une seule ligne. C'est la première propriété à appliquer pour des tableaux propres." },
      { time: 76, timeStr: "01:16", text: "Les dimensions du tableau se contrôlent avec width et height. width: 100% permet au tableau d'occuper toute la largeur. On peut aussi ajuster la hauteur des en-têtes." },
      { time: 121, timeStr: "02:01", text: "L'alignement du texte se fait avec text-align pour l'horizontal (left, center, right) et vertical-align pour le vertical (top, middle, bottom). Les en-têtes sont centrés par défaut." },
      { time: 199, timeStr: "03:19", text: "La propriété padding ajoute de l'espace entre le contenu et la bordure de la cellule. Cela rend le tableau plus aéré et plus facile à lire." },
      { time: 232, timeStr: "03:52", text: "Les couleurs et arrière-plans améliorent le design. On peut colorer les en-têtes, alterner les couleurs des lignes avec nth-child(even), et ajouter un effet de survol avec hover." },
      { time: 313, timeStr: "05:13", text: "En conclusion, pour des tableaux professionnels : utilisez border-collapse: collapse, ajoutez du padding, utilisez des couleurs alternées, un effet de survol, et rendez les tableaux responsives sur mobile." }
    ]
  },
      'html_css_lists.mp3': {
    title: "CSS Lists - Styliser les Listes en CSS",
    description: "Apprenez à styliser les listes HTML en CSS : puces, numéros, images personnalisées et menus de navigation",
    chapters: [
      { time: 0, timeStr: "00:00", title: "Introduction aux listes en CSS" },
      { time: 30, timeStr: "00:30", title: "list-style-type - Changer les puces et numéros" },
      { time: 60, timeStr: "01:00", title: "Valeurs pour listes non ordonnées (disc, circle, square)" },
      { time: 90, timeStr: "01:30", title: "Valeurs pour listes ordonnées (decimal, roman, alpha)" },
      { time: 120, timeStr: "02:00", title: "list-style-position (inside vs outside)" },
      { time: 150, timeStr: "02:30", title: "list-style-image - Images personnalisées" },
      { time: 180, timeStr: "03:00", title: "Propriété raccourcie list-style" },
      { time: 210, timeStr: "03:30", title: "Supprimer les puces pour menus de navigation" },
      { time: 240, timeStr: "04:00", title: "Listes imbriquées et stylisation" },
      { time: 270, timeStr: "04:30", title: "Exemples pratiques et menu horizontal" },
      { time: 300, timeStr: "05:00", title: "Bonnes pratiques et accessibilité" },
      { time: 447, timeStr: "07:27", title: "Conclusion - Récapitulatif" }
    ],
    transcript: [
      { time: 0, timeStr: "00:00", text: "Bienvenue dans ce cours sur le stylage des listes en CSS. Les listes HTML (ul et ol) peuvent être personnalisées pour améliorer l'apparence et la lisibilité de votre contenu." },
      { time: 30, timeStr: "00:30", text: "La propriété list-style-type permet de changer le type de marqueur. Pour les listes non ordonnées, on peut utiliser disc (puce pleine), circle (puce creuse), square (puce carrée), ou none (pas de puce)." },
      { time: 60, timeStr: "01:00", text: "Les puces par défaut sont disc. circle donne un cercle vide, square une forme carrée. Ces options permettent d'adapter le style à votre design." },
      { time: 90, timeStr: "01:30", text: "Pour les listes ordonnées, on peut utiliser decimal (1,2,3), decimal-leading-zero (01,02,03), lower-roman (i,ii,iii), upper-roman (I,II,III), lower-alpha (a,b,c) ou upper-alpha (A,B,C)." },
      { time: 120, timeStr: "02:00", text: "list-style-position contrôle l'emplacement du marqueur. outside place le marqueur à l'extérieur du bloc texte. inside le place à l'intérieur, le texte se décale pour s'aligner après la puce." },
      { time: 150, timeStr: "02:30", text: "list-style-image permet de remplacer la puce standard par une image personnalisée. Il est recommandé de toujours définir un fallback avec list-style-type au cas où l'image ne charge pas." },
      { time: 180, timeStr: "03:00", text: "La propriété raccourcie list-style combine type, position et image. Exemple : list-style: square inside url('puce.png'). Cela permet d'écrire du code plus concis." },
      { time: 210, timeStr: "03:30", text: "Pour créer des menus de navigation, on utilise souvent list-style-type: none pour supprimer les puces, puis on retire les marges et paddings par défaut." },
      { time: 240, timeStr: "04:00", text: "Pour les listes imbriquées, on peut styliser chaque niveau différemment. Par exemple, niveau 1 avec square, niveau 2 avec circle, niveau 3 avec disc." },
      { time: 270, timeStr: "04:30", text: "Un exemple pratique : un menu horizontal avec display: inline ou float: left sur les éléments li, combiné avec list-style-type: none et des paddings pour l'espacement." },
      { time: 300, timeStr: "05:00", text: "Bonnes pratiques : utilisez list-style-type: none pour les menus, privilégiez les images SVG pour list-style-image, utilisez des fallbacks, et pensez à l'accessibilité." },
      { time: 447, timeStr: "07:27", text: "En conclusion, maîtrisez ces propriétés pour créer des listes professionnelles. Expérimentez avec les différents types de marqueurs et les positions pour trouver le style parfait pour vos projets." }
    ]
  },
      'html_css_links.mp3': {
    title: "CSS Links - Styliser les Liens Hypertextes",
    description: "Apprenez à styliser les liens hypertextes en CSS avec les pseudo-classes :link, :visited, :hover et :active",
    chapters: [
      { time: 0, timeStr: "00:00", title: "Introduction au stylage des liens CSS" },
      { time: 3, timeStr: "00:03", title: "Les liens peuvent être stylisés avec couleur, police, arrière-plan" },
      { time: 28, timeStr: "00:28", title: "Les quatre états d'un lien" },
      { time: 67, timeStr: "01:07", title: "Changer les couleurs pour chaque état" },
      { time: 129, timeStr: "02:09", title: "L'ordre des règles CSS est important (LoVe HA!)" },
      { time: 154, timeStr: "02:34", title: "Décoration du texte (text-decoration)" },
      { time: 184, timeStr: "03:04", title: "Styliser l'arrière-plan et grouper les états" },
      { time: 254, timeStr: "04:14", title: "Conclusion - Expérimentez avec les liens" }
    ],
    transcript: [
      { time: 0, timeStr: "00:00", text: "Bienvenue dans ce cours sur le stylage des liens en CSS. Les liens hypertextes peuvent être stylisés avec différentes propriétés CSS : couleur, police, arrière-plan, décoration, et plus encore." },
      { time: 3, timeStr: "00:03", text: "Chaque lien peut avoir un style différent selon son état. Les liens sont des éléments interactifs essentiels sur le web, et un bon stylage améliore l'expérience utilisateur." },
      { time: 28, timeStr: "00:28", text: "Il existe quatre états pour un lien. Le premier est a:link, le lien normal non visité. Ensuite a:visited, le lien déjà cliqué. Puis a:hover, le lien survolé par la souris. Enfin a:active, le lien au moment du clic." },
      { time: 67, timeStr: "01:07", text: "Pour chaque état, on peut changer la couleur. Par exemple, bleu pour les liens non visités, rouge pour les liens visités, orange au survol, et vert au moment du clic." },
      { time: 129, timeStr: "02:09", text: "L'ordre des règles CSS est crucial. La règle hover doit venir après link et visited. La règle active doit venir après hover. Retenez la règle mnémotechnique LoVe HA! : Link, Visited, Hover, Active." },
      { time: 154, timeStr: "02:34", text: "La propriété text-decoration permet de contrôler le soulignement. On peut retirer le soulignement par défaut avec text-decoration: none, ou ajouter des effets comme line-through au survol." },
      { time: 184, timeStr: "03:04", text: "On peut aussi styliser l'arrière-plan des liens. Pour optimiser le code, on peut grouper les états qui partagent les mêmes styles, comme link et visited ensemble, puis hover et active ensemble." },
      { time: 254, timeStr: "04:14", text: "En conclusion, expérimentez avec les différentes pseudo-classes. N'oubliez pas l'ordre LoVe HA! et utilisez les transitions pour des effets fluides. Consultez la documentation pour plus d'exemples." }
    ]
  },
      'html_css_fonts.mp3': {
    title: "CSS Font - Propriétés des Polices",
    description: "Apprenez à maîtriser les propriétés CSS pour les polices : font-family, font-size, font-weight, font-style",
    chapters: [
      { time: 0, timeStr: "00:00", title: "Introduction aux propriétés CSS des polices" },
      { time: 8, timeStr: "00:08", title: "Familles de polices (font-family)" },
      { time: 61, timeStr: "01:01", title: "Serif vs Sans-serif vs Monospace" },
      { time: 117, timeStr: "01:57", title: "Système de fallback pour les polices" },
      { time: 191, timeStr: "03:11", title: "Style de police (font-style: normal, italic, oblique)" },
      { time: 240, timeStr: "04:00", title: "Taille de police (font-size: px, em, rem)" },
      { time: 439, timeStr: "07:19", title: "Graisse de police (font-weight)" },
      { time: 506, timeStr: "08:26", title: "Conclusion - Bonnes pratiques" }
    ],
    transcript: [
      { time: 0, timeStr: "00:00", text: "Bienvenue dans ce cours sur les propriétés CSS des polices. Les propriétés font permettent de contrôler l'apparence du texte : famille, taille, style, épaisseur." },
      { time: 8, timeStr: "00:08", text: "font-family définit la police du texte. Il existe des familles génériques comme serif, sans-serif, monospace, et des polices spécifiques comme Arial ou Times New Roman." },
      { time: 61, timeStr: "01:01", text: "Serif : polices avec empattements (petites lignes décoratives), comme Times New Roman. Sans-serif : polices sans empattements, comme Arial, plus modernes. Monospace : tous les caractères ont la même largeur, idéal pour le code." },
      { time: 117, timeStr: "01:57", text: "Le système de fallback permet de spécifier plusieurs polices séparées par des virgules. Le navigateur essaie la première, puis la seconde. Toujours terminer par une famille générique." },
      { time: 191, timeStr: "03:11", text: "font-style contrôle si le texte est en italique. Les valeurs sont normal, italic, et oblique. Italic est préféré car mieux supporté que oblique." },
      { time: 240, timeStr: "04:00", text: "font-size définit la taille du texte. Les pixels sont des unités absolues, les em et rem sont relatives. Pour l'accessibilité, privilégiez les unités relatives qui permettent le redimensionnement." },
      { time: 439, timeStr: "07:19", text: "font-weight contrôle l'épaisseur du texte. Les valeurs possibles sont normal, bold, ou des valeurs numériques de 100 à 900. 400 équivaut à normal, 700 à bold." },
      { time: 506, timeStr: "08:26", text: "En conclusion, maîtrisez font-family avec fallback, privilégiez les unités relatives pour la taille, utilisez italic pour l'italique et les valeurs numériques pour la graisse. Expérimentez avec ces propriétés pour créer des typographies uniques." }
    ]
  },
       'html_css_text.mp3': {
    title: "CSS Text - Propriétés de Mise en Forme du Texte",
    description: "Apprenez à maîtriser les propriétés CSS pour la mise en forme du texte",
    chapters: [
      { time: 0, timeStr: "00:00", title: "Introduction aux propriétés texte en CSS" },
      { time: 30, timeStr: "00:30", title: "Alignement du texte (text-align)" },
      { time: 60, timeStr: "01:00", title: "Décoration du texte (text-decoration)" },
      { time: 90, timeStr: "01:30", title: "Transformation du texte (text-transform)" },
      { time: 120, timeStr: "02:00", title: "Espacement (letter-spacing, word-spacing)" },
      { time: 150, timeStr: "02:30", title: "Hauteur de ligne (line-height)" },
      { time: 180, timeStr: "03:00", title: "Indentation du texte (text-indent)" },
      { time: 210, timeStr: "03:30", title: "Ombres du texte (text-shadow)" },
      { time: 240, timeStr: "04:00", title: "Couleur du texte (color)" },
      { time: 270, timeStr: "04:30", title: "Exemples pratiques combinés" },
      { time: 300, timeStr: "05:00", title: "Bonnes pratiques et accessibilité" },
      { time: 360, timeStr: "06:00", title: "Conclusion - Récapitulatif" }
    ],
    transcript: [
      { time: 0, timeStr: "00:00", text: "Bienvenue dans ce cours sur les propriétés CSS pour la mise en forme du texte. CSS offre de nombreuses propriétés pour styliser le texte : alignement, décoration, transformation, espacement, ombres, et bien plus encore." },
      { time: 30, timeStr: "00:30", text: "La propriété text-align contrôle l'alignement horizontal du texte. Les valeurs possibles sont left pour aligner à gauche, right pour aligner à droite, center pour centrer, et justify pour justifier le texte sur toute la largeur." },
      { time: 60, timeStr: "01:00", text: "text-decoration ajoute ou retire des effets décoratifs. underline souligne, overline ajoute une ligne au-dessus, line-through barre le texte, et none supprime toute décoration. Très utile pour les liens." },
      { time: 90, timeStr: "01:30", text: "text-transform contrôle la casse des lettres. uppercase met tout en majuscules, lowercase en minuscules, capitalize met la première lettre de chaque mot en majuscule." },
      { time: 120, timeStr: "02:00", text: "Pour l'espacement, letter-spacing contrôle l'espace entre les lettres, tandis que word-spacing contrôle l'espace entre les mots. Ces propriétés acceptent des valeurs en pixels ou en em." },
      { time: 150, timeStr: "02:30", text: "line-height définit la hauteur de ligne, c'est-à-dire l'interlignage. Une valeur de 1.4 à 1.6 est recommandée pour une bonne lisibilité." },
      { time: 180, timeStr: "03:00", text: "text-indent permet de décaler la première ligne d'un paragraphe. C'est très utile pour les articles de blog ou les paragraphes de texte longs." },
      { time: 210, timeStr: "03:30", text: "text-shadow ajoute une ombre portée au texte. La syntaxe est text-shadow: offset-x offset-y blur-radius color. Vous pouvez même ajouter plusieurs ombres séparées par des virgules." },
      { time: 240, timeStr: "04:00", text: "La propriété color définit la couleur du texte, avec plusieurs formats: noms de couleurs comme red, codes HEX comme #FF0000, RGB comme rgb(255,0,0), ou HSL." },
      { time: 270, timeStr: "04:30", text: "En pratique, vous pouvez combiner ces propriétés. Par exemple, un titre centré avec ombre, des liens sans soulignement qui s'affichent au survol, des paragraphes justifiés avec indentation." },
      { time: 300, timeStr: "05:00", text: "Bonnes pratiques : utilisez line-height pour améliorer la lisibilité, text-transform pour uniformiser la casse, et text-decoration: none sur les liens pour un design moderne tout en gardant un effet au survol." },
      { time: 360, timeStr: "06:00", text: "En conclusion, maîtrisez ces propriétés pour créer des typographies uniques et professionnelles. Expérimentez avec les combinaisons pour trouver le style parfait pour vos projets." }
    ]
  },
      'html_css_margin.mp3': {
    title: "CSS Margin - Les Marges en CSS",
    description: "Apprenez à utiliser les marges en CSS pour contrôler l'espacement extérieur des éléments",
    chapters: [
      { time: 0, timeStr: "00:00", title: "Introduction aux marges CSS" },
      { time: 12, timeStr: "00:12", title: "Définition des marges - espace extérieur" },
      { time: 65, timeStr: "01:05", title: "Les propriétés individuelles (margin-top, right, bottom, left)" },
      { time: 140, timeStr: "02:20", title: "La propriété raccourcie margin" },
      { time: 220, timeStr: "03:40", title: "Auto margins pour centrer les éléments" },
      { time: 256, timeStr: "04:16", title: "Conclusion - margin: 0 auto et margin collapsing" }
    ],
    transcript: [
      { time: 0, timeStr: "00:00", text: "Bienvenue dans ce cours sur les marges en CSS. Les marges créent de l'espace à l'extérieur de la bordure d'un élément, le poussant loin des autres éléments autour de lui." },
      { time: 12, timeStr: "00:12", text: "La marge est l'espace extérieur. Contrairement au padding, la marge est transparente et ne peut pas avoir de couleur d'arrière-plan. Elle sert à espacer les éléments entre eux." },
      { time: 65, timeStr: "01:05", text: "CSS permet de définir chaque marge individuellement avec margin-top pour le haut, margin-right pour la droite, margin-bottom pour le bas et margin-left pour la gauche. Chaque côté peut avoir une valeur différente." },
      { time: 140, timeStr: "02:20", text: "La propriété raccourcie margin permet de définir les quatre marges en une seule ligne. Une seule valeur s'applique aux quatre côtés. Deux valeurs : la première pour le haut et le bas, la seconde pour la droite et la gauche." },
      { time: 220, timeStr: "03:40", text: "margin: auto est très utile pour centrer horizontalement des éléments block. L'élément doit avoir une largeur définie. La syntaxe margin: 0 auto est la façon standard de centrer un élément." },
      { time: 256, timeStr: "04:16", text: "N'oubliez pas le margin collapsing : les marges verticales entre éléments adjacents se fusionnent en une seule marge. Utilisez margin: 0 auto pour centrer, et souvenez-vous de l'ordre horaire pour les quatre valeurs." }
    ]
  },
  
  'html_css_padding.mp3': {
    title: "CSS Padding - Le Remplissage en CSS",
    description: "Apprenez à utiliser le padding en CSS pour contrôler l'espacement intérieur des éléments",
    chapters: [
      { time: 0, timeStr: "00:00", title: "Introduction au padding CSS" },
      { time: 3, timeStr: "00:03", title: "Définition - espace entre contenu et bordure" },
      { time: 63, timeStr: "01:03", title: "Définir le padding individuellement par côté" },
      { time: 98, timeStr: "01:38", title: "La propriété raccourcie padding" },
      { time: 128, timeStr: "02:08", title: "Unités et pourcentages pour le padding" },
      { time: 237, timeStr: "03:57", title: "Conclusion - à l'intérieur de la bordure" }
    ],
    transcript: [
      { time: 0, timeStr: "00:00", text: "Bienvenue dans ce cours sur le padding en CSS. Le padding crée de l'espace à l'intérieur d'un élément, entre son contenu et sa bordure. Cela permet d'aérer le contenu." },
      { time: 3, timeStr: "00:03", text: "Contrairement à la marge, le padding est à l'intérieur de la bordure. Il peut avoir une couleur d'arrière-plan et rend l'élément plus spacieux intérieurement sans déplacer les éléments voisins." },
      { time: 63, timeStr: "01:03", text: "Vous pouvez définir des paddings différents sur chaque côté avec padding-top, padding-right, padding-bottom et padding-left. Par exemple, padding-top: 10px ajoute 10px au-dessus du contenu." },
      { time: 98, timeStr: "01:38", text: "La propriété raccourcie padding fonctionne comme margin. Une valeur pour les quatre côtés. Deux valeurs : la première pour haut et bas, la seconde pour droite et gauche. Trois ou quatre valeurs pour des réglages plus précis." },
      { time: 128, timeStr: "02:08", text: "Le padding peut être défini en pixels, points, ems, rems, ou pourcentages. Les pourcentages sont calculés par rapport à la largeur de l'élément parent, même pour les paddings verticaux." },
      { time: 237, timeStr: "03:57", text: "En conclusion, utilisez padding pour aérer l'intérieur de vos éléments. Le padding augmente la taille totale de l'élément par défaut, contrairement à la marge qui ajoute de l'espace à l'extérieur." }
    ]
  },
      'html_basics.mp3': {
        title: "Formatage du Texte en HTML",
        description: "Apprenez à formater le texte avec les balises HTML"
      },
      'html_liens.mp3': {
        title: "Les Liens Hypertextes en HTML",
        description: "Maîtrisez la création de liens hypertextes"
      },
      'html_img.mp3': {
        title: "Images en HTML",
        description: "Apprenez à intégrer et optimiser des images en HTML",
        chapters: [
          { time: 0, timeStr: "00:00", title: "Introduction aux images HTML" },
          { time: 120, timeStr: "02:00", title: "La balise img et ses attributs (src, alt)" },
          { time: 240, timeStr: "04:00", title: "Dimensionnement des images" },
          { time: 360, timeStr: "06:00", title: "Images cliquables et liens" },
          { time: 480, timeStr: "08:00", title: "Formats d'images (JPEG, PNG, GIF, WebP, SVG)" },
          { time: 600, timeStr: "10:00", title: "Optimisation et bonnes pratiques" }
        ],
        transcript: [
          { time: 0, timeStr: "00:00", text: "Bienvenue dans ce cours sur les images en HTML. Les images sont essentielles pour enrichir le contenu visuel d'une page web." },
          { time: 120, timeStr: "02:00", text: "La balise <img> est utilisée pour insérer des images. Les attributs src (source) et alt (texte alternatif) sont obligatoires." },
          { time: 240, timeStr: "04:00", text: "Spécifiez toujours les dimensions de vos images pour éviter les sauts de page pendant le chargement." },
          { time: 360, timeStr: "06:00", text: "Pour rendre une image cliquable, entourez-la d'une balise <a> avec l'attribut href." },
          { time: 480, timeStr: "08:00", text: "JPEG pour les photos, PNG pour la transparence, GIF pour les animations, WebP pour la meilleure compression." },
          { time: 600, timeStr: "10:00", text: "Optimisez vos images en les compressant et en utilisant des formats adaptés pour un chargement rapide." }
        ]
      },
      'html_formulaires.mp3': {  
    title: "Formulaires HTML Avancés",
    description: "Maîtrisez la création de formulaires HTML complexes",
    chapters: [
      { time: 0, timeStr: "00:00", title: "Introduction aux formulaires HTML" },
      { time: 180, timeStr: "03:00", title: "Structure de base d'un formulaire" },
      { time: 360, timeStr: "06:00", title: "Types de champs HTML5" },
      { time: 540, timeStr: "09:00", title: "Validation des formulaires" },
      { time: 720, timeStr: "12:00", title: "Bonnes pratiques" }
    ],
    transcript: [
      { time: 0, timeStr: "00:00", text: "Bienvenue dans ce cours sur les formulaires HTML avancés." },
      { time: 180, timeStr: "03:00", text: "La balise <form> avec les attributs action et method." },
      { time: 360, timeStr: "06:00", text: "Les nouveaux types d'input HTML5: email, tel, number, date." },
      { time: 540, timeStr: "09:00", text: "La validation HTML5 avec les attributs required, pattern, min, max." },
      { time: 720, timeStr: "12:00", text: "Optimisez vos formulaires pour l'expérience utilisateur." }
    ]
  },
  'html_semantique.mp3': {
    title: "HTML5 Sémantique - Structures Modernes",
    description: "Découvrez les balises sémantiques HTML5 (header, nav, main, article, section, aside, footer) pour une meilleure accessibilité et un meilleur référencement SEO.",
    chapters: [
      { time: 0, timeStr: "00:00", title: "Qu'est-ce que le HTML Sémantique ?" },
      { time: 90, timeStr: "01:30", title: "Pourquoi la sémantique est importante (SEO, Accessibilité)" },
      { time: 180, timeStr: "03:00", title: "Les balises structurelles : header, nav, main" },
      { time: 270, timeStr: "04:30", title: "Les balises de contenu : article, section" },
      { time: 390, timeStr: "06:30", title: "Les balises complémentaires : aside, footer" },
      { time: 480, timeStr: "08:00", title: "Les balises pour le contenu multimédia : figure, figcaption" },
      { time: 570, timeStr: "09:30", title: "Le problème du 'Div Soup'" },
      { time: 660, timeStr: "11:00", title: "Bonnes pratiques et récapitulatif" }
    ],
    transcript: [
      { time: 0, timeStr: "00:00", text: "Bienvenue dans ce cours sur le HTML5 sémantique. Aujourd'hui, nous allons voir comment structurer une page web correctement." },
      { time: 90, timeStr: "01:30", text: "Le HTML sémantique est crucial pour l'accessibilité. Les lecteurs d'écran comme VoiceOver utilisent ces balises pour aider les utilisateurs malvoyants à naviguer." },
      { time: 180, timeStr: "03:00", text: "Commencez par identifier les grandes régions de votre page : l'en-tête avec <header>, la navigation avec <nav>, et le contenu principal avec <main>." },
      { time: 270, timeStr: "04:30", text: "Utilisez <article> pour du contenu autonome qui pourrait être distribué, comme un article de blog. Utilisez <section> pour découper votre contenu principal en thèmes." },
      { time: 390, timeStr: "06:30", text: "<aside> est parfait pour une barre latérale contenant des publicités ou des liens. <footer> conclut la page avec le copyright et les liens de contact." },
      { time: 480, timeStr: "08:00", text: "N'oubliez pas d'utiliser une balise <figure> pour une image ou un schéma important, et <figcaption> pour lui ajouter une légende." },
      { time: 570, timeStr: "09:30", text: "Évitez ce qu'on appelle le 'div soup', un code rempli de divs innombrables. C'est mauvais pour l'accessibilité, le SEO et la lisibilité." },
      { time: 660, timeStr: "11:00", text: "En résumé, privilégiez toujours la balise sémantique adaptée à votre contenu. C'est une bonne pratique qui rendra vos sites web meilleurs." }
    ]
  },
  'html_mise_en_page_flexBox_grid.mp3': {
    title: "CSS - Mise en Page Avancée (Flexbox & Grid)",
    description: "Apprenez à utiliser Flexbox et Grid pour créer des mises en page modernes, responsives et professionnelles.",
    chapters: [
      { time: 0, timeStr: "00:00", title: "Introduction - Flexbox vs Grid" },
      { time: 60, timeStr: "01:00", title: "Flexbox: Layout 1D" },
      { time: 120, timeStr: "02:00", title: "Propriétés Flexbox principales" },
      { time: 180, timeStr: "03:00", title: "CSS Grid: Layout 2D" },
      { time: 240, timeStr: "04:00", title: "Propriétés Grid essentielles" },
      { time: 300, timeStr: "05:00", title: "Différence Flexbox vs Grid" },
      { time: 360, timeStr: "06:00", title: "Combiner Flexbox et Grid" },
      { time: 420, timeStr: "07:00", title: "Exercice pratique" }
    ],
    transcript: [
      { time: 0, timeStr: "00:00", text: "Bienvenue dans ce cours sur les mises en page CSS avancées. Aujourd'hui, nous allons explorer Flexbox et CSS Grid." },
      { time: 60, timeStr: "01:00", text: "Flexbox est un système de layout unidimensionnel (1D). Il permet de distribuer l'espace dans un conteneur et d'aligner les éléments sur une seule dimension (ligne ou colonne)." },
      { time: 120, timeStr: "02:00", text: "Les propriétés Flexbox principales sont: display: flex, flex-direction, justify-content pour l'alignement horizontal, align-items pour l'alignement vertical, et flex-wrap pour le passage à la ligne." },
      { time: 180, timeStr: "03:00", text: "CSS Grid est un système bidimensionnel (2D) qui permet de gérer à la fois les lignes et les colonnes." },
      { time: 240, timeStr: "04:00", text: "Les propriétés Grid essentielles: display: grid, grid-template-columns pour définir les colonnes, grid-template-rows pour les lignes, et gap pour l'espacement." },
      { time: 300, timeStr: "05:00", text: "La principale différence: Flexbox est conçu pour les layouts 1D (une seule direction), tandis que Grid est pour les layouts 2D (lignes ET colonnes)." },
      { time: 360, timeStr: "06:00", text: "Pour des projets modernes, combinez Flexbox pour les composants et Grid pour la structure globale de la page." },
      { time: 420, timeStr: "07:00", text: "Exercice pratique: Créez un layout avec header en Flexbox et le contenu principal en Grid." }
    ]
  },
  'html_tableau.mp3': {
    title: "Les Tableaux en HTML",
    description: "Apprenez à créer et formater des tableaux HTML pour organiser vos données structurées",
    chapters: [
      { time: 0, timeStr: "00:00", title: "Introduction aux tableaux HTML" },
      { time: 30, timeStr: "00:30", title: "Objectif : Organiser des données structurées" },
      { time: 60, timeStr: "01:00", title: "Les balises de base : table, tr, td" },
      { time: 90, timeStr: "01:30", title: "Les en-têtes de colonnes avec <th>" },
      { time: 120, timeStr: "02:00", title: "Structure complète d'un tableau" },
      { time: 149, timeStr: "02:29", title: "Récapitulatif et bonnes pratiques" }
    ],
    transcript: [
      { time: 0, timeStr: "00:00", text: "Bienvenue dans ce cours sur les tableaux en HTML. Dans ce tutoriel, vous allez apprendre à organiser et afficher des informations structurées sur vos pages web." },
      { time: 30, timeStr: "00:30", text: "Les tableaux sont utilisés pour organiser et afficher des informations structurées sur les pages web, comme des données organisées en lignes et colonnes." },
      { time: 60, timeStr: "01:00", text: "Le tableau se construit avec plusieurs balises : <table> pour créer le tableau, <tr> pour définir une ligne, et <td> pour une cellule de données." },
      { time: 90, timeStr: "01:30", text: "Pour les en-têtes, utilisez la balise <th> (table header) qui sera généralement affichée en gras et centrée. Elle remplace <td> dans les lignes d'en-tête." },
      { time: 120, timeStr: "02:00", text: "Ce tutoriel est conçu pour les débutants en HTML, montrant étape par étape comment créer un tableau simple et expliquant le fonctionnement de chaque balise." },
      { time: 149, timeStr: "02:29", text: "Ce tutoriel fait partie d'une série plus large visant à enseigner les fondamentaux du HTML pour les débutants. En résumé, c'est un tutoriel concis qui vous guide à travers les essentiels de la création et du formatage des tableaux en HTML." }
    ]
  },
  'html_head.mp3': {
    title: "HTML Head - Métadonnées et SEO",
    description: "Découvrez la balise <head> et son importance pour le SEO, l'accessibilité et les métadonnées",
    chapters: [
      { time: 0, timeStr: "00:00", title: "Introduction - Qu'est-ce que la balise <head> ?" },
      { time: 15, timeStr: "00:15", title: "Objectif : Contenir les métadonnées" },
      { time: 30, timeStr: "00:30", title: "Les éléments essentiels : title, meta, link" },
      { time: 45, timeStr: "00:45", title: "Pourquoi le <head> est crucial pour le SEO" },
      { time: 60, timeStr: "01:00", title: "Bonnes pratiques et démonstration pratique" },
      { time: 75, timeStr: "01:15", title: "Récapitulatif" }
    ],
    transcript: [
      { time: 0, timeStr: "00:00", text: "Bienvenue dans ce cours sur la balise <head> en HTML. Aujourd'hui, nous allons explorer cette section essentielle d'une page web qui contient des métadonnées, c'est-à-dire des informations sur la page qui ne sont pas visibles directement par l'utilisateur." },
      { time: 15, timeStr: "00:15", text: "Le <head> contient des métadonnées sur la page web, pas de contenu visible. Il inclut des éléments comme <title> pour le titre d'onglet, <meta> pour les descriptions et l'encodage des caractères, ainsi que des liens vers des ressources externes comme les feuilles de style CSS." },
      { time: 30, timeStr: "00:30", text: "Les éléments essentiels du <head> incluent la balise <title>, les balises <meta> pour la description et les mots-clés, les balises <link> pour les feuilles de style et les favicons, et les balises <script> pour le JavaScript." },
      { time: 45, timeStr: "00:45", text: "L'utilisation correcte du <head> améliore le référencement SEO, l'accessibilité et la fonctionnalité globale d'une page web. Les moteurs de recherche utilisent ces métadonnées pour comprendre et indexer votre contenu." },
      { time: 60, timeStr: "01:00", text: "Ce tutoriel montre des exemples pratiques de comment structurer un document HTML basique avec une section <head> bien formatée. Nous voyons comment ajouter le jeu de caractères UTF-8, la balise viewport pour le responsive, et les métadonnées pour les réseaux sociaux." },
      { time: 75, timeStr: "01:15", text: "En résumé, cette vidéo enseigne aux débutants comment configurer correctement les métadonnées et les ressources d'une page HTML en utilisant l'élément <head>. C'est un tutoriel concis mais complet sur les essentiels de la balise <head>." }
    ]
  },
  'html_multimedia.mp3': {
    title: "HTML Multimédia : Vidéo, Audio et Plug-ins",
    description: "Apprenez à intégrer et utiliser du contenu multimédia dans vos pages web avec les balises HTML5 <video> et <audio>",
    chapters: [
      { time: 0, timeStr: "00:00", title: "Introduction au multimédia" },
      { time: 44, timeStr: "00:44", title: "Définition du multimédia (texte, audio, vidéo, animation)" },
      { time: 112, timeStr: "01:52", title: "Formats de fichiers supportés (MP3, MP4)" },
      { time: 373, timeStr: "06:13", title: "Utilisation de la balise <video>" },
      { time: 413, timeStr: "06:53", title: "Utilisation de la balise <audio>" },
      { time: 535, timeStr: "08:55", title: "Plug-ins et méthodes héritées (<object>, <embed>)" },
      { time: 654, timeStr: "10:54", title: "Conclusion et bonnes pratiques" }
    ],
    transcript: [
      { time: 0, timeStr: "00:00", text: "Bienvenue dans ce cours sur le multimédia en HTML. Aujourd'hui, nous allons apprendre à intégrer et utiliser du contenu multimédia dans vos pages web." },
      { time: 44, timeStr: "00:44", text: "Le multimédia combine texte, audio, vidéo et animation. Les navigateurs offrent une interactivité native avec ces éléments grâce aux balises HTML5." },
      { time: 112, timeStr: "01:52", text: "Les formats de fichiers supportés incluent MP3 pour l'audio et MP4 pour la vidéo. Ces formats sont largement utilisés à travers toutes les plateformes web." },
      { time: 373, timeStr: "06:13", text: "La balise <video> permet d'embedder des vidéos avec des attributs comme src, width, height. L'attribut controls ajoute les contrôles de lecture (play, pause, volume)." },
      { time: 413, timeStr: "06:53", text: "La balise <audio> fonctionne de manière similaire pour les fichiers audio. L'attribut controls ajoute les boutons play, pause et le contrôle du volume." },
      { time: 535, timeStr: "08:55", text: "Avant HTML5, on utilisait les balises <object> et <embed> pour intégrer du contenu externe via des plug-ins. Ces méthodes sont moins courantes aujourd'hui grâce au support natif d'HTML5." },
      { time: 654, timeStr: "10:54", text: "En conclusion, pratiquez l'utilisation des balises multimédia pour rendre vos pages plus engageantes. N'oubliez pas d'ajouter l'attribut controls pour que les utilisateurs puissent contrôler la lecture." }
    ]
  },
  'html_responsive_media.mp3': {
    title: "CSS Media Queries - Fondamentaux du Responsive Design",
    description: "Apprenez à utiliser les CSS Media Queries pour créer des sites web responsives qui s'adaptent à tous les appareils",
    chapters: [
      { time: 0, timeStr: "00:00", title: "Introduction aux Media Queries" },
      { time: 16, timeStr: "00:16", title: "Syntaxe de base des Media Queries" },
      { time: 76, timeStr: "01:16", title: "Types d'appareils (screen, print, speech)" },
      { time: 145, timeStr: "02:25", title: "Exemple pratique avec max-width" },
      { time: 200, timeStr: "03:20", title: "Styles spécifiques à l'impression" },
      { time: 272, timeStr: "04:32", title: "L'ordre des règles CSS et la spécificité" },
      { time: 274, timeStr: "04:34", title: "Requêtes d'orientation (landscape/portrait)" },
      { time: 325, timeStr: "05:25", title: "Combinaison de conditions (ET et OU)" },
      { time: 391, timeStr: "06:31", title: "Les sélecteurs les plus utiles (max/min-width, orientation)" },
      { time: 417, timeStr: "06:57", title: "Conclusion - Fondation du responsive design" }
    ],
    transcript: [
      { time: 0, timeStr: "00:00", text: "Les CSS media queries sont essentielles pour la création de sites web responsives. Elles permettent d'adapter les styles CSS en fonction des caractéristiques de l'appareil : taille d'écran, orientation, type d'affichage." },
      { time: 16, timeStr: "00:16", text: "La syntaxe de base utilise @media suivie d'une condition et des styles entre accolades. Par exemple : @media (max-width: 500px) { body { color: blue; } }" },
      { time: 76, timeStr: "01:16", text: "Les différents types d'appareils incluent screen pour les écrans, print pour l'impression papier, speech pour les lecteurs d'écran, et all pour tous les appareils." },
      { time: 145, timeStr: "02:25", text: "Dans cet exemple pratique, la couleur du texte change. Par défaut elle est rouge. Mais lorsque la largeur d'écran est inférieure à 500 pixels, elle devient bleue." },
      { time: 200, timeStr: "03:20", text: "Les styles spécifiques à l'impression permettent de masquer les éléments non pertinents comme les menus de navigation, ou d'ajuster les couleurs pour économiser l'encre." },
      { time: 272, timeStr: "04:32", text: "L'ordre des règles CSS est très important. Les règles qui apparaissent plus tard dans la feuille de style l'emportent sur les précédentes, même à l'intérieur des media queries." },
      { time: 274, timeStr: "04:34", text: "Les requêtes d'orientation permettent de détecter si l'appareil est en mode paysage ou portrait, et d'appliquer des styles adaptés à chaque orientation." },
      { time: 325, timeStr: "05:25", text: "Pour combiner plusieurs conditions, utilisez 'and' pour un ET logique, et la virgule pour un OU logique. Par exemple : @media (orientation: landscape) and (max-width: 600px)" },
      { time: 391, timeStr: "06:31", text: "Les sélecteurs les plus utiles sont max-width pour cibler les petits écrans, min-width pour les grands écrans, orientation pour la rotation de l'appareil, et print pour l'impression." },
      { time: 417, timeStr: "06:57", text: "En conclusion, les media queries sont la fondation du responsive design. Maîtrisez-les pour créer des sites web qui s'adaptent parfaitement à tous les appareils : mobiles, tablettes et ordinateurs." }
    ]
  },
  'html_css_selectors.mp3': {
    title: "CSS - Les Sélecteurs Simples (Element, ID, Class)",
    description: "Apprenez les trois sélecteurs CSS les plus courants pour styliser vos pages web",
    chapters: [
      { time: 0, timeStr: "00:00", title: "Introduction aux sélecteurs CSS" },
      { time: 20, timeStr: "00:20", title: "Les sélecteurs d'élément (type selectors)" },
      { time: 40, timeStr: "00:40", title: "Les sélecteurs d'ID (#id)" },
      { time: 60, timeStr: "01:00", title: "Les sélecteurs de classe (.class)" },
      { time: 80, timeStr: "01:20", title: "Comparaison et bonnes pratiques" },
      { time: 100, timeStr: "01:40", title: "Exemples pratiques en code" },
      { time: 120, timeStr: "02:00", title: "Conclusion - Les blocs de construction du CSS" }
    ],
    transcript: [
      { time: 0, timeStr: "00:00", text: "Bienvenue dans ce cours sur les sélecteurs CSS simples. Les sélecteurs CSS sont la base du stylage web. Ils permettent de cibler précisément les éléments HTML à styliser." },
      { time: 20, timeStr: "00:20", text: "Le sélecteur d'élément cible toutes les occurrences d'une balise HTML spécifique. Par exemple, le sélecteur 'p' appliquera les styles à tous les paragraphes de la page. Exemple : p { color: red; }" },
      { time: 40, timeStr: "00:40", text: "Le sélecteur d'ID cible un élément unique dans la page, en utilisant la syntaxe #suivi du nom de l'ID. Chaque ID doit être unique. Exemple : #header { font-size: 20px; }" },
      { time: 60, timeStr: "01:00", text: "Le sélecteur de classe cible plusieurs éléments qui partagent le même nom de classe, avec la syntaxe .suivi du nom de la classe. Exemple : .highlight { background: yellow; }" },
      { time: 80, timeStr: "01:20", text: "La principale différence : un ID est unique sur la page, une classe peut être réutilisée plusieurs fois. Les classes sont plus flexibles et recommandées pour le styling, les IDs sont idéals pour les éléments uniques et le JavaScript." },
      { time: 100, timeStr: "01:40", text: "Dans la pratique, on utilise souvent les classes par défaut car elles sont réutilisables. Un élément peut même avoir plusieurs classes, séparées par des espaces, comme class='btn btn-primary large'." },
      { time: 120, timeStr: "02:00", text: "En conclusion, maîtriser les sélecteurs d'élément, d'ID et de classe est essentiel pour écrire du CSS efficace. Ce sont les blocs de construction du styling web. Entraînez-vous avec ces trois types de sélecteurs pour bien comprendre quand utiliser chacun." }
    ]
  },
  'html_css_colors.mp3': {
    title: "CSS Couleurs - Noms, HEX, RGB, HSL",
    description: "Apprenez à utiliser les couleurs en CSS pour donner vie à vos pages web",
    chapters: [
      { time: 0, timeStr: "00:00", title: "Introduction aux couleurs en CSS" },
      { time: 20, timeStr: "00:20", title: "Les noms de couleurs" },
      { time: 40, timeStr: "00:40", title: "Les codes HEX (hexadécimaux)" },
      { time: 60, timeStr: "01:00", title: "Les valeurs RGB" },
      { time: 80, timeStr: "01:20", title: "RGBA - Ajouter l'opacité" },
      { time: 100, timeStr: "01:40", title: "Les valeurs HSL (Hue, Saturation, Lightness)" },
      { time: 120, timeStr: "02:00", title: "HSLA - Opacité avec HSL" },
      { time: 140, timeStr: "02:20", title: "Comparaison des formats" },
      { time: 160, timeStr: "02:40", title: "Bonnes pratiques et accessibilité" }
    ],
    transcript: [
      { time: 0, timeStr: "00:00", text: "Bienvenue dans ce cours sur les couleurs en CSS. Les couleurs sont essentielles pour donner vie à vos pages web. CSS offre plusieurs façons de définir et manipuler les couleurs." },
      { time: 20, timeStr: "00:20", text: "Les noms de couleurs sont le format le plus simple. CSS supporte 140 noms de couleurs standards comme red, blue, green, yellow, orange, purple, etc. C'est parfait pour les couleurs de base." },
      { time: 40, timeStr: "00:40", text: "Les codes HEX utilisent 6 caractères hexadécimaux précédés d'un #. Par exemple, #FF0000 pour le rouge, #00FF00 pour le vert, #0000FF pour le bleu. C'est le format le plus utilisé en web design." },
      { time: 60, timeStr: "01:00", text: "RGB définit une couleur par un mélange de rouge, vert et bleu. Chaque valeur est comprise entre 0 et 255. Exemple : rgb(255, 0, 0) donne du rouge pur, rgb(0, 255, 0) du vert." },
      { time: 80, timeStr: "01:20", text: "RGBA ajoute un quatrième paramètre pour l'opacité. La valeur alpha va de 0 (complètement transparent) à 1 (complètement opaque). Exemple : rgba(255, 0, 0, 0.5) donne du rouge semi-transparent." },
      { time: 100, timeStr: "01:40", text: "HSL est un format plus intuitif. H pour Hue (teinte) de 0 à 360°, S pour Saturation (0-100%), L pour Lightness (luminosité 0-100%). Par exemple, hsl(0, 100%, 50%) donne du rouge." },
      { time: 120, timeStr: "02:00", text: "HSLA fonctionne comme HSL mais avec un canal alpha pour l'opacité. Exemple : hsla(240, 100%, 50%, 0.5) donne du bleu semi-transparent. C'est très utile pour les overlays." },
      { time: 140, timeStr: "02:20", text: "Quel format choisir ? Les noms sont simples mais limités. HEX et RGB sont précis et universels. HSL est excellent pour créer des variations de couleurs en ajustant la luminosité ou la saturation." },
      { time: 160, timeStr: "02:40", text: "Bonnes pratiques : utilisez des variables CSS pour les couleurs réutilisables, assurez un bon contraste entre texte et arrière-plan pour l'accessibilité, et testez vos couleurs sur différents écrans." }
    ]
  },
  'html_css_background.mp3': {
    title: "CSS Background Images - Images d'Arrière-plan",
    description: "Apprenez à utiliser les images d'arrière-plan en CSS pour enrichir vos pages web",
    chapters: [
      { time: 0, timeStr: "00:00", title: "Introduction aux images d'arrière-plan" },
      { time: 10, timeStr: "00:10", title: "La propriété background-image" },
      { time: 20, timeStr: "00:20", title: "Contrôle de la répétition (background-repeat)" },
      { time: 35, timeStr: "00:35", title: "Positionnement (background-position)" },
      { time: 50, timeStr: "00:50", title: "Dimensionnement (background-size: cover/contain)" },
      { time: 65, timeStr: "01:05", title: "Combinaison avec couleurs et fallback" },
      { time: 80, timeStr: "01:20", title: "Bonnes pratiques et exercice" }
    ],
    transcript: [
      { time: 0, timeStr: "00:00", text: "Bienvenue dans ce cours sur les images d'arrière-plan en CSS. Les images d'arrière-plan permettent d'ajouter des visuels attrayants derrière le contenu de vos pages web." },
      { time: 10, timeStr: "00:10", text: "La propriété background-image permet de définir une image comme arrière-plan. Par exemple : background-image: url('image.jpg'); pour mettre une image derrière un élément." },
      { time: 20, timeStr: "00:20", text: "Par défaut, l'image se répète en mosaïque. background-repeat: no-repeat empêche la répétition. repeat-x répète horizontalement, repeat-y verticalement." },
      { time: 35, timeStr: "00:35", text: "background-position contrôle l'emplacement. Utilisez center, top, bottom, left, right, ou des pourcentages. background-position: center centre l'image parfaitement." },
      { time: 50, timeStr: "00:50", text: "background-size: cover redimensionne l'image pour couvrir tout l'élément, même si elle est rognée. contain montre l'image entière, mais peut laisser des espaces vides." },
      { time: 65, timeStr: "01:05", text: "Toujours définir une couleur d'arrière-plan de secours. Par exemple background-color: #333; Elle s'affiche pendant le chargement ou si l'image ne peut pas être chargée." },
      { time: 80, timeStr: "01:20", text: "Bonnes pratiques : optimisez vos images, utilisez cover pour les héros, testez sur mobile, et assurez un bon contraste entre l'arrière-plan et le texte pour l'accessibilité." }
    ]
  },
  'html_css_border.mp3': {
    title: "CSS Borders - Bordures en CSS",
    description: "Apprenez à styliser, dimensionner et colorer les bordures autour des éléments HTML",
    chapters: [
      { time: 0, timeStr: "00:00", title: "Introduction aux bordures CSS" },
      { time: 20, timeStr: "00:20", title: "Les styles de bordures (border-style)" },
      { time: 37, timeStr: "00:37", title: "Les styles de base : none, dotted, dashed, solid, double" },
      { time: 60, timeStr: "01:00", title: "Les styles 3D : groove, ridge, inset, outset" },
      { time: 94, timeStr: "01:34", title: "Les effets 3D en détail" },
      { time: 150, timeStr: "02:30", title: "La largeur des bordures (border-width)" },
      { time: 180, timeStr: "03:00", title: "La couleur des bordures (border-color)" },
      { time: 257, timeStr: "04:17", title: "Bordures différentes par côté" },
      { time: 426, timeStr: "07:06", title: "La propriété raccourcie (border)" },
      { time: 460, timeStr: "07:40", title: "Bordures côté-spécifiques raccourcies" },
      { time: 512, timeStr: "08:32", title: "Conclusion et bonnes pratiques" }
    ],
    transcript: [
      { time: 0, timeStr: "00:00", text: "Bienvenue dans ce cours sur les bordures CSS. Les bordures permettent d'ajouter des contours stylisés autour des éléments HTML. Elles peuvent être personnalisées en termes de style, d'épaisseur et de couleur." },
      { time: 20, timeStr: "00:20", text: "La propriété border-style est fondamentale. Sans style défini, les bordures ne s'affichent pas, même si vous définissez une largeur ou une couleur. C'est la propriété la plus importante." },
      { time: 37, timeStr: "00:37", text: "Les styles de base incluent : none pour pas de bordure, dotted pour des pointillés, dashed pour des tirets, solid pour une ligne pleine, et double pour deux lignes parallèles. Le style double divise l'épaisseur uniformément." },
      { time: 60, timeStr: "01:00", text: "Pour des effets 3D, nous avons groove qui donne un effet creusé, ridge pour un effet en relief, inset pour un effet encastré, et outset pour un effet saillant." },
      { time: 94, timeStr: "01:34", text: "Les effets 3D comme groove et ridge dépendent de la largeur et de la couleur de la bordure. Plus l'épaisseur est grande, plus l'effet 3D est prononcé." },
      { time: 150, timeStr: "02:30", text: "La largeur des bordures se contrôle avec border-width. On peut utiliser des valeurs prédéfinies : thin pour fine, medium pour moyenne, thick pour épaisse, ou des valeurs personnalisées en pixels." },
      { time: 180, timeStr: "03:00", text: "Les couleurs peuvent être définies avec des noms comme red, des codes HEX comme #FF0000, des valeurs RGB comme rgb(255,0,0), ou transparent. Par défaut, la bordure hérite de la couleur du texte." },
      { time: 257, timeStr: "04:17", text: "CSS permet d'appliquer des bordures différentes sur chaque côté. On peut utiliser des propriétés individuelles comme border-top-style, border-right-style, border-bottom-style, border-left-style, ou des valeurs multiples." },
      { time: 426, timeStr: "07:06", text: "La propriété raccourcie border combine style, largeur et couleur en une seule déclaration. Exemple : border: 2px solid red. L'ordre des valeurs n'a pas d'importance." },
      { time: 460, timeStr: "07:40", text: "Pour des bordures côté-spécifiques, on utilise border-top, border-right, border-bottom, border-left. Cela permet de créer des accents visuels subtils, comme une ligne de sélection ou une alerte." },
      { time: 512, timeStr: "08:32", text: "En conclusion, maîtrisez les bordures pour enrichir vos designs. Consultez la référence W3Schools pour plus d'exemples. Entraînez-vous avec différents styles, largeurs et couleurs." }
    ]
  }
    };

    const fileContent = fileContentMap[audioFileName] || {};
    const courseContent = contentMap[course.id] || {};

    return {
      title: fileContent.title || courseContent.title || course.titre,
      description: fileContent.description || courseContent.description || course.description || "Apprenez les bases du HTML",
      audioFile: audioFileName,
      chapters: fileContent.chapters || courseContent.chapters || [],
      transcript: fileContent.transcript || courseContent.transcript || []
    };
  }, []);

  
  const loadAudioFiles = async () => {
    try {
      setLoadingAudio(true);
      const response = await api.get('/static/list');
      const audioFilesList = response.data.files.filter(
        (file: any) => file.type === 'audio' && file.name.endsWith('.mp3')
      );
      setAudioFiles(audioFilesList);
      
      
      if (audioFilesList.length > 0 && !currentAudioFile) {
        setCurrentAudioFile(audioFilesList[0].name);
      }
    } catch (error) {
      console.error('Erreur chargement fichiers audio:', error);
      
      const defaultAudioFiles = [
        { name: 'html_basics.mp3', path: 'html_basics.mp3', size: 0, url: `${AUDIO_BASE_URL}/html_basics.mp3` },
        { name: 'html_liens.mp3', path: 'html_liens.mp3', size: 0, url: `${AUDIO_BASE_URL}/html_liens.mp3` },
        { name: 'html_img.mp3', path: 'html_img.mp3', size: 0, url: `${AUDIO_BASE_URL}/html_img.mp3` },
        { name: 'html_formulaires.mp3', path: 'audio/html_formulaires.mp3', size: 0, url: `${AUDIO_BASE_URL}/html_formulaires.mp3`, type: 'audio' },
        { name: 'html_semantique.mp3', path: 'audio/html_semantique.mp3', size: 0, url: `${AUDIO_BASE_URL}/html_semantique.mp3`, type: 'audio' },
        { name: 'html_mise_en_page_flexBox_grid.mp3', path: 'audio/html_mise_en_page_flexBox_grid.mp3', size: 0, url: `${AUDIO_BASE_URL}/html_mise_en_page_flexBox_grid.mp3`, type: 'audio' },
        { name: 'html_tableau.mp3', path: 'audio/html_tableau.mp3', size: 0, url: `${AUDIO_BASE_URL}/html_tableau.mp3`, type: 'audio' },
        { name: 'html_head.mp3', path: 'audio/html_head.mp3', size: 0, url: `${AUDIO_BASE_URL}/html_head.mp3`, type: 'audio' },
        { name: 'html_multimedia.mp3', path: 'audio/html_multimedia.mp3', size: 0, url: `${AUDIO_BASE_URL}/html_multimedia.mp3`, type: 'audio' },
        { name: 'html_responsive_media.mp3', path: 'audio/html_responsive_media.mp3', size: 0, url: `${AUDIO_BASE_URL}/html_responsive_media.mp3`, type: 'audio' },
        { name: 'html_css_selectors.mp3', path: 'audio/html_css_selectors.mp3', size: 0, url: `${AUDIO_BASE_URL}/html_css_selectors.mp3`, type: 'audio' },
        { name: 'html_css_colors.mp3', path: 'audio/html_css_colors.mp3', size: 0, url: `${AUDIO_BASE_URL}/html_css_colors.mp3`, type: 'audio' },
        { name: 'html_css_background.mp3', path: 'audio/html_css_background.mp3', size: 0, url: `${AUDIO_BASE_URL}/html_css_background.mp3`, type: 'audio' },
        { name: 'html_css_border.mp3', path: 'audio/html_css_border.mp3', size: 0, url: `${AUDIO_BASE_URL}/html_css_border.mp3`, type: 'audio' },
        { name: 'html_css_margin.mp3', path: 'audio/html_css_margin.mp3', size: 0, url: `${AUDIO_BASE_URL}/html_css_margin.mp3`, type: 'audio' },
        { name: 'html_css_padding.mp3', path: 'audio/html_css_padding.mp3', size: 0, url: `${AUDIO_BASE_URL}/html_css_padding.mp3`, type: 'audio' },
        { name: 'html_css_text.mp3', path: 'audio/html_css_text.mp3', size: 0, url: `${AUDIO_BASE_URL}/html_css_text.mp3`, type: 'audio' },
        { name: 'html_css_fonts.mp3', path: 'audio/html_css_fonts.mp3', size: 0, url: `${AUDIO_BASE_URL}/html_css_fonts.mp3`, type: 'audio' },
        {name:'html_css_links.mp3',path:'audio/html_css_links.mp3',size:0,url:`${AUDIO_BASE_URL}/html_css_links.mp3`,type:'audio'},
        { name: 'html_css_lists.mp3', path: 'audio/html_css_lists.mp3', size: 0, url: `${AUDIO_BASE_URL}/html_css_lists.mp3`, type: 'audio' },
        { name: 'html_css_tables.mp3', path: 'audio/html_css_tables.mp3', size: 0, url: `${AUDIO_BASE_URL}/html_css_tables.mp3`, type: 'audio' },
        { name: 'html_css_display_visibility.mp3', path: 'audio/html_css_display_visibility.mp3', size: 0, url: `${AUDIO_BASE_URL}/html_css_display_visibility.mp3`, type: 'audio' },
        { name: 'html_css_positioning.mp3', path: 'audio/html_css_positioning.mp3', size: 0, url: `${AUDIO_BASE_URL}/html_css_positioning.mp3`, type: 'audio' },
        { name: 'html_css_overflow.mp3', path: 'audio/html_css_overflow.mp3', size: 0, url: `${AUDIO_BASE_URL}/html_css_overflow.mp3`, type: 'audio' },
        { name: 'html_css_float.mp3', path: 'audio/html_css_float.mp3', size: 0, url: `${AUDIO_BASE_URL}/html_css_float.mp3`, type: 'audio' },
        { name: 'html_js_introduction.mp3', path: 'audio/html_js_introduction.mp3', size: 0, url: `${AUDIO_BASE_URL}/html_js_introduction.mp3`, type: 'audio' },
        { name: 'html_js_variables.mp3', path: 'audio/html_js_variables.mp3', size: 0, url: `${AUDIO_BASE_URL}/html_js_variables.mp3`, type: 'audio' },
        { name: 'html_js_datatypes.mp3', path: 'audio/html_js_datatypes.mp3', size: 0, url: `${AUDIO_BASE_URL}/html_js_datatypes.mp3`, type: 'audio' },
        { name: 'html_js_operators.mp3', path: 'audio/html_js_operators.mp3', size: 0, url: `${AUDIO_BASE_URL}/html_js_operators.mp3`, type: 'audio' },
        { name: 'html_js_if_conditions.mp3', path: 'audio/html_js_if_conditions.mp3', size: 0, url: `${AUDIO_BASE_URL}/html_js_if_conditions.mp3`, type: 'audio' },
        { name: 'html_js_loops.mp3', path: 'audio/html_js_loops.mp3', size: 0, url: `${AUDIO_BASE_URL}/html_js_loops.mp3`, type: 'audio' },
        { name: 'html_js_strings_methods.mp3', path: 'audio/html_js_strings_methods.mp3', size: 0, url: `${AUDIO_BASE_URL}/html_js_strings_methods.mp3`, type: 'audio' },
        { name: 'html_js_numbers_methods.mp3', path: 'audio/html_js_numbers_methods.mp3', size: 0, url: `${AUDIO_BASE_URL}/html_js_numbers_methods.mp3`, type: 'audio' },
        { name: 'html_js_functions.mp3', path: 'audio/html_js_functions.mp3', size: 0, url: `${AUDIO_BASE_URL}/html_js_functions.mp3`, type: 'audio' },
        { name: 'html_js_objects.mp3', path: 'audio/html_js_objects.mp3', size: 0, url: `${AUDIO_BASE_URL}/html_js_objects.mp3`, type: 'audio' },
        { name: 'html_js_arrays.mp3', path: 'audio/html_js_arrays.mp3', size: 0, url: `${AUDIO_BASE_URL}/html_js_arrays.mp3`, type: 'audio' },
        { name: 'html_js_sets.mp3', path: 'audio/html_js_sets.mp3', size: 0, url: `${AUDIO_BASE_URL}/html_js_sets.mp3`, type: 'audio' },
        { name: 'html_js_maps.mp3', path: 'audio/html_js_maps.mp3', size: 0, url: `${AUDIO_BASE_URL}/html_js_maps.mp3`, type: 'audio' },
        { name: 'html_js_math_objects.mp3', path: 'audio/html_js_math_objects.mp3', size: 0, url: `${AUDIO_BASE_URL}/html_js_math_objects.mp3`, type: 'audio' },
        { name: 'html_js_regex.mp3', path: 'audio/html_js_regex.mp3', size: 0, url: `${AUDIO_BASE_URL}/html_js_regex.mp3`, type: 'audio' },
        { name: 'html_js_events.mp3', path: 'audio/html_js_events.mp3', size: 0, url: `${AUDIO_BASE_URL}/html_js_events.mp3`, type: 'audio' }

      ];
      setAudioFiles(defaultAudioFiles);
      if (!currentAudioFile) {
        setCurrentAudioFile('html_basics.mp3');
      }
    } finally {
      setLoadingAudio(false);
    }
  };

  
  const getDefaultQuestionsForCourse = useCallback((courseId: number): Question[] => {
    const questionsMap: Record<number, Question[]> = {
      48: [ 
    {
      id: 4801,
      question: "Quelle est la principale différence entre un event handler et un event listener ?",
      options: { 
        A: "Handler ne fonctionne que sur mobile", 
        B: "Handler permet plusieurs fonctions, Listener une seule", 
        C: "Handler permet une seule fonction par événement, Listener permet plusieurs", 
        D: "Ils sont identiques" 
      },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "Event handlers (comme onclick) ne permettent qu'une seule fonction par événement. Event listeners permettent d'attacher plusieurs fonctions."
    },
    {
      id: 4802,
      question: "Quelle méthode permet d'attacher un écouteur d'événement ?",
      options: { A: "attachEvent()", B: "addEvent()", C: "addEventListener()", D: "setListener()" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "addEventListener() est la méthode standard pour attacher des écouteurs d'événements."
    },
    {
      id: 4803,
      question: "Que se passe-t-on si on assigne deux fois onclick sur le même bouton ?",
      options: { 
        A: "Les deux s'exécutent", 
        B: "Le second remplace le premier", 
        C: "Une erreur se produit", 
        D: "Rien ne se passe" 
      },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "Le second gestionnaire remplace le premier car un seul handler par événement est autorisé."
    },
    {
      id: 4804,
      question: "Que se passe-t-on si on utilise deux fois addEventListener sur le même événement ?",
      options: { 
        A: "Le second remplace le premier", 
        B: "Les deux s'exécutent", 
        C: "Une erreur se produit", 
        D: "Seul le premier s'exécute" 
      },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "Les deux écouteurs s'exécutent car addEventListener permet d'attacher plusieurs fonctions."
    },
    {
      id: 4805,
      question: "Quelle méthode permet de supprimer un écouteur d'événement ?",
      options: { 
        A: "removeEvent()", 
        B: "detachListener()", 
        C: "removeEventListener()", 
        D: "deleteListener()" 
      },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "removeEventListener() supprime un écouteur d'événement précédemment ajouté."
    },
    {
      id: 4806,
      question: "Quelle est la syntaxe correcte pour ajouter un écouteur de clic ?",
      options: { 
        A: "button.onclick = function() {}", 
        B: "button.click(function() {})", 
        C: "button.addEventListener('click', function() {})", 
        D: "button.addEvent('click', function() {})" 
      },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "addEventListener('click', callback) est la syntaxe standard pour ajouter un écouteur de clic."
    },
    {
      id: 4807,
      question: "Quel événement correspond à un double clic ?",
      options: { A: "click", B: "doubleclick", C: "dblclick", D: "double-click" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "dblclick est l'événement pour le double clic."
    },
    {
      id: 4808,
      question: "Pourquoi recommande-t-on d'utiliser addEventListener plutôt que les handlers onclick ?",
      options: { 
        A: "C'est plus rapide", 
        B: "Cela permet d'attacher plusieurs fonctions", 
        C: "Cela fonctionne sur plus de navigateurs", 
        D: "Cela utilise moins de mémoire" 
      },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "addEventListener permet d'attacher plusieurs fonctions au même événement, contrairement à onclick."
    },
    {
      id: 4809,
      question: "Quel événement est déclenché quand la souris passe au-dessus d'un élément ?",
      options: { A: "mouseenter", B: "mouseover", C: "mouseup", D: "mousedown" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "mouseover est déclenché quand la souris passe au-dessus d'un élément."
    },
    {
      id: 4810,
      question: "Que doit-on passer à removeEventListener pour supprimer un écouteur ?",
      options: { 
        A: "Seulement le type d'événement", 
        B: "La fonction originale utilisée dans addEventListener", 
        C: "Le nom de l'élément", 
        D: "L'index de l'écouteur" 
      },
      reponse_correcte: "B",
      points: 15,
      difficulte: "moyen",
      explication: "removeEventListener nécessite la même fonction que celle ajoutée avec addEventListener."
    }
  ],
       47: [ 
    {
      id: 4701,
      question: "Que signifie l'abréviation RegEx ?",
      options: { A: "Regular Expression", B: "Regular Text", C: "Regex Expression", D: "Real Expression" },
      reponse_correcte: "A",
      points: 10,
      difficulte: "facile",
      explication: "RegEx signifie Regular Expression (expression régulière)."
    },
    {
      id: 4702,
      question: "Quel flag rend une recherche insensible à la casse ?",
      options: { A: "g", B: "i", C: "m", D: "c" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "Le flag 'i' rend la recherche insensible à la casse (case-insensitive)."
    },
    {
      id: 4703,
      question: "Quelle méthode RegEx vérifie si un motif existe dans une chaîne ?",
      options: { A: "match()", B: "test()", C: "search()", D: "exec()" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "test() vérifie si un motif existe et retourne true ou false."
    },
    {
      id: 4704,
      question: "Quelle méthode de chaîne remplace du texte avec une expression régulière ?",
      options: { A: "match()", B: "search()", C: "replace()", D: "split()" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "replace() remplace les correspondances d'une expression régulière."
    },
    {
      id: 4705,
      question: "Que signifie le flag 'g' dans une expression régulière ?",
      options: { A: "Global (trouve toutes les occurrences)", B: "Group", C: "Grand", D: "Greedy" },
      reponse_correcte: "A",
      points: 10,
      difficulte: "facile",
      explication: "Le flag 'g' signifie global et trouve toutes les occurrences, pas seulement la première."
    },
    {
      id: 4706,
      question: "Que représente \\d en regex ?",
      options: { A: "Une lettre", B: "Un chiffre", C: "Un espace", D: "Un caractère spécial" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "\\d représente n'importe quel chiffre (0-9)."
    },
    {
      id: 4707,
      question: "Quelle méthode retourne l'index de la première correspondance ?",
      options: { A: "match()", B: "test()", C: "search()", D: "exec()" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "search() retourne l'index de la première correspondance, ou -1 si non trouvée."
    },
    {
      id: 4708,
      question: "Que signifie le quantificateur '+' en regex ?",
      options: { A: "Zéro ou une fois", B: "Une ou plusieurs fois", C: "Zéro ou plusieurs fois", D: "Exactement une fois" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "+ signifie une ou plusieurs fois."
    },
    {
      id: 4709,
      question: "Comment écrire une expression régulière pour trouver toutes les occurrences du mot 'test' (insensible à la casse) ?",
      options: { A: "/test/g", B: "/test/i", C: "/test/gi", D: "/test/ig" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "g pour global, i pour insensible à la casse."
    },
    {
      id: 4710,
      question: "Que retourne la méthode match() ?",
      options: { A: "Un booléen", B: "Un index", C: "Un tableau des correspondances", D: "Une nouvelle chaîne" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "match() retourne un tableau contenant toutes les correspondances trouvées."
    }
  ],
      46: [ 
    {
      id: 4601,
      question: "Quelle méthode arrondit un nombre à l'entier le plus proche ?",
      options: { A: "Math.floor()", B: "Math.ceil()", C: "Math.round()", D: "Math.trunc()" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "Math.round() arrondit à l'entier le plus proche (vers le haut pour 0.5 et plus)."
    },
    {
      id: 4602,
      question: "Comment obtenir la valeur de Pi en JavaScript ?",
      options: { A: "Math.Pi", B: "Math.PI", C: "Math.pi", D: "Math.PI()" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "Math.PI (en majuscules) donne la constante mathématique π."
    },
    {
      id: 4603,
      question: "Quelle méthode supprime la partie décimale d'un nombre ?",
      options: { A: "Math.round()", B: "Math.floor()", C: "Math.ceil()", D: "Math.trunc()" },
      reponse_correcte: "D",
      points: 10,
      difficulte: "facile",
      explication: "Math.trunc() supprime la partie décimale, ne gardant que l'entier."
    },
    {
      id: 4604,
      question: "Comment générer un nombre aléatoire entre 0 et 1 ?",
      options: { A: "Math.random()", B: "Math.random(1)", C: "Math.rand()", D: "Math.randomBetween(0,1)" },
      reponse_correcte: "A",
      points: 10,
      difficulte: "facile",
      explication: "Math.random() retourne un nombre aléatoire entre 0 (inclus) et 1 (exclus)."
    },
    {
      id: 4605,
      question: "Que retourne Math.pow(2, 4) ?",
      options: { A: "6", B: "8", C: "12", D: "16" },
      reponse_correcte: "D",
      points: 10,
      difficulte: "facile",
      explication: "Math.pow(2, 4) calcule 2^4 = 16."
    },
    {
      id: 4606,
      question: "Que retourne Math.max(5, 10, 3, 8, 2) ?",
      options: { A: "2", B: "5", C: "8", D: "10" },
      reponse_correcte: "D",
      points: 10,
      difficulte: "facile",
      explication: "Math.max() retourne la plus grande valeur parmi les arguments, donc 10."
    },
    {
      id: 4607,
      question: "Que retourne Math.abs(-7) ?",
      options: { A: "0", B: "7", C: "-7", D: "undefined" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "Math.abs() retourne la valeur absolue, donc 7."
    },
    {
      id: 4608,
      question: "Que retourne Math.floor(4.9) ?",
      options: { A: "4", B: "5", C: "4.9", D: "0" },
      reponse_correcte: "A",
      points: 10,
      difficulte: "facile",
      explication: "Math.floor() arrondit toujours vers le bas, donc 4."
    },
    {
      id: 4609,
      question: "Que retourne Math.sqrt(16) ?",
      options: { A: "4", B: "8", C: "16", D: "256" },
      reponse_correcte: "A",
      points: 10,
      difficulte: "facile",
      explication: "Math.sqrt(16) calcule la racine carrée de 16, qui est 4."
    },
    {
      id: 4610,
      question: "Comment obtenir un nombre aléatoire entre 1 et 100 ?",
      options: { 
        A: "Math.random() * 100", 
        B: "Math.floor(Math.random() * 100)", 
        C: "Math.floor(Math.random() * 100) + 1", 
        D: "Math.random() * 100 + 1" 
      },
      reponse_correcte: "C",
      points: 15,
      difficulte: "moyen",
      explication: "Math.floor(Math.random() * 100) + 1 donne un entier entre 1 et 100."
    }
  ],
      45: [ 
    {
      id: 4501,
      question: "Qu'est-ce qu'une Map en JavaScript ?",
      options: { 
        A: "Un tableau", 
        B: "Une structure de données clé-valeur", 
        C: "Une fonction", 
        D: "Une variable" 
      },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "Map est une structure de données qui stocke des paires clé-valeur."
    },
    {
      id: 4502,
      question: "Quelle méthode ajoute une paire clé-valeur à une Map ?",
      options: { A: ".add()", B: ".push()", C: ".set()", D: ".insert()" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "La méthode .set(key, value) ajoute une paire clé-valeur à la Map."
    },
    {
      id: 4503,
      question: "Comment récupérer la valeur associée à une clé dans une Map ?",
      options: { A: ".fetch()", B: ".get()", C: ".retrieve()", D: ".value()" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "La méthode .get(key) retourne la valeur associée à la clé."
    },
    {
      id: 4504,
      question: "Quelle propriété donne le nombre d'entrées dans une Map ?",
      options: { A: "length", B: "count", C: "size", D: "entries" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "La propriété size retourne le nombre d'entrées dans la Map."
    },
    {
      id: 4505,
      question: "Quelle méthode vérifie si une clé existe dans une Map ?",
      options: { A: ".contains()", B: ".has()", C: ".exists()", D: ".includes()" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "La méthode .has(key) vérifie si une clé existe dans la Map."
    },
    {
      id: 4506,
      question: "Quel type de clés peut-on utiliser dans une Map ?",
      options: { 
        A: "Uniquement des chaînes", 
        B: "Uniquement des nombres", 
        C: "N'importe quel type", 
        D: "Uniquement des objets" 
      },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "Map permet d'utiliser n'importe quel type de données comme clé : string, number, object, etc."
    },
    {
      id: 4507,
      question: "Quelle est la différence entre Map et Object ?",
      options: { 
        A: "Map a une propriété size, Object non", 
        B: "Map est itérable, Object non", 
        C: "Map permet des clés de tout type", 
        D: "Toutes ces réponses" 
      },
      reponse_correcte: "D",
      points: 15,
      difficulte: "moyen",
      explication: "Map a une propriété size, est directement itérable, et permet des clés de tout type."
    },
    {
      id: 4508,
      question: "Comment supprimer une entrée spécifique d'une Map ?",
      options: { A: ".remove()", B: ".delete()", C: ".clear()", D: ".pop()" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "La méthode .delete(key) supprime une entrée spécifique de la Map."
    },
    {
      id: 4509,
      question: "Que retourne .get() si la clé n'existe pas ?",
      options: { A: "null", B: "undefined", C: "0", D: "false" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: ".get() retourne undefined si la clé n'existe pas dans la Map."
    },
    {
      id: 4510,
      question: "Quelle boucle peut-on utiliser pour parcourir une Map ?",
      options: { A: "for...in", B: "for...of", C: "forEach", D: "Les réponses B et C" },
      reponse_correcte: "D",
      points: 10,
      difficulte: "facile",
      explication: "On peut parcourir une Map avec for...of ou la méthode .forEach()."
    }
  ],
      44: [ 
    {
      id: 4401,
      question: "Quelle est la principale caractéristique d'un Set en JavaScript ?",
      options: { 
        A: "Stocke des valeurs ordonnées", 
        B: "Stocke uniquement des valeurs uniques", 
        C: "Stocke des paires clé-valeur", 
        D: "Stocke des valeurs triées" 
      },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "Un Set stocke uniquement des valeurs uniques. Les doublons sont automatiquement ignorés."
    },
    {
      id: 4402,
      question: "Comment crée-t-on un Set en JavaScript ?",
      options: { A: "let set = []", B: "let set = {}", C: "let set = new Set()", D: "let set = new Array()" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "On utilise le constructeur new Set() pour créer un Set."
    },
    {
      id: 4403,
      question: "Quelle méthode ajoute une valeur à un Set ?",
      options: { A: ".push()", B: ".append()", C: ".add()", D: ".insert()" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "La méthode .add() insère une nouvelle valeur dans le Set."
    },
    {
      id: 4404,
      question: "Comment vérifier si une valeur existe dans un Set ?",
      options: { A: ".contains()", B: ".has()", C: ".includes()", D: ".exist()" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "La méthode .has() vérifie si une valeur existe dans le Set et retourne true ou false."
    },
    {
      id: 4405,
      question: "Quelle propriété donne le nombre d'éléments dans un Set ?",
      options: { A: "length", B: "count", C: "size", D: "items" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "La propriété size retourne le nombre d'éléments dans le Set."
    },
    {
      id: 4406,
      question: "Que se passe-t-il si on ajoute un doublon à un Set ?",
      options: { 
        A: "Une erreur se produit", 
        B: "La valeur est dupliquée", 
        C: "Le doublon est ignoré", 
        D: "Le Set est vidé" 
      },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "Les doublons sont automatiquement ignorés lors de l'ajout à un Set."
    },
    {
      id: 4407,
      question: "Quelle est la différence entre un Set et un Array ?",
      options: { 
        A: "Array permet les doublons, Set non", 
        B: "Set est basé sur des indices, Array non", 
        C: "Array stocke des valeurs uniques", 
        D: "Il n'y a pas de différence" 
      },
      reponse_correcte: "A",
      points: 15,
      difficulte: "moyen",
      explication: "Les tableaux (Array) permettent les doublons, tandis que les Sets stockent uniquement des valeurs uniques."
    },
    {
      id: 4408,
      question: "Que donne new Set([1, 2, 2, 3, 3, 3]) ?",
      options: { 
        A: "Set(3) {1, 2, 3}", 
        B: "Set(6) {1, 2, 2, 3, 3, 3}", 
        C: "Erreur", 
        D: "[1, 2, 3]" 
      },
      reponse_correcte: "A",
      points: 10,
      difficulte: "facile",
      explication: "Set supprime automatiquement les doublons, donc ne conserve que 1, 2, 3."
    },
    {
      id: 4409,
      question: "Comment supprimer toutes les valeurs d'un Set ?",
      options: { A: ".removeAll()", B: ".deleteAll()", C: ".clear()", D: ".reset()" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "La méthode .clear() supprime toutes les valeurs d'un Set."
    },
    {
      id: 4410,
      question: "Quel mot-clé utilise-t-on pour parcourir un Set avec une boucle ?",
      options: { A: "for...in", B: "for...of", C: "forEach", D: "Les réponses B et C" },
      reponse_correcte: "D",
      points: 10,
      difficulte: "facile",
      explication: "On peut parcourir un Set avec for...of ou la méthode .forEach()."
    }
  ],
      43: [ 
    {
      id: 4301,
      question: "Comment crée-t-on un tableau vide en JavaScript ?",
      options: { A: "let arr = {}", B: "let arr = []", C: "let arr = ()", D: "let arr = <>" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "Un tableau se crée avec des crochets []."
    },
    {
      id: 4302,
      question: "Quelle est la propriété qui donne le nombre d'éléments dans un tableau ?",
      options: { A: "size", B: "count", C: "length", D: "items" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "length est la propriété qui retourne le nombre d'éléments."
    },
    {
      id: 4303,
      question: "Quelle méthode ajoute un élément à la fin d'un tableau ?",
      options: { A: "push()", B: "pop()", C: "unshift()", D: "shift()" },
      reponse_correcte: "A",
      points: 10,
      difficulte: "facile",
      explication: "push() ajoute un élément à la fin du tableau."
    },
    {
      id: 4304,
      question: "Quelle méthode supprime le premier élément d'un tableau ?",
      options: { A: "push()", B: "pop()", C: "unshift()", D: "shift()" },
      reponse_correcte: "D",
      points: 10,
      difficulte: "facile",
      explication: "shift() supprime le premier élément et le retourne."
    },
    {
      id: 4305,
      question: "À quel indice commence un tableau en JavaScript ?",
      options: { A: "1", B: "0", C: "-1", D: "dépend de la taille" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "Les indices commencent à 0 en JavaScript."
    },
    {
      id: 4306,
      question: "Que retourne indexOf() si l'élément n'est pas trouvé ?",
      options: { A: "0", B: "null", C: "undefined", D: "-1" },
      reponse_correcte: "D",
      points: 10,
      difficulte: "facile",
      explication: "indexOf() retourne -1 si l'élément n'est pas dans le tableau."
    },
    {
      id: 4307,
      question: "Quelle boucle est recommandée pour parcourir un tableau avec une syntaxe propre ?",
      options: { A: "for", B: "while", C: "for...of", D: "do...while" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "for...of est la boucle recommandée pour parcourir les valeurs d'un tableau."
    },
    {
      id: 4308,
      question: "Que fait la méthode sort() sur un tableau ?",
      options: { A: "Inverse l'ordre", B: "Trie alphabétiquement", C: "Supprime les doublons", D: "Ajoute des éléments" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "sort() trie les éléments d'un tableau dans l'ordre alphabétique."
    },
    {
      id: 4309,
      question: "Comment ajouter un élément au début d'un tableau ?",
      options: { A: "push()", B: "pop()", C: "unshift()", D: "shift()" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "unshift() ajoute un élément au début du tableau."
    },
    {
      id: 4310,
      question: "Que signifie l'expression fruits[2] si fruits = ['pomme', 'banane', 'orange'] ?",
      options: { A: "pomme", B: "banane", C: "orange", D: "undefined" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "fruits[2] accède au troisième élément (indice 2) : 'orange'."
    }
  ],
      42: [ 
    {
      id: 4201,
      question: "Qu'est-ce qu'un objet en JavaScript ?",
      options: { 
        A: "Un tableau de données", 
        B: "Une collection de propriétés et de méthodes", 
        C: "Une variable spéciale", 
        D: "Une boucle" 
      },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "Un objet est une collection de propriétés (données) et de méthodes (fonctions)."
    },
    {
      id: 4202,
      question: "Comment accède-t-on à une propriété d'un objet ?",
      options: { A: "object->property", B: "object[property]", C: "object.property", D: "object:property" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "On utilise la notation pointée : objet.propriete."
    },
    {
      id: 4203,
      question: "Quelle syntaxe utilise-t-on pour créer un objet en JavaScript ?",
      options: { A: "[]", B: "()", C: "{}", D: "<>" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "Les objets sont créés avec des accolades {} contenant des paires clé-valeur."
    },
    {
      id: 4204,
      question: "Qu'est-ce qu'une méthode dans un objet ?",
      options: { 
        A: "Une propriété", 
        B: "Une fonction liée à l'objet", 
        C: "Une variable", 
        D: "Un tableau" 
      },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "Une méthode est une fonction qui appartient à un objet et représente une action."
    },
    {
      id: 4205,
      question: "Pourquoi utilise-t-on des objets en JavaScript ?",
      options: { 
        A: "Pour créer des boucles", 
        B: "Pour modéliser des entités du monde réel", 
        C: "Pour déclarer des variables", 
        D: "Pour importer des modules" 
      },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "Les objets permettent de modéliser des entités réelles avec leurs propriétés et comportements."
    },
    {
      id: 4206,
      question: "Comment appeler une méthode 'sayHello' d'un objet person1 ?",
      options: { A: "person1.sayHello", B: "person1.sayHello()", C: "sayHello(person1)", D: "person1(sayHello)" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "Pour appeler une méthode, on utilise le nom de l'objet suivi du nom de la méthode avec des parenthèses."
    },
    {
      id: 4207,
      question: "Que signifie 'this' à l'intérieur d'une méthode d'objet ?",
      options: { 
        A: "L'objet global", 
        B: "L'objet courant", 
        C: "La fonction parente", 
        D: "Une variable locale" 
      },
      reponse_correcte: "B",
      points: 15,
      difficulte: "moyen",
      explication: "'this' fait référence à l'objet courant, c'est-à-dire l'objet qui appelle la méthode."
    },
    {
      id: 4208,
      question: "Les objets peuvent-ils contenir d'autres objets comme propriétés ?",
      options: { A: "Oui", B: "Non", C: "Seulement avec des tableaux", D: "Uniquement en mode strict" },
      reponse_correcte: "A",
      points: 10,
      difficulte: "facile",
      explication: "Oui, les objets peuvent contenir d'autres objets (propriétés imbriquées)."
    },
    {
      id: 4209,
      question: "Quelle est la différence entre une propriété et une méthode ?",
      options: { 
        A: "Une propriété est une donnée, une méthode est une action", 
        B: "Il n'y a pas de différence", 
        C: "Une propriété est une fonction", 
        D: "Une méthode est une variable" 
      },
      reponse_correcte: "A",
      points: 10,
      difficulte: "facile",
      explication: "Les propriétés stockent des données, les méthodes définissent des actions/comportements."
    },
    {
      id: 4210,
      question: "Comment supprimer une propriété d'un objet ?",
      options: { 
        A: "object.remove('property')", 
        B: "delete object.property", 
        C: "object.property = null", 
        D: "object.delete('property')" 
      },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "L'opérateur delete permet de supprimer une propriété d'un objet."
    }
  ],
       41: [ 
    {
      id: 4101,
      question: "Qu'est-ce qu'une fonction en JavaScript ?",
      options: { 
        A: "Un bloc de code réutilisable", 
        B: "Une variable spéciale", 
        C: "Une boucle", 
        D: "Un type de données" 
      },
      reponse_correcte: "A",
      points: 10,
      difficulte: "facile",
      explication: "Une fonction est un bloc de code réutilisable qui effectue une tâche spécifique."
    },
    {
      id: 4102,
      question: "Que fait le mot-clé 'return' dans une fonction ?",
      options: { 
        A: "Affiche une valeur", 
        B: "Arrête la fonction et renvoie une valeur", 
        C: "Déclare une variable", 
        D: "Crée une boucle" 
      },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "return arrête l'exécution de la fonction et renvoie une valeur à l'appelant."
    },
    {
      id: 4103,
      question: "Comment appelle-t-on une fonction en JavaScript ?",
      options: { A: "functionName", B: "functionName()", C: "call functionName", D: "run functionName" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "Pour appeler une fonction, on utilise son nom suivi de parenthèses."
    },
    {
      id: 4104,
      question: "Quelle est la différence entre paramètre et argument ?",
      options: { 
        A: "C'est la même chose", 
        B: "Paramètre = place dans la définition, argument = valeur passée", 
        C: "Argument = place, paramètre = valeur", 
        D: "Il n'y a pas de différence" 
      },
      reponse_correcte: "B",
      points: 15,
      difficulte: "moyen",
      explication: "Un paramètre est un placeholder dans la définition de la fonction. Un argument est la valeur réelle passée lors de l'appel."
    },
    {
      id: 4105,
      question: "Que retourne la fonction addition(5, 3) ?",
      options: { A: "53", B: "8", C: "2", D: "15" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "addition(5, 3) retourne 8, car 5 + 3 = 8."
    },
    {
      id: 4106,
      question: "Comment savoir si un nombre est pair en JavaScript ?",
      options: { A: "nombre / 2", B: "nombre % 2 === 0", C: "nombre * 2", D: "nombre - 2" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "Le modulo (%) retourne le reste. Si nombre % 2 === 0, le nombre est pair."
    },
    {
      id: 4107,
      question: "Comment valider qu'un email contient le caractère '@' ?",
      options: { 
        A: "email.contains('@')", 
        B: "email.has('@')", 
        C: "email.includes('@')", 
        D: "email.indexOf('@')" 
      },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "includes() vérifie si une chaîne contient une sous-chaîne et retourne true ou false."
    },
    {
      id: 4108,
      question: "Que fait le code 'return nombre % 2 === 0 ? true : false' ?",
      options: { 
        A: "Une boucle", 
        B: "Un opérateur ternaire", 
        C: "Une déclaration de variable", 
        D: "Une fonction fléchée" 
      },
      reponse_correcte: "B",
      points: 15,
      difficulte: "moyen",
      explication: "C'est l'opérateur ternaire, une forme raccourcie de if/else."
    },
    {
      id: 4109,
      question: "Quel mot-clé utilise-t-on pour déclarer une fonction ?",
      options: { A: "func", B: "function", C: "def", D: "define" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "On utilise le mot-clé 'function' pour déclarer une fonction en JavaScript."
    },
    {
      id: 4110,
      question: "Une fois le mot-clé 'return' exécuté, que se passe-t-il ?",
      options: { 
        A: "La fonction continue", 
        B: "La fonction s'arrête immédiatement", 
        C: "La fonction redémarre", 
        D: "Une erreur se produit" 
      },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "return arrête immédiatement l'exécution de la fonction et renvoie la valeur spécifiée."
    }
  ],
      40: [ 
    {
      id: 4001,
      question: "Que signifie NaN en JavaScript ?",
      options: { A: "Null a Number", B: "Not a Number", C: "Number and Null", D: "New Assignment Number" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "NaN signifie 'Not a Number', une valeur spéciale retournée quand une opération mathématique échoue."
    },
    {
      id: 4002,
      question: "Quelle est la différence entre isNaN() et Number.isNaN() ?",
      options: { 
        A: "Elles font la même chose", 
        B: "isNaN() convertit d'abord la valeur, Number.isNaN() ne convertit pas", 
        C: "Number.isNaN() convertit d'abord la valeur", 
        D: "isNaN() est plus récente" 
      },
      reponse_correcte: "B",
      points: 15,
      difficulte: "moyen",
      explication: "isNaN() convertit d'abord la valeur en nombre, Number.isNaN() vérifie si la valeur est NaN sans conversion."
    },
    {
      id: 4003,
      question: "Que retourne Number(true) ?",
      options: { A: "true", B: "false", C: "1", D: "0" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "Number(true) retourne 1, et Number(false) retourne 0."
    },
    {
      id: 4004,
      question: "Que fait parseFloat() ?",
      options: { 
        A: "Convertit en entier", 
        B: "Convertit en nombre décimal", 
        C: "Convertit en chaîne", 
        D: "Convertit en booléen" 
      },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "parseFloat() convertit une chaîne en nombre décimal (flottant)."
    },
    {
      id: 4005,
      question: "Quelle méthode permet de limiter le nombre de décimales ?",
      options: { A: "toDecimal()", B: "toPrecision()", C: "toFixed()", D: "toFloat()" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "toFixed() limite le nombre de décimales et retourne une chaîne."
    },
    {
      id: 4006,
      question: "Quel est le résultat de 5 === '5' en JavaScript ?",
      options: { A: "true", B: "false", C: "10", D: "Erreur" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "5 (nombre) n'est pas égal à '5' (chaîne) car les types sont différents."
    },
    {
      id: 4007,
      question: "Que retourne parseInt('123px') ?",
      options: { A: "123", B: "123px", C: "NaN", D: "0" },
      reponse_correcte: "A",
      points: 10,
      difficulte: "facile",
      explication: "parseInt() extrait l'entier au début de la chaîne, ignorant le reste."
    },
    {
      id: 4008,
      question: "Que retourne Number('abc') ?",
      options: { A: "abc", B: "0", C: "NaN", D: "Erreur" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "Number('abc') ne peut pas convertir 'abc' en nombre, donc retourne NaN."
    },
    {
      id: 4009,
      question: "Quelle méthode vérifie si une valeur est un entier ?",
      options: { A: "isInt()", B: "isInteger()", C: "Number.isInteger()", D: "isNumber()" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "Number.isInteger() vérifie si la valeur est un nombre entier."
    },
    {
      id: 4010,
      question: "Que retourne (3.14159).toFixed(2) ?",
      options: { A: "3.14", B: "3.14159", C: "3.15", D: "'3.14'" },
      reponse_correcte: "D",
      points: 10,
      difficulte: "facile",
      explication: "toFixed(2) retourne une chaîne avec 2 décimales, donc '3.14'."
    }
  ],
      39: [ 
    {
      id: 3901,
      question: "Que signifie qu'une chaîne de caractères est 'immuable' en JavaScript ?",
      options: { 
        A: "Elle peut être modifiée directement", 
        B: "Elle ne peut pas être modifiée; toute modification crée une nouvelle chaîne", 
        C: "Elle est automatiquement convertie en nombre", 
        D: "Elle ne peut pas être utilisée dans des conditions" 
      },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "Les chaînes sont immuables, ce qui signifie qu'une fois créées, elles ne peuvent pas être modifiées. Toute opération qui semble modifier une chaîne crée en réalité une nouvelle chaîne."
    },
    {
      id: 3902,
      question: "Que fait la méthode trim() sur une chaîne ?",
      options: { 
        A: "Supprime tous les espaces", 
        B: "Supprime les espaces au début et à la fin", 
        C: "Ajoute des espaces", 
        D: "Convertit en minuscules" 
      },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "trim() supprime les espaces au début et à la fin d'une chaîne, idéal pour nettoyer les entrées utilisateur."
    },
    {
      id: 3903,
      question: "Quelle propriété retourne le nombre de caractères dans une chaîne ?",
      options: { A: ".size", B: ".count", C: ".length", D: ".charCount" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "length est une propriété qui retourne le nombre de caractères dans une chaîne."
    },
    {
      id: 3904,
      question: "Que retourne la méthode includes() ?",
      options: { 
        A: "Le nombre d'occurrences", 
        B: "La position de la sous-chaîne", 
        C: "true ou false (booléen)", 
        D: "La sous-chaîne trouvée" 
      },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "includes() retourne un booléen (true ou false) selon que la sous-chaîne est présente ou non."
    },
    {
      id: 3905,
      question: "Comment convertir une chaîne CSV en tableau ?",
      options: { A: ".toArray()", B: ".split(',')", C: ".join(',')", D: ".slice()" },
      reponse_correcte: "B",
      points: 15,
      difficulte: "moyen",
      explication: "split(',') divise la chaîne à chaque virgule et retourne un tableau de valeurs."
    },
    {
      id: 3906,
      question: "Que fait toUpperCase() sur une chaîne ?",
      options: { A: "Convertit en minuscules", B: "Convertit en majuscules", C: "Supprime les espaces", D: "Inverse la chaîne" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "toUpperCase() convertit tous les caractères d'une chaîne en majuscules."
    },
    {
      id: 3907,
      question: "Quel est le résultat de 'Hello World'.includes('World') ?",
      options: { A: "true", B: "false", C: "5", D: "World" },
      reponse_correcte: "A",
      points: 10,
      difficulte: "facile",
      explication: "'Hello World' contient la sous-chaîne 'World', donc includes() retourne true."
    },
    {
      id: 3908,
      question: "Comment extraire le nom d'utilisateur d'un email avec split() ?",
      options: { 
        A: "email.split('.')[0]", 
        B: "email.split('@')[1]", 
        C: "email.split('@')[0]", 
        D: "email.split(',')[0]" 
      },
      reponse_correcte: "C",
      points: 15,
      difficulte: "moyen",
      explication: "split('@')[0] divise l'email au niveau du @ et prend la première partie (avant le @)."
    },
    {
      id: 3909,
      question: "Quelle méthode utiliser pour supprimer les espaces inutiles dans un formulaire ?",
      options: { A: ".trim()", B: ".clean()", C: ".removeSpaces()", D: ".strip()" },
      reponse_correcte: "A",
      points: 10,
      difficulte: "facile",
      explication: "trim() est la méthode standard pour supprimer les espaces au début et à la fin d'une chaîne."
    },
    {
      id: 3910,
      question: "Quelle est la valeur de 'JavaScript'.length ?",
      options: { A: "8", B: "9", C: "10", D: "11" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "'JavaScript' contient 10 caractères (J,a,v,a,S,c,r,i,p,t)."
    }
  ],
      38: [ 
    {
      id: 3801,
      question: "Quelles sont les trois parties d'une boucle for en JavaScript ?",
      options: { A: "début, milieu, fin", B: "initialisation, condition, incrément", C: "start, stop, step", D: "init, while, update" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "Une boucle for comporte : initialisation, condition, incrément."
    },
    {
      id: 3802,
      question: "Que fait i++ dans une boucle for ?",
      options: { A: "Décrémente i de 1", B: "Incrémente i de 1", C: "Multiplie i par 2", D: "Divise i par 2" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "i++ incrémente la variable i de 1 à chaque itération."
    },
    {
      id: 3803,
      question: "Combien de fois la boucle for (let i = 0; i < 5; i++) s'exécute-t-elle ?",
      options: { A: "4 fois", B: "5 fois", C: "6 fois", D: "0 fois" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "La boucle s'exécute pour i = 0,1,2,3,4 → 5 fois."
    },
    {
      id: 3804,
      question: "Comment écrire une boucle for qui affiche les nombres de 1 à 5 ?",
      options: { 
        A: "for (let i = 0; i < 5; i++)", 
        B: "for (let i = 1; i <= 5; i++)", 
        C: "for (let i = 1; i < 5; i++)", 
        D: "for (let i = 0; i <= 5; i++)" 
      },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "for (let i = 1; i <= 5; i++) affiche i = 1,2,3,4,5."
    },
    {
      id: 3805,
      question: "Comment créer une boucle for inversée de 5 à 1 ?",
      options: { 
        A: "for (let i = 5; i > 0; i++)", 
        B: "for (let i = 5; i >= 1; i--)", 
        C: "for (let i = 1; i <= 5; i++)", 
        D: "for (let i = 5; i < 1; i--)" 
      },
      reponse_correcte: "B",
      points: 15,
      difficulte: "moyen",
      explication: "i-- décrémente, on commence à 5 et on continue tant que i >= 1."
    },
    {
      id: 3806,
      question: "Que fait l'opérateur i += 2 dans une boucle for ?",
      options: { A: "Incrémente i de 2", B: "Décrémente i de 2", C: "Multiplie i par 2", D: "Divise i par 2" },
      reponse_correcte: "A",
      points: 10,
      difficulte: "facile",
      explication: "i += 2 est équivalent à i = i + 2, on avance de 2 en 2."
    },
    {
      id: 3807,
      question: "Comment parcourir tous les éléments d'un tableau fruits avec une boucle for ?",
      options: { 
        A: "for (let i = 0; i < fruits.length; i++)", 
        B: "for (let i = 0; i <= fruits.length; i++)", 
        C: "for (let i = 1; i < fruits.length; i++)", 
        D: "for (let i = fruits.length; i > 0; i--)" 
      },
      reponse_correcte: "A",
      points: 10,
      difficulte: "facile",
      explication: "La condition i < fruits.length permet de parcourir toutes les cases du tableau."
    },
    {
      id: 3808,
      question: "Quelle boucle est idéale quand on connaît le nombre d'itérations à l'avance ?",
      options: { A: "while", B: "do...while", C: "for", D: "for...in" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "for est idéale quand le nombre d'itérations est connu à l'avance."
    },
    {
      id: 3809,
      question: "Que signifie l'opérateur % (modulo) dans une condition comme i % 2 !== 0 ?",
      options: { A: "Division", B: "Reste de la division", C: "Multiplication", D: "Addition" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "% retourne le reste de la division. i % 2 !== 0 est vrai pour les nombres impairs."
    },
    {
      id: 3810,
      question: "Que se passe-t-il si la condition d'une boucle for n'est jamais vraie ?",
      options: { 
        A: "La boucle s'exécute une fois", 
        B: "La boucle ne s'exécute pas", 
        C: "La boucle s'exécute à l'infini", 
        D: "Une erreur se produit" 
      },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "Si la condition est fausse dès le départ, la boucle ne s'exécute pas."
    }
  ],
      37: [ 
    {
      id: 3701,
      question: "Quelle instruction JavaScript permet d'exécuter un bloc de code si une condition est vraie ?",
      options: { A: "for", B: "while", C: "if", D: "switch" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "if est l'instruction conditionnelle de base qui exécute un bloc si la condition est vraie."
    },
    {
      id: 3702,
      question: "Que fait l'opérateur && en JavaScript ?",
      options: { A: "OU logique", B: "ET logique", C: "NON logique", D: "Assignation" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "&& est l'opérateur ET logique. Il retourne true seulement si les deux opérandes sont true."
    },
    {
      id: 3703,
      question: "Que se passe-t-il si la condition d'un if est fausse et qu'il n'y a pas de else ?",
      options: { 
        A: "Une erreur se produit", 
        B: "Le code continue normalement", 
        C: "Le programme s'arrête", 
        D: "La condition devient vraie" 
      },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "Si la condition est fausse et qu'il n'y a pas de else, rien ne s'exécute et le programme continue."
    },
    {
      id: 3704,
      question: "Quel est le résultat de l'expression (5 > 3 || 2 > 10) ?",
      options: { A: "true", B: "false", C: "undefined", D: "Erreur" },
      reponse_correcte: "A",
      points: 15,
      difficulte: "moyen",
      explication: "5 > 3 est true, donc l'opérateur OR (||) retourne true."
    },
    {
      id: 3705,
      question: "Quelle instruction permet de vérifier plusieurs conditions à la suite ?",
      options: { A: "else", B: "else if", C: "switch", D: "while" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "else if permet de vérifier plusieurs conditions dans l'ordre jusqu'à ce qu'une soit vraie."
    },
    {
      id: 3706,
      question: "Que fait l'opérateur ternaire ?",
      options: { 
        A: "Une forme raccourcie de if/else", 
        B: "Une boucle", 
        C: "Une fonction", 
        D: "Une variable" 
      },
      reponse_correcte: "A",
      points: 15,
      difficulte: "moyen",
      explication: "L'opérateur ternaire (condition ? valeur_si_vrai : valeur_si_faux) est une forme concise de if/else."
    },
    {
      id: 3707,
      question: "Si on a une variable age = 15, que retourne (age >= 18) ?",
      options: { A: "true", B: "false", C: "undefined", D: "null" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "15 >= 18 est false car 15 n'est pas supérieur ou égal à 18."
    },
    {
      id: 3708,
      question: "Quelle est la bonne syntaxe pour un bloc else if ?",
      options: { 
        A: "elseif (condition) { }", 
        B: "else if (condition) { }", 
        C: "else-if (condition) { }", 
        D: "elif (condition) { }" 
      },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "La syntaxe correcte est 'else if (condition) { }' avec un espace entre else et if."
    },
    {
      id: 3709,
      question: "Quel opérateur logique représente le NON (inverse) ?",
      options: { A: "&&", B: "||", C: "!", D: "==" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "! est l'opérateur logique NOT. Il inverse la valeur d'un booléen."
    },
    {
      id: 3710,
      question: "Que se passe-t-il si plusieurs conditions sont vraies dans une chaîne else if ?",
      options: { 
        A: "Toutes s'exécutent", 
        B: "Seule la première vraie s'exécute", 
        C: "Aucune ne s'exécute", 
        D: "Une erreur se produit" 
      },
      reponse_correcte: "B",
      points: 15,
      difficulte: "moyen",
      explication: "Dès qu'une condition est vraie, son bloc s'exécute et le reste de la chaîne est ignoré."
    }
  ],
      36: [ 
    {
      id: 3601,
      question: "Quel opérateur JavaScript est utilisé pour l'assignation ?",
      options: { A: "==", B: "===", C: "=", D: "!=" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "L'opérateur = assigne une valeur à une variable."
    },
    {
      id: 3602,
      question: "Que signifie l'opérateur % en JavaScript ?",
      options: { A: "Pourcentage", B: "Modulo (reste de division)", C: "Division", D: "Multiplication" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "% est l'opérateur modulo qui retourne le reste d'une division."
    },
    {
      id: 3603,
      question: "Que fait l'opérateur += ?",
      options: { A: "Compare si égal", B: "Ajoute et assigne", C: "Multiplie et assigne", D: "Soustrait et assigne" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "x += y équivaut à x = x + y."
    },
    {
      id: 3604,
      question: "Quel opérateur est utilisé pour la concaténation de chaînes ?",
      options: { A: "&", B: "||", C: "+", D: "," },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "L'opérateur + concatène les chaînes en JavaScript."
    },
    {
      id: 3605,
      question: "Que retourne 5 === '5' en JavaScript ?",
      options: { A: "true", B: "false", C: "undefined", D: "Erreur" },
      reponse_correcte: "B",
      points: 15,
      difficulte: "moyen",
      explication: "=== vérifie l'égalité en valeur ET en type. 5 (number) === '5' (string) donne false."
    },
    {
      id: 3606,
      question: "Quel est le résultat de 5 + '5' en JavaScript ?",
      options: { A: "10", B: "55", C: "Erreur", D: "undefined" },
      reponse_correcte: "B",
      points: 15,
      difficulte: "moyen",
      explication: "Lorsqu'on ajoute un nombre et une chaîne, JavaScript convertit le nombre en chaîne et concatène."
    },
    {
      id: 3607,
      question: "Quel opérateur logique représente le ET ?",
      options: { A: "||", B: "&&", C: "!", D: "&" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "&& est l'opérateur ET logique, true uniquement si les deux opérandes sont true."
    },
    {
      id: 3608,
      question: "Que signifie l'opérateur ** en JavaScript ?",
      options: { A: "Multiplication", B: "Exponentiation", C: "Concaténation", D: "Comparaison" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "** est l'opérateur d'exponentiation. 2 ** 3 = 8."
    },
    {
      id: 3609,
      question: "Quelle est la différence entre == et === ?",
      options: { 
        A: "Aucune différence", 
        B: "== compare la valeur, === compare la valeur et le type", 
        C: "=== compare uniquement le type", 
        D: "== est plus rapide" 
      },
      reponse_correcte: "B",
      points: 15,
      difficulte: "moyen",
      explication: "== compare uniquement la valeur (avec conversion), === compare la valeur ET le type."
    },
    {
      id: 3610,
      question: "Que retourne 10 > 5 && 3 < 2 ?",
      options: { A: "true", B: "false", C: "undefined", D: "Erreur" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "10 > 5 est true, 3 < 2 est false, donc true && false = false."
    }
  ],
      35: [ 
    {
      id: 3501,
      question: "Quel type de données représente une valeur logique (vrai/faux) en JavaScript ?",
      options: { A: "Number", B: "String", C: "Boolean", D: "Object" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "Boolean représente les valeurs true (vrai) et false (faux)."
    },
    {
      id: 3502,
      question: "Que se passe-t-il quand on utilise undefined dans une opération mathématique ?",
      options: { A: "0", B: "undefined", C: "NaN", D: "Erreur" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "undefined + 5 donne NaN (Not a Number)."
    },
    {
      id: 3503,
      question: "Quelle est la différence entre null et undefined ?",
      options: { 
        A: "C'est la même chose", 
        B: "null est une valeur assignée, undefined est une variable non assignée", 
        C: "undefined est une valeur assignée, null est non assigné", 
        D: "null est pour les nombres, undefined pour les textes" 
      },
      reponse_correcte: "B",
      points: 15,
      difficulte: "moyen",
      explication: "null est une valeur assignée signifiant 'aucune valeur', undefined signifie qu'une variable a été déclarée mais pas assignée."
    },
    {
      id: 3504,
      question: "Quel type de données représente du texte en JavaScript ?",
      options: { A: "Number", B: "String", C: "Boolean", D: "Symbol" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "String représente les chaînes de caractères (texte)."
    },
    {
      id: 3505,
      question: "Quel type de données permet de créer des identifiants uniques en JavaScript ?",
      options: { A: "Number", B: "String", C: "Object", D: "Symbol" },
      reponse_correcte: "D",
      points: 15,
      difficulte: "moyen",
      explication: "Symbol est un type introduit en ES6 pour créer des identifiants uniques et immuables."
    },
    {
      id: 3506,
      question: "Combien y a-t-il de types de données fondamentaux en JavaScript ?",
      options: { A: "5", B: "6", C: "7", D: "8" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "Il y a 7 types : Boolean, Null, Undefined, Number, String, Symbol, Object."
    },
    {
      id: 3507,
      question: "Quel type de données est utilisé pour stocker des collections de paires clé-valeur ?",
      options: { A: "Array", B: "Object", C: "String", D: "Number" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "Object permet de stocker des données sous forme de paires clé-valeur."
    },
    {
      id: 3508,
      question: "Deux symboles créés avec la même description sont-ils égaux ?",
      options: { A: "Oui", B: "Non", C: "Dépend du navigateur", D: "Seulement en mode strict" },
      reponse_correcte: "B",
      points: 15,
      difficulte: "moyen",
      explication: "Deux symboles avec la même description ne sont pas égaux car chaque symbole est unique."
    },
    {
      id: 3509,
      question: "Que donne null + 5 en JavaScript ?",
      options: { A: "null5", B: "5", C: "NaN", D: "Erreur" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "null se comporte comme 0 dans les opérations mathématiques, donc null + 5 = 5."
    },
    {
      id: 3510,
      question: "Quelle est la valeur d'une variable déclarée mais non assignée ?",
      options: { A: "null", B: "0", C: "undefined", D: "NaN" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "Une variable déclarée mais non assignée a la valeur undefined."
    }
  ],
      34: [ 
    {
      id: 3401,
      question: "Quels sont les trois mots-clés pour déclarer des variables en JavaScript ?",
      options: { A: "variable, let, const", B: "var, let, const", C: "var, let, constant", D: "v, l, c" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "var, let et const sont les trois mots-clés pour déclarer des variables en JavaScript."
    },
    {
      id: 3402,
      question: "Quelle est la bonne pratique pour déclarer une variable dont la valeur ne changera pas ?",
      options: { A: "var", B: "let", C: "const", D: "static" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "const est utilisé pour les valeurs qui ne doivent pas changer."
    },
    {
      id: 3403,
      question: "Quel mot-clé doit-on utiliser pour une variable qui peut changer de valeur ?",
      options: { A: "const", B: "let", C: "var", D: "static" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "let est utilisé pour les variables dont la valeur peut changer."
    },
    {
      id: 3404,
      question: "Que signifie le signe '=' en JavaScript ?",
      options: { A: "Égalité", B: "Assignation", C: "Comparaison", D: "Multiplication" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "En JavaScript, '=' est l'opérateur d'assignation, pas de comparaison."
    },
    {
      id: 3405,
      question: "Quel caractère n'est PAS autorisé dans un nom de variable ?",
      options: { A: "_", B: "$", C: "-", D: "lettre" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "Le tiret '-' n'est pas autorisé dans les noms de variables."
    },
    {
      id: 3406,
      question: "Que se passe-t-il quand on fait '5' + 10 en JavaScript ?",
      options: { A: "15", B: "510", C: "Erreur", D: "undefined" },
      reponse_correcte: "B",
      points: 15,
      difficulte: "moyen",
      explication: "'5' + 10 donne '510' (concaténation car '5' est une chaîne)."
    },
    {
      id: 3407,
      question: "JavaScript est-il sensible à la casse (case-sensitive) pour les noms de variables ?",
      options: { A: "Oui", B: "Non", C: "Parfois", D: "Seulement sur mobile" },
      reponse_correcte: "A",
      points: 10,
      difficulte: "facile",
      explication: "JavaScript est sensible à la casse : 'carName' et 'carname' sont différents."
    },
    {
      id: 3408,
      question: "Quelle est la valeur de x après l'opération x = x + 3 si x valait 5 ?",
      options: { A: "5", B: "3", C: "8", D: "53" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "x = x + 3 calcule 5 + 3, donc x devient 8."
    },
    {
      id: 3409,
      question: "Lequel de ces noms de variable est VALIDE ?",
      options: { A: "2player", B: "player-name", C: "player_name", D: "player name" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "player_name est valide (le tiret bas est autorisé)."
    },
    {
      id: 3410,
      question: "Quel mot-clé est considéré comme déprécié et à éviter ?",
      options: { A: "let", B: "const", C: "var", D: "static" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "var est l'ancienne méthode à éviter. let et const sont préférés."
    }
  ],
      33: [ 
    {
      id: 3301,
      question: "Qu'est-ce que JavaScript ?",
      options: { 
        A: "Un langage de balisage comme HTML", 
        B: "Un langage de programmation du web", 
        C: "Un langage de style comme CSS", 
        D: "Un logiciel de montage vidéo" 
      },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "JavaScript est le langage de programmation du web. Il permet de rendre les pages interactives."
    },
    {
      id: 3302,
      question: "Quelle méthode JavaScript permet de trouver un élément HTML par son ID ?",
      options: { 
        A: "getElementById()", 
        B: "getElementByClass()", 
        C: "getElementByName()", 
        D: "getElementByTag()" 
      },
      reponse_correcte: "A",
      points: 10,
      difficulte: "facile",
      explication: "getElementById() est la méthode qui permet de sélectionner un élément HTML par son attribut id."
    },
    {
      id: 3303,
      question: "Comment modifier le contenu texte d'un élément HTML en JavaScript ?",
      options: { 
        A: "element.value = nouveauTexte", 
        B: "element.innerHTML = nouveauTexte", 
        C: "element.text = nouveauTexte", 
        D: "element.content = nouveauTexte" 
      },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "innerHTML permet de modifier le contenu HTML d'un élément."
    },
    {
      id: 3304,
      question: "Comment masquer un élément HTML avec JavaScript ?",
      options: { 
        A: "element.style.hide = true", 
        B: "element.style.display = 'none'", 
        C: "element.style.visible = false", 
        D: "element.style.opacity = 0" 
      },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "element.style.display = 'none' masque l'élément en le supprimant de la mise en page."
    },
    {
      id: 3305,
      question: "Comment réafficher un élément masqué avec JavaScript ?",
      options: { 
        A: "element.style.display = 'visible'", 
        B: "element.style.display = 'show'", 
        C: "element.style.display = 'block'", 
        D: "element.style.display = 'on'" 
      },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "element.style.display = 'block' (ou 'inline') permet de réafficher un élément masqué."
    },
    {
      id: 3306,
      question: "JavaScript peut-il modifier les attributs HTML comme src d'une image ?",
      options: { A: "Oui", B: "Non", C: "Uniquement avec du CSS", D: "Seulement sur mobile" },
      reponse_correcte: "A",
      points: 10,
      difficulte: "facile",
      explication: "Oui, JavaScript peut modifier n'importe quel attribut HTML, y compris src d'une image."
    },
    {
      id: 3307,
      question: "Quelle propriété CSS utilise-t-on pour modifier la couleur de fond d'un élément en JavaScript ?",
      options: { A: "backgroundColor", B: "background-color", C: "bgColor", D: "background" },
      reponse_correcte: "A",
      points: 10,
      difficulte: "facile",
      explication: "En JavaScript, on utilise backgroundColor (camelCase) pour modifier la couleur de fond."
    },
    {
      id: 3308,
      question: "JavaScript accepte-t-il les guillemets simples et doubles pour les chaînes ?",
      options: { 
        A: "Uniquement les guillemets doubles", 
        B: "Uniquement les guillemets simples", 
        C: "Les deux", 
        D: "Ni l'un ni l'autre" 
      },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "JavaScript accepte à la fois les guillemets simples et doubles pour les chaînes de caractères."
    },
    {
      id: 3309,
      question: "Quelle est la bonne syntaxe pour modifier la taille de police d'un élément ?",
      options: { 
        A: "element.style.font-size = '20px'", 
        B: "element.style.fontSize = '20px'", 
        C: "element.style.fontsize = '20px'", 
        D: "element.style.fontSize = 20px" 
      },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "En JavaScript, les propriétés CSS s'écrivent en camelCase : fontSize, backgroundColor, etc."
    },
    {
      id: 3310,
      question: "Que peut-on faire avec JavaScript sur une page web ?",
      options: { 
        A: "Modifier le HTML", 
        B: "Modifier les styles CSS", 
        C: "Masquer/afficher des éléments", 
        D: "Toutes ces réponses" 
      },
      reponse_correcte: "D",
      points: 10,
      difficulte: "facile",
      explication: "JavaScript peut tout modifier : contenu HTML, styles CSS, attributs, et peut masquer/afficher des éléments."
    }
  ],
      32: [ 
    {
      id: 3201,
      question: "Quelle valeur de float permet de positionner un élément à gauche ?",
      options: { A: "right", B: "none", C: "left", D: "both" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "float: left; positionne l'élément à gauche, permettant au texte de s'enrouler à droite."
    },
    {
      id: 3202,
      question: "À quoi sert la propriété clear en CSS ?",
      options: { 
        A: "À supprimer les flottements", 
        B: "À empêcher les éléments flottants d'apparaître autour d'un élément", 
        C: "À rendre un élément transparent", 
        D: "À centrer un élément" 
      },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "clear empêche les éléments flottants d'apparaître sur le côté spécifié (left, right, both)."
    },
    {
      id: 3203,
      question: "Comment créer une galerie d'images avec des éléments alignés horizontalement en CSS ?",
      options: { A: "display: block;", B: "position: absolute;", C: "float: left;", D: "text-align: center;" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "float: left; permet d'aligner horizontalement les éléments d'une galerie."
    },
    {
      id: 3204,
      question: "Que se passe-t-il lorsqu'un conteneur parent contient uniquement des éléments flottants ?",
      options: { 
        A: "Le conteneur s'étend automatiquement", 
        B: "Le conteneur s'effondre (hauteur nulle)", 
        C: "Le conteneur devient flottant", 
        D: "Le conteneur se divise en colonnes" 
      },
      reponse_correcte: "B",
      points: 15,
      difficulte: "moyen",
      explication: "Un conteneur contenant uniquement des éléments flottants s'effondre. On utilise clearfix pour résoudre ce problème."
    },
    {
      id: 3205,
      question: "Quelle valeur de clear empêche les éléments flottants à gauche ET à droite ?",
      options: { A: "left", B: "right", C: "none", D: "both" },
      reponse_correcte: "D",
      points: 10,
      difficulte: "facile",
      explication: "clear: both; empêche les éléments flottants des deux côtés."
    },
    {
      id: 3206,
      question: "Quel est le comportement par défaut de la propriété float ?",
      options: { A: "left", B: "right", C: "none", D: "both" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "float: none; est la valeur par défaut, aucun flottement n'est appliqué."
    },
    {
      id: 3207,
      question: "Comment résoudre le problème d'effondrement d'un conteneur parent d'éléments flottants ?",
      options: { 
        A: "Ajouter overflow: hidden", 
        B: "Utiliser la technique clearfix", 
        C: "Ajouter clear: both en fin de conteneur", 
        D: "Toutes ces réponses" 
      },
      reponse_correcte: "D",
      points: 15,
      difficulte: "moyen",
      explication: "Plusieurs solutions existent : overflow: hidden, clearfix::after, ou un élément avec clear: both."
    },
    {
      id: 3208,
      question: "Que signifie la technique 'clearfix' ?",
      options: { 
        A: "Une technique pour fixer la hauteur des conteneurs flottants", 
        B: "Une propriété CSS pour centrer les éléments", 
        C: "Une méthode pour supprimer les flottements", 
        D: "Un sélecteur CSS pour les flottants" 
      },
      reponse_correcte: "A",
      points: 15,
      difficulte: "moyen",
      explication: "Clearfix est une technique qui empêche les conteneurs parents de s'effondrer quand ils contiennent des éléments flottants."
    },
    {
      id: 3209,
      question: "Quelle alternative moderne est préférable à float pour les mises en page complexes ?",
      options: { A: "position", B: "Flexbox ou Grid", C: "display: block", D: "text-align" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "Pour les mises en page complexes, Flexbox et Grid sont préférables à float."
    },
    {
      id: 3210,
      question: "Comment faire pour que le texte ne s'enroule pas autour d'une image flottante ?",
      options: { 
        A: "Ajouter clear: both à l'image", 
        B: "Ajouter clear: both au paragraphe suivant", 
        C: "Utiliser float: none", 
        D: "Ajouter overflow: hidden" 
      },
      reponse_correcte: "B",
      points: 15,
      difficulte: "moyen",
      explication: "clear: both sur l'élément suivant empêche l'enroulement autour de l'image flottante."
    }
  ],

      31: [ 
    {
      id: 3101,
      question: "Quelle est la valeur par défaut de la propriété CSS overflow ?",
      options: { A: "hidden", B: "scroll", C: "visible", D: "auto" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "overflow: visible est la valeur par défaut. Le contenu qui dépasse s'affiche en dehors de la boîte."
    },
    {
      id: 3102,
      question: "Quelle valeur d'overflow ajoute des barres de défilement uniquement lorsque c'est nécessaire ?",
      options: { A: "scroll", B: "auto", C: "hidden", D: "visible" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "overflow: auto ajoute des barres de défilement seulement si le contenu dépasse le conteneur."
    },
    {
      id: 3103,
      question: "Comment couper (cacher) le contenu qui dépasse d'un élément ?",
      options: { A: "overflow: visible", B: "overflow: hidden", C: "overflow: scroll", D: "overflow: auto" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "overflow: hidden coupe et cache le contenu qui dépasse du conteneur."
    },
    {
      id: 3104,
      question: "Quelle valeur d'overflow ajoute des barres de défilement quel que soit le contenu ?",
      options: { A: "scroll", B: "auto", C: "hidden", D: "visible" },
      reponse_correcte: "A",
      points: 10,
      difficulte: "facile",
      explication: "overflow: scroll ajoute toujours des barres de défilement, même si le contenu rentre parfaitement."
    },
    {
      id: 3105,
      question: "Que signifie overflow: clip ?",
      options: { 
        A: "Ajoute des barres de défilement", 
        B: "Similaire à hidden mais permet un dépassement partiel avec marge", 
        C: "Affiche le contenu qui dépasse", 
        D: "Supprime le contenu qui dépasse" 
      },
      reponse_correcte: "B",
      points: 15,
      difficulte: "moyen",
      explication: "clip est similaire à hidden mais fonctionne avec overflow-clip-margin pour permettre un dépassement partiel."
    },
    {
      id: 3106,
      question: "Quel est l'inconvénient principal de overflow: scroll ?",
      options: { 
        A: "Il cache le contenu", 
        B: "Il affiche toujours des barres de défilement, même si inutiles", 
        C: "Il ne fonctionne pas sur mobile", 
        D: "Il ralentit la page" 
      },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "scroll affiche toujours des barres de défilement, même quand le contenu rentre, ce qui peut être inesthétique."
    },
    {
      id: 3107,
      question: "Avec overflow: hidden, le contenu caché est-il accessible par copier-coller ?",
      options: { 
        A: "Non, il est complètement inaccessible", 
        B: "Oui, il reste accessible", 
        C: "Seulement sur certains navigateurs", 
        D: "Oui, mais uniquement sur mobile" 
      },
      reponse_correcte: "B",
      points: 15,
      difficulte: "moyen",
      explication: "Même avec hidden, le contenu reste dans le DOM et est accessible (copier-coller, inspecteur, etc.)"
    },
    {
      id: 3108,
      question: "Quelle valeur d'overflow est recommandée pour une zone de texte qui peut contenir beaucoup de contenu ?",
      options: { A: "scroll", B: "hidden", C: "visible", D: "auto" },
      reponse_correcte: "D",
      points: 10,
      difficulte: "facile",
      explication: "auto est recommandé car il ajoute des barres de défilement uniquement si nécessaire."
    },
    {
      id: 3109,
      question: "Laquelle de ces affirmations sur overflow: visible est correcte ?",
      options: { 
        A: "Cache le contenu qui dépasse", 
        B: "Ajoute des barres de défilement", 
        C: "Le contenu qui dépasse s'affiche hors de la boîte", 
        D: "Supprime le contenu qui dépasse" 
      },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "visible permet au contenu qui dépasse de s'afficher en dehors de la boîte."
    },
    {
      id: 3110,
      question: "Quelle propriété permet de contrôler le débordement horizontal uniquement ?",
      options: { A: "overflow", B: "overflow-y", C: "overflow-x", D: "overflow-clip" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "overflow-x contrôle le débordement horizontal, tandis que overflow-y contrôle le vertical."
    }
  ],

      30: [ 
    {
      id: 3001,
      question: "Quelle est la valeur par défaut de la propriété CSS position ?",
      options: { A: "relative", B: "absolute", C: "static", D: "fixed" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "position: static est la valeur par défaut. Les éléments suivent le flux normal de la page."
    },
    {
      id: 3002,
      question: "Quelle valeur de position retire complètement un élément du flux normal de la page ?",
      options: { A: "relative", B: "absolute", C: "fixed", D: "static" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "position: absolute retire l'élément du flux normal. Il est positionné par rapport à son ancêtre positionné."
    },
    {
      id: 3003,
      question: "Quelle valeur de position permet de créer une barre de navigation qui reste visible pendant le défilement ?",
      options: { A: "relative", B: "absolute", C: "fixed", D: "sticky" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "position: fixed fixe l'élément par rapport à la fenêtre du navigateur. Il reste visible lors du défilement."
    },
    {
      id: 3004,
      question: "Quelle valeur de position permet de décaler un élément par rapport à sa position normale sans le retirer du flux ?",
      options: { A: "relative", B: "absolute", C: "fixed", D: "static" },
      reponse_correcte: "A",
      points: 10,
      difficulte: "facile",
      explication: "position: relative déplace l'élément par rapport à sa position normale tout en conservant son espace d'origine."
    },
    {
      id: 3005,
      question: "Quelle est la caractéristique principale de position: sticky ?",
      options: { 
        A: "Il retire l'élément du flux", 
        B: "Il alterne entre relative et fixed selon le défilement", 
        C: "Il fixe l'élément en bas de page", 
        D: "Il empêche le défilement" 
      },
      reponse_correcte: "B",
      points: 15,
      difficulte: "moyen",
      explication: "sticky alterne entre relative et fixed : l'élément reste collé à un seuil lors du défilement."
    },
    {
      id: 3006,
      question: "Que se passe-t-il si on utilise position: absolute sans ancêtre positionné ?",
      options: { 
        A: "L'élément est positionné par rapport au body", 
        B: "L'élément reste à sa position normale", 
        C: "L'élément disparaît", 
        D: "L'élément devient fixed" 
      },
      reponse_correcte: "A",
      points: 15,
      difficulte: "moyen",
      explication: "Sans ancêtre positionné, l'élément absolu se positionne par rapport au corps de la page (<body>)."
    },
    {
      id: 3007,
      question: "Quelle propriété permet de contrôler l'ordre d'empilement des éléments positionnés ?",
      options: { A: "stack-order", B: "layer-index", C: "z-index", D: "overlay" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "z-index contrôle l'ordre d'empilement des éléments positionnés. Plus la valeur est élevée, plus l'élément apparaît au-dessus."
    },
    {
      id: 3008,
      question: "Quelle propriété est nécessaire pour que position: sticky fonctionne ?",
      options: { A: "z-index", B: "display", C: "top, bottom, left ou right", D: "margin" },
      reponse_correcte: "C",
      points: 15,
      difficulte: "moyen",
      explication: "sticky nécessite un seuil comme top: 0 pour déterminer à quel moment l'élément devient collant."
    },
    {
      id: 3009,
      question: "Quelle valeur de position est souvent utilisée comme conteneur pour des éléments absolus ?",
      options: { A: "static", B: "relative", C: "fixed", D: "sticky" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "position: relative sans décalage est souvent utilisé pour créer un contexte de positionnement pour des éléments absolus."
    },
    {
      id: 3010,
      question: "Les propriétés top, right, bottom, left fonctionnent-elles avec position: static ?",
      options: { 
        A: "Oui, comme pour les autres positions", 
        B: "Non, elles n'ont aucun effet", 
        C: "Oui, mais seulement sur mobile", 
        D: "Non, seulement sur desktop" 
      },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "top, right, bottom, left n'ont aucun effet sur un élément avec position: static."
    }
  ]
  ,

      29: [ 
    {
      id: 2901,
      question: "Quelle est la différence entre visibility: hidden et display: none ?",
      options: { 
        A: "Ils font exactement la même chose", 
        B: "visibility: hidden cache mais garde l'espace, display: none supprime complètement l'élément", 
        C: "display: none cache mais garde l'espace, visibility: hidden supprime l'élément", 
        D: "visibility: hidden fonctionne seulement sur mobile" 
      },
      reponse_correcte: "B",
      points: 15,
      difficulte: "moyen",
      explication: "visibility: hidden cache l'élément mais conserve son espace. display: none supprime complètement l'élément."
    },
    {
      id: 2902,
      question: "Comment créer un menu horizontal avec une liste ul et des éléments li ?",
      options: { A: "display: block;", B: "display: inline;", C: "display: none;", D: "visibility: hidden;" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "display: inline sur les éléments li permet de les afficher horizontalement."
    },
    {
      id: 2903,
      question: "Quel est le comportement par défaut d'un élément <div> en CSS ?",
      options: { A: "inline", B: "inline-block", C: "block", D: "flex" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "<div> est un élément block par défaut, il prend toute la largeur disponible."
    },
    {
      id: 2904,
      question: "Quel est le comportement par défaut d'un élément <span> en CSS ?",
      options: { A: "block", B: "inline", C: "inline-block", D: "flex" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "<span> est un élément inline par défaut, il ne prend que la largeur nécessaire."
    },
    {
      id: 2905,
      question: "Que se passe-t-il quand on applique visibility: hidden à un élément ?",
      options: { 
        A: "L'élément disparaît mais l'espace reste vide", 
        B: "L'élément disparaît et l'espace est supprimé", 
        C: "L'élément devient transparent mais reste cliquable", 
        D: "L'élément est déplacé hors de l'écran" 
      },
      reponse_correcte: "A",
      points: 10,
      difficulte: "facile",
      explication: "visibility: hidden cache l'élément, mais l'espace qu'il occupait reste réservé."
    },
    {
      id: 2906,
      question: "Quelle valeur de display supprime complètement un élément de la mise en page ?",
      options: { A: "hidden", B: "invisible", C: "none", D: "collapse" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "display: none; supprime complètement l'élément, comme s'il n'existait pas."
    },
    {
      id: 2907,
      question: "Quelle propriété permet de combiner les avantages de block et inline ?",
      options: { A: "display: block", B: "display: inline", C: "display: inline-block", D: "display: flex" },
      reponse_correcte: "C",
      points: 15,
      difficulte: "moyen",
      explication: "inline-block permet de définir largeur et hauteur tout en restant sur la même ligne."
    },
    {
      id: 2908,
      question: "Les éléments block ont quelle caractéristique ?",
      options: { 
        A: "Prennent toute la largeur disponible", 
        B: "Ne prennent que la largeur nécessaire", 
        C: "Restent sur la même ligne", 
        D: "Ne peuvent pas avoir de largeur définie" 
      },
      reponse_correcte: "A",
      points: 10,
      difficulte: "facile",
      explication: "Les éléments block prennent toute la largeur disponible et forcent un saut de ligne."
    },
    {
      id: 2909,
      question: "Que se passe-t-il quand on applique display: inline à un élément block ?",
      options: { 
        A: "Il devient invisible", 
        B: "Il reste block", 
        C: "Il se comporte comme un élément inline", 
        D: "Il double de taille" 
      },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "display: inline transforme un élément block en élément inline."
    },
    {
      id: 2910,
      question: "Quelle est la différence entre display: inline-block et display: block ?",
      options: { 
        A: "inline-block permet de rester sur la même ligne, block force un saut", 
        B: "inline-block ne permet pas de largeur fixe", 
        C: "block ne permet pas de hauteur fixe", 
        D: "Il n'y a pas de différence" 
      },
      reponse_correcte: "A",
      points: 15,
      difficulte: "moyen",
      explication: "inline-block reste sur la même ligne tout en acceptant largeur et hauteur, contrairement à block."
    }
  ]
  ,
      28: [ 
    {
      id: 2801,
      question: "Quelle propriété CSS permet de fusionner les bordures doubles d'un tableau en une seule ligne ?",
      options: { A: "border-merge", B: "border-collapse", C: "border-single", D: "border-combine" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "border-collapse: collapse; fusionne les bordures adjacentes en une seule ligne."
    },
    {
      id: 2802,
      question: "Quelle propriété CSS permet d'ajouter de l'espace entre le contenu et la bordure d'une cellule de tableau ?",
      options: { A: "margin", B: "spacing", C: "padding", D: "border-spacing" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "padding ajoute de l'espace intérieur entre le contenu et la bordure de la cellule."
    },
    {
      id: 2803,
      question: "Comment centrer horizontalement le texte dans une cellule de tableau ?",
      options: { A: "vertical-align: center;", B: "text-align: center;", C: "align: center;", D: "text-center: true;" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "text-align: center; centre le texte horizontalement dans la cellule."
    },
    {
      id: 2804,
      question: "Quelle propriété CSS contrôle l'alignement vertical du contenu dans une cellule de tableau ?",
      options: { A: "text-align", B: "vertical-align", C: "align-vertical", D: "valign" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "vertical-align contrôle l'alignement vertical (top, middle, bottom)."
    },
    {
      id: 2805,
      question: "Quel est le problème lorsqu'on applique border à la fois au tableau ET aux cellules sans border-collapse ?",
      options: { 
        A: "Les bordures disparaissent", 
        B: "Des bordures doubles apparaissent", 
        C: "Le tableau devient invisible", 
        D: "Les bordures deviennent rouges" 
      },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "Sans border-collapse, le tableau ET les cellules ont chacun leurs bordures, créant un effet de double bordure."
    },
    {
      id: 2806,
      question: "Comment créer un effet de lignes alternées (striped) dans un tableau ?",
      options: { 
        A: "table:nth-child(even)", 
        B: "tr:nth-child(even)", 
        C: "td:nth-child(odd)", 
        D: "table:alternate" 
      },
      reponse_correcte: "B",
      points: 15,
      difficulte: "moyen",
      explication: "tr:nth-child(even) { background-color: #f2f2f2; } permet de colorer les lignes paires."
    },
    {
      id: 2807,
      question: "Comment rendre un tableau responsive sur mobile ?",
      options: { 
        A: "width: 100%;", 
        B: "overflow-x: auto; sur un conteneur parent", 
        C: "display: block;", 
        D: "position: relative;" 
      },
      reponse_correcte: "B",
      points: 15,
      difficulte: "moyen",
      explication: "En plaçant le tableau dans un conteneur avec overflow-x: auto, on permet le défilement horizontal sur mobile."
    },
    {
      id: 2808,
      question: "Quelle propriété permet d'ajouter un effet de survol (hover) sur les lignes d'un tableau ?",
      options: { A: "table:hover", B: "tr:hover", C: "td:hover", D: "tbody:hover" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "tr:hover { background-color: #ddd; } change l'arrière-plan des lignes au survol."
    },
    {
      id: 2809,
      question: "Quelle est la valeur par défaut de text-align pour les en-têtes de tableau (th) ?",
      options: { A: "left", B: "right", C: "center", D: "justify" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "Par défaut, les en-têtes de tableau (th) sont centrés horizontalement."
    },
    {
      id: 2810,
      question: "Comment créer un tableau qui occupe 100% de la largeur de son conteneur ?",
      options: { A: "width: 100%;", B: "size: full;", C: "expand: true;", D: "full-width: yes;" },
      reponse_correcte: "A",
      points: 10,
      difficulte: "facile",
      explication: "width: 100%; permet au tableau d'occuper toute la largeur de son conteneur parent."
    }
  ]
  ,
      27: [ 
    {
      id: 2701,
      question: "Quelle propriété CSS permet de changer le type de puce d'une liste non ordonnée (ul) ?",
      options: { A: "list-style-position", B: "list-style-type", C: "list-style-image", D: "list-marker" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "list-style-type permet de changer le type de marqueur (disc, circle, square, none, etc.)."
    },
    {
      id: 2702,
      question: "Quel est le type de marqueur par défaut pour une liste non ordonnée (ul) ?",
      options: { A: "circle", B: "square", C: "disc", D: "none" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "disc est le type de marqueur par défaut pour les listes non ordonnées (puce pleine)."
    },
    {
      id: 2703,
      question: "Comment remplacer la puce standard par une image personnalisée en CSS ?",
      options: { 
        A: "list-style-type: image;", 
        B: "list-style-image: url('image.png');", 
        C: "list-marker: image('image.png');", 
        D: "bullet-image: url('image.png');" 
      },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "list-style-image: url('image.png'); permet d'utiliser une image personnalisée comme puce."
    },
    {
      id: 2704,
      question: "Quelle est la différence entre list-style-position: inside et outside ?",
      options: { 
        A: "inside place la puce à l'intérieur du bloc texte, outside à l'extérieur", 
        B: "inside place la puce à gauche, outside à droite", 
        C: "inside et outside font la même chose", 
        D: "inside est pour les listes imbriquées" 
      },
      reponse_correcte: "A",
      points: 15,
      difficulte: "moyen",
      explication: "inside place le marqueur à l'intérieur du bloc de texte, outside à l'extérieur (par défaut)."
    },
    {
      id: 2705,
      question: "Quelle valeur de list-style-type faut-il utiliser pour supprimer complètement les puces d'une liste ?",
      options: { A: "disc", B: "circle", C: "none", D: "hidden" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "list-style-type: none; supprime les puces ou numéros d'une liste."
    },
    {
      id: 2706,
      question: "Pour les listes ordonnées (ol), quelle valeur donne des numéros romains majuscules (I, II, III) ?",
      options: { A: "lower-roman", B: "upper-roman", C: "decimal", D: "upper-alpha" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "upper-roman donne des numéros romains en majuscules (I, II, III, IV...)."
    },
    {
      id: 2707,
      question: "Comment créer un menu de navigation horizontal en CSS à partir d'une liste ul ?",
      options: { 
        A: "list-style-type: horizontal;", 
        B: "display: block;", 
        C: "display: inline; ou float: left;", 
        D: "list-style-position: horizontal;" 
      },
      reponse_correcte: "C",
      points: 15,
      difficulte: "moyen",
      explication: "On utilise display: inline ou float: left sur les éléments li pour créer un menu horizontal."
    },
    {
      id: 2708,
      question: "Quelle est la propriété raccourcie pour définir tous les styles de liste en une seule déclaration ?",
      options: { A: "list", B: "list-style", C: "ul-style", D: "marker" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "list-style est la propriété raccourcie qui combine list-style-type, list-style-position et list-style-image."
    },
    {
      id: 2709,
      question: "Quelle propriété CSS faut-il souvent ajouter quand on utilise list-style-type: none ?",
      options: { 
        A: "margin: 0; padding: 0;", 
        B: "border: 0;", 
        C: "display: block;", 
        D: "float: left;" 
      },
      reponse_correcte: "A",
      points: 10,
      difficulte: "facile",
      explication: "Il est souvent nécessaire de supprimer les marges et paddings par défaut avec margin: 0; padding: 0;."
    },
    {
      id: 2710,
      question: "Quelle valeur de list-style-type donne une puce carrée ?",
      options: { A: "disc", B: "circle", C: "square", D: "rectangle" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "square donne une puce carrée pour les listes non ordonnées."
    }
  ],

      26: [ 
    {
      id: 2601,
      question: "Quels sont les quatre états d'un lien en CSS ?",
      options: { 
        A: "start, end, hover, click", 
        B: "link, visited, hover, active", 
        C: "normal, hover, click, focus", 
        D: "static, dynamic, hover, click" 
      },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "Les quatre états sont : link (non visité), visited (visité), hover (survol), active (clic)."
    },
    {
      id: 2602,
      question: "Quelle pseudo-classe CSS cible un lien au moment où la souris le survole ?",
      options: { A: "a:link", B: "a:visited", C: "a:hover", D: "a:active" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "a:hover cible le lien lorsque la souris est au-dessus."
    },
    {
      id: 2603,
      question: "Comment retirer le soulignement par défaut d'un lien en CSS ?",
      options: { 
        A: "text-decoration: none;", 
        B: "text-decoration: underline;", 
        C: "text-decoration: remove;", 
        D: "underline: none;" 
      },
      reponse_correcte: "A",
      points: 10,
      difficulte: "facile",
      explication: "text-decoration: none; supprime le soulignement des liens."
    },
    {
      id: 2604,
      question: "Quelle est la règle mnémotechnique pour retenir l'ordre des pseudo-classes des liens ?",
      options: { A: "HA! LoVe", B: "LoVe HA!", C: "ViHoLa", D: "LiViHoAc" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "LoVe HA! : Link, Visited, Hover, Active."
    },
    {
      id: 2605,
      question: "Pourquoi l'ordre des règles CSS pour les liens est-il important ?",
      options: { 
        A: "Pour des raisons de performance", 
        B: "Parce que hover doit être après link et visited, et active après hover", 
        C: "L'ordre n'a pas d'importance", 
        D: "Pour la compatibilité avec les anciens navigateurs" 
      },
      reponse_correcte: "B",
      points: 15,
      difficulte: "moyen",
      explication: "hover doit être après link et visited, et active après hover. L'ordre LoVe HA! est essentiel."
    },
    {
      id: 2606,
      question: "Quelle pseudo-classe cible un lien au moment précis du clic ?",
      options: { A: "a:link", B: "a:visited", C: "a:hover", D: "a:active" },
      reponse_correcte: "D",
      points: 10,
      difficulte: "facile",
      explication: "a:active cible le lien au moment du clic (avant que la page ne se charge)."
    },
    {
      id: 2607,
      question: "Que se passe-t-il si on place a:hover avant a:visited dans la feuille de style ?",
      options: { 
        A: "Rien ne change", 
        B: "Le style a:visited ne s'appliquera pas après un survol", 
        C: "Le style a:hover ne fonctionnera pas", 
        D: "Le lien deviendra invisible" 
      },
      reponse_correcte: "B",
      points: 15,
      difficulte: "moyen",
      explication: "Si hover est avant visited, les styles visited seront ignorés car hover a la même spécificité mais vient avant."
    },
    {
      id: 2608,
      question: "Comment ajouter un arrière-plan jaune au survol d'un lien ?",
      options: { 
        A: "a:hover { background-color: yellow; }", 
        B: "a:link { background-color: yellow; }", 
        C: "a:visited { background-color: yellow; }", 
        D: "a:active { background-color: yellow; }" 
      },
      reponse_correcte: "A",
      points: 10,
      difficulte: "facile",
      explication: "a:hover { background-color: yellow; } ajoute un arrière-plan jaune au survol."
    },
    {
      id: 2609,
      question: "Quelle pseudo-classe cible un lien déjà cliqué (visité) ?",
      options: { A: "a:link", B: "a:visited", C: "a:hover", D: "a:active" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "a:visited cible les liens que l'utilisateur a déjà visités."
    },
    {
      id: 2610,
      question: "Pourquoi est-il conseillé d'ajouter un effet au survol des liens ?",
      options: { 
        A: "Pour améliorer l'expérience utilisateur", 
        B: "Pour rendre le site plus beau", 
        C: "Pour le référencement", 
        D: "Les réponses A et B sont correctes" 
      },
      reponse_correcte: "D",
      points: 10,
      difficulte: "facile",
      explication: "Les effets au survol améliorent l'expérience utilisateur et rendent le site plus interactif et agréable."
    }
  ],

      25: [ 
    {
      id: 2501,
      question: "Que signifie 'serif' en typographie CSS ?",
      options: { 
        A: "Police sans empattements", 
        B: "Police avec empattements (petites lignes décoratives)", 
        C: "Police à largeur fixe", 
        D: "Police cursive" 
      },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "Serif désigne les polices avec empattements, comme Times New Roman."
    },
    {
      id: 2502,
      question: "Comment définir une police de secours (fallback) en CSS ?",
      options: { 
        A: "font-fallback: Arial;", 
        B: "font-family: Arial, Helvetica, sans-serif;", 
        C: "backup-font: Arial;", 
        D: "font-alternative: Arial;" 
      },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "On utilise font-family avec plusieurs polices séparées par des virgules, en terminant par une famille générique."
    },
    {
      id: 2503,
      question: "Quelle propriété CSS permet de mettre le texte en italique ?",
      options: { A: "font-weight", B: "font-style", C: "text-decoration", D: "font-variant" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "font-style: italic; met le texte en italique."
    },
    {
      id: 2504,
      question: "Quelle est la différence entre les unités px et em pour font-size ?",
      options: { 
        A: "px est relatif, em est absolu", 
        B: "px est absolu (fixe), em est relatif à la police parente", 
        C: "px et em sont identiques", 
        D: "px ne fonctionne que sur mobile" 
      },
      reponse_correcte: "B",
      points: 15,
      difficulte: "moyen",
      explication: "px est une unité absolue (taille fixe), em est relative à la taille de police de l'élément parent."
    },
    {
      id: 2505,
      question: "Que signifie 'monospace' en CSS ?",
      options: { 
        A: "Police avec empattements", 
        B: "Tous les caractères ont la même largeur", 
        C: "Police sans empattements", 
        D: "Police cursive" 
      },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "Monospace signifie que tous les caractères ont la même largeur, idéal pour le code."
    },
    {
      id: 2506,
      question: "A quoi correspondent les valeurs font-weight: 400 et font-weight: 700 ?",
      options: { 
        A: "400 = light, 700 = extra-bold", 
        B: "400 = normal, 700 = bold", 
        C: "400 = italic, 700 = bold", 
        D: "400 = thin, 700 = black" 
      },
      reponse_correcte: "B",
      points: 15,
      difficulte: "moyen",
      explication: "font-weight: 400 équivaut à normal, font-weight: 700 équivaut à bold."
    },
    {
      id: 2507,
      question: "Pourquoi est-il recommandé d'utiliser des unités relatives pour font-size ?",
      options: { 
        A: "Pour des raisons de performance", 
        B: "Pour permettre aux utilisateurs de redimensionner le texte", 
        C: "Pour que le site soit plus beau", 
        D: "C'est une obligation HTML" 
      },
      reponse_correcte: "B",
      points: 15,
      difficulte: "moyen",
      explication: "Les unités relatives permettent aux utilisateurs de redimensionner le texte dans leur navigateur, améliorant l'accessibilité."
    },
    {
      id: 2508,
      question: "Quelle propriété CSS contrôle l'épaisseur du texte (gras) ?",
      options: { A: "font-style", B: "font-size", C: "font-weight", D: "font-family" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "font-weight contrôle l'épaisseur du texte. Les valeurs incluent normal, bold, ou 100 à 900."
    },
    {
      id: 2509,
      question: "Quelle est la différence entre font-style: italic et font-style: oblique ?",
      options: { 
        A: "Italic est plus incliné", 
        B: "Italic utilise une version italique de la police, oblique incline le texte", 
        C: "Oblique est plus supporté", 
        D: "Il n'y a pas de différence" 
      },
      reponse_correcte: "B",
      points: 15,
      difficulte: "moyen",
      explication: "Italic utilise une version italique spéciale de la police, oblique incline mécaniquement le texte. Italic est préféré."
    },
    {
      id: 2510,
      question: "Quelle est la valeur par défaut de font-weight ?",
      options: { A: "bold", B: "normal", C: "100", D: "medium" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "La valeur par défaut de font-weight est normal (équivalent à 400)."
    }
  ],

      24: [ 
    {
      id: 2401,
      question: "Quelle propriété CSS permet d'aligner le texte horizontalement ?",
      options: { A: "text-align", B: "text-decoration", C: "text-transform", D: "text-shadow" },
      reponse_correcte: "A",
      points: 10,
      difficulte: "facile",
      explication: "text-align contrôle l'alignement horizontal du texte (left, right, center, justify)."
    },
    {
      id: 2402,
      question: "Comment retirer le soulignement d'un lien en CSS ?",
      options: { A: "text-decoration: none;", B: "text-decoration: underline;", C: "text-transform: none;", D: "text-align: none;" },
      reponse_correcte: "A",
      points: 10,
      difficulte: "facile",
      explication: "text-decoration: none; supprime la décoration du texte, y compris le soulignement des liens."
    },
    {
      id: 2403,
      question: "Que fait la propriété text-transform: uppercase ?",
      options: { A: "Met le texte en minuscules", B: "Met le texte en majuscules", C: "Met la première lettre en majuscule", D: "Supprime les espaces" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "text-transform: uppercase transforme tout le texte en majuscules."
    },
    {
      id: 2404,
      question: "Quelle propriété permet d'ajouter une ombre au texte ?",
      options: { A: "text-decoration", B: "text-shadow", C: "box-shadow", D: "text-align" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "text-shadow ajoute une ombre portée au texte."
    },
    {
      id: 2405,
      question: "Comment justifier un paragraphe (texte aligné à gauche et à droite) ?",
      options: { A: "text-align: left;", B: "text-align: right;", C: "text-align: center;", D: "text-align: justify;" },
      reponse_correcte: "D",
      points: 10,
      difficulte: "facile",
      explication: "text-align: justify; justifie le texte pour qu'il soit aligné à gauche et à droite."
    },
    {
      id: 2406,
      question: "Quelle propriété contrôle l'espacement entre les lettres ?",
      options: { A: "word-spacing", B: "letter-spacing", C: "line-height", D: "text-indent" },
      reponse_correcte: "B",
      points: 15,
      difficulte: "moyen",
      explication: "letter-spacing définit l'espacement entre les caractères (lettres)."
    },
    {
      id: 2407,
      question: "Quelle propriété définit la hauteur de ligne (interlignage) ?",
      options: { A: "line-height", B: "letter-spacing", C: "word-spacing", D: "text-indent" },
      reponse_correcte: "A",
      points: 10,
      difficulte: "facile",
      explication: "line-height contrôle l'interlignage entre les lignes de texte."
    },
    {
      id: 2408,
      question: "Quelle valeur de text-decoration permet de barrer le texte ?",
      options: { A: "underline", B: "overline", C: "line-through", D: "none" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "text-decoration: line-through; ajoute une ligne qui traverse le texte (effet barré)."
    },
    {
      id: 2409,
      question: "Que signifie text-transform: capitalize ?",
      options: { A: "Tout en majuscules", B: "Tout en minuscules", C: "Première lettre de chaque mot en majuscule", D: "Aucune transformation" },
      reponse_correcte: "C",
      points: 15,
      difficulte: "moyen",
      explication: "capitalize met la première lettre de chaque mot en majuscule."
    },
    {
      id: 2410,
      question: "Quelle propriété permet de décaler la première ligne d'un paragraphe ?",
      options: { A: "text-align", B: "text-indent", C: "letter-spacing", D: "word-spacing" },
      reponse_correcte: "B",
      points: 15,
      difficulte: "moyen",
      explication: "text-indent définit l'indentation (décalage) de la première ligne d'un paragraphe."
    }
  ],

      22: [ 
    {
      id: 2201,
      question: "Quelle est la différence entre margin et padding ?",
      options: { 
        A: "margin et padding font la même chose", 
        B: "margin est l'espace extérieur (hors bordure), padding est l'espace intérieur", 
        C: "margin s'applique au texte, padding aux images", 
        D: "margin ne fonctionne que sur mobile" 
      },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "Margin crée de l'espace à l'extérieur de la bordure, tandis que padding crée de l'espace à l'intérieur."
    },
    {
      id: 2202,
      question: "Comment centrer horizontalement un élément block avec margin ?",
      options: { A: "margin: center;", B: "margin: 0 auto;", C: "margin: auto 0;", D: "text-align: center;" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "margin: 0 auto; centre l'élément horizontalement. L'élément doit avoir une largeur définie."
    },
    {
      id: 2203,
      question: "Que signifie margin: 10px 20px 30px 40px ?",
      options: { 
        A: "top=10px, right=20px, bottom=30px, left=40px", 
        B: "top=40px, right=30px, bottom=20px, left=10px", 
        C: "top=10px, right=30px, bottom=20px, left=40px", 
        D: "top=10px, right=40px, bottom=20px, left=30px" 
      },
      reponse_correcte: "A",
      points: 15,
      difficulte: "moyen",
      explication: "L'ordre des valeurs suit le sens horaire : top, right, bottom, left."
    },
    {
      id: 2204,
      question: "Qu'est-ce que le 'margin collapsing' ?",
      options: { 
        A: "Les marges disparaissent complètement", 
        B: "Les marges horizontales se fusionnent", 
        C: "Les marges verticales entre éléments adjacents se fusionnent en une seule marge", 
        D: "Les marges deviennent transparentes" 
      },
      reponse_correcte: "C",
      points: 15,
      difficulte: "moyen",
      explication: "Le margin collapsing fusionne les marges verticales adjacentes en une seule marge (la plus grande)."
    },
    {
      id: 2205,
      question: "Quelle propriété définit la marge uniquement à droite ?",
      options: { A: "margin-right", B: "margin-left", C: "margin-bottom", D: "margin-top" },
      reponse_correcte: "A",
      points: 10,
      difficulte: "facile",
      explication: "margin-right définit la marge sur le côté droit de l'élément."
    }
  ],
  
  23: [ 
    {
      id: 2301,
      question: "Que fait la propriété padding en CSS ?",
      options: { 
        A: "Crée de l'espace à l'extérieur de l'élément", 
        B: "Crée de l'espace à l'intérieur, entre le contenu et la bordure", 
        C: "Ajoute une bordure autour de l'élément", 
        D: "Change la couleur de fond" 
      },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "Le padding crée de l'espace à l'intérieur de l'élément, entre son contenu et sa bordure."
    },
    {
      id: 2302,
      question: "Quel padding applique 10px en haut/bas et 20px à gauche/droite ?",
      options: { 
        A: "padding: 10px 20px;", 
        B: "padding: 20px 10px;", 
        C: "padding: 10px 20px 10px 20px;", 
        D: "Les réponses A et C sont correctes" 
      },
      reponse_correcte: "D",
      points: 10,
      difficulte: "facile",
      explication: "padding: 10px 20px; équivaut à padding: 10px 20px 10px 20px; (top/bottom=10px, right/left=20px)."
    },
    {
      id: 2303,
      question: "À quoi correspond padding: 20px ?",
      options: { 
        A: "20px uniquement en haut", 
        B: "20px sur les 4 côtés", 
        C: "20px à gauche et droite", 
        D: "20px en haut et bas" 
      },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "Une seule valeur pour padding s'applique aux 4 côtés (top, right, bottom, left)."
    },
    {
      id: 2304,
      question: "Le padding peut-il avoir une couleur d'arrière-plan ?",
      options: { 
        A: "Non, il est toujours transparent", 
        B: "Oui, car il est à l'intérieur de la bordure", 
        C: "Seulement sur les éléments block", 
        D: "Uniquement en mode impression" 
      },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "Le padding hérite de la couleur d'arrière-plan de l'élément car il est à l'intérieur de la bordure."
    },
    {
      id: 2305,
      question: "Comment définir un padding de 5px en haut et 15px sur les autres côtés ?",
      options: { 
        A: "padding: 5px 15px;", 
        B: "padding: 15px 5px;", 
        C: "padding: 5px 15px 15px 15px;", 
        D: "padding: 15px 5px 5px 5px;" 
      },
      reponse_correcte: "C",
      points: 15,
      difficulte: "moyen",
      explication: "padding: 5px 15px 15px 15px; donne top=5px, right=15px, bottom=15px, left=15px."
    }
  ],

      17: [
    {
      id: 1701,
      question: "Quel est le sélecteur CSS qui cible TOUS les paragraphes d'une page ?",
      options: { A: "#paragraph", B: ".paragraph", C: "p", D: "<p>" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "Le sélecteur d'élément 'p' cible tous les paragraphes &lt;p&gt; de la page."
    },
    {
      id: 1702,
      question: "Quelle syntaxe utilise-t-on pour cibler un élément par son ID ?",
      options: { A: ".monId", B: "#monId", C: "monId", D: "*monId" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "Le sélecteur d'ID utilise le symbole # suivi du nom de l'ID."
    },
    {
      id: 1703,
      question: "Quelle est la principale différence entre un ID et une classe en CSS ?",
      options: { 
        A: "Les IDs sont pour le texte, les classes pour les images", 
        B: "Un ID est unique sur la page, une classe peut être réutilisée plusieurs fois", 
        C: "Les IDs fonctionnent uniquement sur mobile", 
        D: "Les classes sont plus récentes que les IDs" 
      },
      reponse_correcte: "B",
      points: 15,
      difficulte: "moyen",
      explication: "Un ID doit être unique dans la page (un seul élément), tandis qu'une classe peut être appliquée à plusieurs éléments."
    },
    {
      id: 1704,
      question: "Comment cibler tous les éléments qui ont la classe 'highlight' ?",
      options: { A: "#highlight", B: "highlight", C: ".highlight", D: "*highlight" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "Le sélecteur de classe utilise le point '.' suivi du nom de la classe."
    },
    {
      id: 1705,
      question: "Que signifie le sélecteur CSS 'p.highlight' ?",
      options: { 
        A: "Tous les paragraphes ET tous les éléments avec classe highlight", 
        B: "Tous les paragraphes qui ont la classe highlight", 
        C: "Tous les éléments avec la classe highlight à l'intérieur d'un paragraphe", 
        D: "Le paragraphe ayant l'ID highlight" 
      },
      reponse_correcte: "B",
      points: 15,
      difficulte: "moyen",
      explication: "p.highlight cible spécifiquement les balises &lt;p&gt; qui ont la classe 'highlight'."
    },
    {
      id: 1706,
      question: "Quel sélecteur est le plus approprié pour styliser un bouton présent plusieurs fois sur une page ?",
      options: { 
        A: "ID (#submit)", 
        B: "Classe (.btn-submit)", 
        C: "Élément (button)", 
        D: "Attribut ([type='submit'])" 
      },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "Une classe est idéale car elle permet d'appliquer les mêmes styles à plusieurs boutons similaires."
    },
    {
      id: 1707,
      question: "Un élément HTML peut-il avoir plusieurs classes ?",
      options: { 
        A: "Oui, en séparant les classes par des espaces", 
        B: "Non, un élément ne peut avoir qu'une seule classe", 
        C: "Oui, mais seulement deux classes maximum", 
        D: "Non, car cela créerait des conflits" 
      },
      reponse_correcte: "A",
      points: 10,
      difficulte: "facile",
      explication: "Un élément peut avoir plusieurs classes séparées par des espaces, comme class='btn btn-primary large'."
    },
    {
      id: 1708,
      question: "Le sélecteur '#header' a une spécificité plus élevée que le sélecteur '.header' ?",
      options: { 
        A: "Oui, les IDs ont une spécificité plus élevée que les classes", 
        B: "Non, ils ont la même spécificité", 
        C: "Cela dépend de l'ordre dans le fichier CSS", 
        D: "Les classes ont une spécificité plus élevée" 
      },
      reponse_correcte: "A",
      points: 15,
      difficulte: "moyen",
      explication: "Les sélecteurs d'ID ont une spécificité plus élevée (100) que les classes (10)."
    },
    {
      id: 1709,
      question: "Quel sélecteur CSS ciblera tous les titres h1 de la page ?",
      options: { A: "#h1", B: ".h1", C: "h1", D: "<h1>" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "Le sélecteur d'élément 'h1' cible toutes les balises &lt;h1&gt; de la page."
    },
    {
      id: 1710,
      question: "Pourquoi est-il recommandé d'utiliser des classes plutôt que des IDs pour le styling ?",
      options: { 
        A: "Parce que les IDs sont obsolètes", 
        B: "Parce que les classes sont réutilisables et plus flexibles", 
        C: "Parce que les IDs ne fonctionnent pas sur tous les navigateurs", 
        D: "Parce que les classes sont plus rapides" 
      },
      reponse_correcte: "B",
      points: 15,
      difficulte: "moyen",
      explication: "Les classes sont réutilisables, permettent plus de flexibilité et rendent le CSS plus maintenable."
    }
  ],

  20: [ 
    {
      id: 2001,
      question: "Quelle propriété CSS est fondamentale car elle doit être définie pour que la bordure s'affiche ?",
      options: { A: "border-width", B: "border-color", C: "border-style", D: "border-radius" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "border-style est la propriété fondamentale. Sans style défini, la bordure ne s'affiche pas, même si width et color sont définis."
    },
    {
      id: 2002,
      question: "Quel style de bordure donne un effet 3D creusé (enfoncé) ?",
      options: { A: "ridge", B: "groove", C: "outset", D: "inset" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "groove crée un effet 3D creusé (comme une rainure), tandis que ridge donne un effet en relief."
    },
    {
      id: 2003,
      question: "Comment créer une bordure pleine rouge de 2 pixels ?",
      options: { 
        A: "border: 2px solid red;", 
        B: "border: red 2px solid;", 
        C: "border: solid red 2px;", 
        D: "Toutes ces réponses" 
      },
      reponse_correcte: "D",
      points: 10,
      difficulte: "facile",
      explication: "Toutes ces syntaxes sont correctes. border accepte les valeurs dans n'importe quel ordre (width, style, color)."
    },
    {
      id: 2004,
      question: "Quelle propriété permet d'arrondir les coins d'une bordure ?",
      options: { A: "border-round", B: "border-corner", C: "border-radius", D: "border-circle" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "border-radius permet d'arrondir les coins des bordures. Plus la valeur est grande, plus les coins sont arrondis."
    },
    {
      id: 2005,
      question: "Comment appliquer une bordure uniquement en bas d'un élément ?",
      options: { 
        A: "border: bottom 2px solid red;", 
        B: "border-bottom: 2px solid red;", 
        C: "border-bottom-style: solid; border-bottom-width: 2px; border-bottom-color: red;", 
        D: "Les réponses B et C sont correctes" 
      },
      reponse_correcte: "D",
      points: 15,
      difficulte: "moyen",
      explication: "border-bottom est la propriété raccourcie, mais on peut aussi utiliser les propriétés individuelles."
    },
    {
      id: 2006,
      question: "Que signifie border-style: double ?",
      options: { 
        A: "Deux bordures superposées", 
        B: "Deux lignes parallèles avec un espace entre elles", 
        C: "Bordure qui change de couleur", 
        D: "Bordure clignotante" 
      },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "double crée deux lignes parallèles. L'épaisseur totale est divisée pour créer la bordure double."
    },
    {
      id: 2007,
      question: "Quelle est la valeur par défaut de border-width ?",
      options: { A: "thin", B: "medium", C: "thick", D: "1px" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "La valeur par défaut de border-width est 'medium' (environ 3-4px selon le navigateur)."
    },
    {
      id: 2008,
      question: "Comment écrire la propriété raccourcie pour définir des bordures différentes sur chaque côté ?",
      options: { 
        A: "border: solid 2px red, dashed 4px blue;", 
        B: "border-style: solid dashed dotted double;", 
        C: "border: top solid, right dashed, bottom dotted, left double;", 
        D: "border-sides: solid 2px;" 
      },
      reponse_correcte: "B",
      points: 15,
      difficulte: "moyen",
      explication: "On peut utiliser border-style avec 4 valeurs (top, right, bottom, left) pour définir des styles différents sur chaque côté."
    },
    {
      id: 2009,
      question: "Quel style de bordure donne un effet 3D saillant (qui ressort) ?",
      options: { A: "inset", B: "outset", C: "groove", D: "ridge" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "outset crée un effet 3D saillant, comme si la bordure ressortait de l'écran."
    },
    {
      id: 2010,
      question: "Que se passe-t-il si on définit border-color sans définir border-style ?",
      options: { 
        A: "La bordure s'affiche avec le style solid par défaut", 
        B: "La bordure s'affiche avec la couleur définie", 
        C: "Aucune bordure ne s'affiche car border-style n'est pas défini", 
        D: "La bordure hérite du style de l'élément parent" 
      },
      reponse_correcte: "C",
      points: 15,
      difficulte: "moyen",
      explication: "border-style doit toujours être défini. Sans style, la bordure ne s'affiche pas, peu importe les autres propriétés définies."
    }
  ]
  ,
  19: [ 
    {
      id: 1901,
      question: "Quelle propriété CSS permet de définir une image d'arrière-plan ?",
      options: { 
        A: "image-background", 
        B: "background-image", 
        C: "bg-image", 
        D: "img-background" 
      },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "La propriété 'background-image' permet de définir une image comme arrière-plan d'un élément."
    },
    {
      id: 1902,
      question: "Comment empêcher une image d'arrière-plan de se répéter ?",
      options: { 
        A: "background-repeat: repeat", 
        B: "background-repeat: once", 
        C: "background-repeat: no-repeat", 
        D: "background-repeat: none" 
      },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "background-repeat: no-repeat empêche l'image de se répéter."
    },
    {
      id: 1903,
      question: "Que signifie background-size: cover ?",
      options: { 
        A: "L'image est affichée en taille réelle", 
        B: "L'image couvre entièrement l'élément (peut être rognée)", 
        C: "L'image est réduite à 50%", 
        D: "L'image est agrandie à 200%" 
      },
      reponse_correcte: "B",
      points: 15,
      difficulte: "moyen",
      explication: "cover redimensionne l'image pour couvrir entièrement l'élément, même si cela signifie rogner certaines parties."
    },
    {
      id: 1904,
      question: "Quelle propriété contrôle la position d'une image d'arrière-plan ?",
      options: { 
        A: "background-location", 
        B: "background-align", 
        C: "background-position", 
        D: "background-place" 
      },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "background-position contrôle l'emplacement de l'image d'arrière-plan."
    },
    {
      id: 1905,
      question: "Que fait background-repeat: repeat-x ?",
      options: { 
        A: "Répète l'image verticalement seulement", 
        B: "Répète l'image horizontalement seulement", 
        C: "Répète l'image dans les deux directions", 
        D: "Ne répète pas l'image" 
      },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "repeat-x répète l'image uniquement horizontalement (de gauche à droite)."
    },
    {
      id: 1906,
      question: "Quelle est la différence entre background-size: cover et contain ?",
      options: { 
        A: "cover remplit l'élément (peut rogner), contain montre l'image entière (peut laisser des espaces)", 
        B: "cover et contain font la même chose", 
        C: "contain remplit l'élément, cover montre l'image entière", 
        D: "cover est pour mobile, contain pour desktop" 
      },
      reponse_correcte: "A",
      points: 15,
      difficulte: "moyen",
      explication: "cover remplit entièrement l'élément (peut rogner), contain montre l'image entière (peut laisser des espaces vides)."
    },
    {
      id: 1907,
      question: "Pourquoi est-il important de définir une couleur d'arrière-plan avec une image ?",
      options: { 
        A: "Pour améliorer les performances", 
        B: "Comme fallback si l'image ne charge pas", 
        C: "Pour que l'image soit plus belle", 
        D: "C'est obligatoire" 
      },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "La couleur d'arrière-plan sert de fallback pendant le chargement ou si l'image ne peut pas être chargée."
    },
    {
      id: 1908,
      question: "Comment centrer une image d'arrière-plan ?",
      options: { 
        A: "background-position: middle", 
        B: "background-position: center", 
        C: "background-align: center", 
        D: "background-pos: 50%" 
      },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "background-position: center centre l'image d'arrière-plan horizontalement et verticalement."
    },
    {
      id: 1909,
      question: "Comment appliquer plusieurs images d'arrière-plan sur le même élément ?",
      options: { 
        A: "Impossible en CSS", 
        B: "En séparant les images par des virgules", 
        C: "En utilisant plusieurs propriétés background-image", 
        D: "Avec la propriété background-stack" 
      },
      reponse_correcte: "B",
      points: 15,
      difficulte: "difficile",
      explication: "On peut utiliser plusieurs images en les séparant par des virgules dans background-image."
    },
    {
      id: 1910,
      question: "Quelle propriété permet de contrôler la taille d'une image d'arrière-plan ?",
      options: { 
        A: "background-size", 
        B: "background-dimension", 
        C: "image-size", 
        D: "bg-size" 
      },
      reponse_correcte: "A",
      points: 10,
      difficulte: "facile",
      explication: "background-size contrôle la taille de l'image d'arrière-plan."
    }
  ],
      6: [
        {
          id: 1,
          question: "Quelle balise utiliser pour le titre principal d'une page HTML ?",
          options: { A: "<title>", B: "<h1>", C: "<head>", D: "<header>" },
          reponse_correcte: "B",
          points: 10,
          difficulte: "facile",
          explication: "La balise <h1> est utilisée pour le titre principal d'une page."
        },
        {
          id: 2,
          question: "Quelle est la différence entre <strong> et <b> en HTML ?",
          options: { 
            A: "Aucune différence", 
            B: "<strong> est sémantique, <b> est visuel", 
            C: "<b> est plus récent", 
            D: "<strong> fonctionne seulement dans les titres" 
          },
          reponse_correcte: "B",
          points: 15,
          difficulte: "moyen",
          explication: "<strong> a une signification sémantique, tandis que <b> est seulement pour l'apparence visuelle."
        }
      ],
      11: [
        {
          id: 3,
          question: "Pourquoi la page d'accueil d'un site web est-elle généralement nommée 'index.html' ?",
          options: { 
            A: "C'est une convention imposée", 
            B: "Les serveurs web sont configurés pour servir ce fichier par défaut", 
            C: "C'est plus facile à retenir", 
            D: "Cela améliore le référencement" 
          },
          reponse_correcte: "B",
          points: 10,
          difficulte: "facile",
          explication: "Les serveurs web sont configurés pour servir automatiquement 'index.html' par défaut."
        },
        {
          id: 8,
          question: "Quelle est la différence entre un lien relatif et un lien absolu en HTML ?",
          options: { 
            A: "Les liens relatifs sont plus rapides à charger", 
            B: "Les liens relatifs sont basés sur l'emplacement actuel, les absolus sur la racine", 
            C: "Les liens absolus ne fonctionnent qu'en ligne", 
            D: "Il n'y a pas de différence fonctionnelle" 
          },
          reponse_correcte: "B",
          points: 20,
          difficulte: "avancé",
          explication: "Un lien relatif est relatif à l'emplacement actuel, un lien absolu part de la racine."
        }
      ],
       9: [
    {
      id: 901,
      question: "Quelle balise HTML5 est utilisée pour définir le contenu principal et unique d'une page ?",
      options: { A: "<header>", B: "<section>", C: "<main>", D: "<article>" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "La balise <main> représente le contenu principal du document, et il ne doit y en avoir qu'une par page."
    },
    {
      id: 902,
      question: "Quel est l'avantage principal d'utiliser des balises sémantiques plutôt que des balises <div> ?",
      options: { 
        A: "Un chargement plus rapide", 
        B: "Une meilleure accessibilité et un meilleur référencement SEO", 
        C: "Des couleurs par défaut plus jolies", 
        D: "La compatibilité avec tous les navigateurs" 
      },
      reponse_correcte: "B",
      points: 15,
      difficulte: "moyen",
      explication: "Les balises sémantiques aident les technologies d'assistance et les moteurs de recherche à comprendre la structure et le rôle du contenu."
    },
    {
      id: 903,
      question: "Quelle est la bonne structure pour regrouper une image et sa légende ?",
      options: { 
        A: "<div><img><span>", 
        B: "</td><description>", 
        C: "<figure><img><figcaption></figure>", 
        D: "<media><img><legend>" 
      },
      reponse_correcte: "C",
      points: 10,
      difficulte: "moyen",
      explication: "<figure> s'utilise pour du contenu multimédia (image, graphique) et <figcaption> pour lui associer une légende."
    },
    {
      id: 904,
      question: "Que signifie 'Div Soup' en HTML ?",
      options: { 
        A: "Une soupe avec des divisions", 
        B: "Un code HTML avec trop de balises <div> non sémantiques", 
        C: "Un style CSS pour les <div>", 
        D: "Une nouvelle balise HTML5" 
      },
      reponse_correcte: "B",
      points: 15,
      difficulte: "difficile",
      explication: '"Div soup" désigne un code HTML où les développeurs utilisent excessivement des balises <div> sans signification sémantique, rendant le code difficile à lire et maintenir.'
    }
  ],
  10: [
    {
      id: 1001,
      question: "Quelle propriété CSS permet d'activer Flexbox sur un conteneur ?",
      options: { A: "display: flex", B: "display: block", C: "display: grid", D: "display: inline" },
      reponse_correcte: "A",
      points: 10,
      difficulte: "facile",
      explication: "display: flex active le mode Flexbox sur un conteneur."
    },
    {
      id: 1002,
      question: "Quelle est la différence principale entre Flexbox et CSS Grid ?",
      options: { 
        A: "Flexbox est 1D, Grid est 2D", 
        B: "Flexbox est plus récent", 
        C: "Grid ne fonctionne que sur mobile", 
        D: "Flexbox est uniquement pour les colonnes" 
      },
      reponse_correcte: "A",
      points: 15,
      difficulte: "moyen",
      explication: "Flexbox gère une seule dimension (ligne ou colonne), alors que Grid gère les deux dimensions (lignes ET colonnes)."
    },
    {
      id: 1003,
      question: "Que signifie 'fr' dans CSS Grid ?",
      options: { A: "Fraction", B: "Frame", C: "Flexible Ratio", D: "Free space" },
      reponse_correcte: "A",
      points: 10,
      difficulte: "moyen",
      explication: "fr signifie 'fraction' et représente une fraction de l'espace disponible dans une grille CSS Grid."
    },
    {
      id: 1004,
      question: "Quelle propriété CSS permet d'aligner les éléments horizontalement en Flexbox ?",
      options: { A: "align-items", B: "justify-content", C: "flex-direction", D: "align-content" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "justify-content contrôle l'alignement horizontal des éléments en Flexbox."
    },
    {
      id: 1005,
      question: "Comment créer un espacement entre les éléments d'une grille CSS ?",
      options: { A: "gap", B: "margin", C: "padding", D: "spacing" },
      reponse_correcte: "A",
      points: 10,
      difficulte: "facile",
      explication: "La propriété 'gap' définit l'espacement entre les éléments d'une grille."
    }
  ],
  13: [ 
    {
      id: 1301,
      question: "Quelle balise HTML utilise-t-on pour créer une ligne dans un tableau ?",
      options: { A: "<td>", B: "<tr>", C: "<table>", D: "<th>" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "La balise <tr> (table row) définit une ligne dans un tableau HTML."
    },
    {
      id: 1302,
      question: "Quelle balise est utilisée pour une cellule d'en-tête dans un tableau HTML ?",
      options: { A: "<td>", B: "<thead>", C: "<th>", D: "<caption>" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "<th> (table header) est utilisée pour les cellules d'en-tête, généralement affichées en gras et centrées."
    },
    {
      id: 1303,
      question: "Quel est l'objectif principal des tableaux en HTML ?",
      options: { 
        A: "Mettre en forme la mise en page d'une page", 
        B: "Organiser et afficher des données structurées", 
        C: "Ajouter des images", 
        D: "Créer des formulaires" 
      },
      reponse_correcte: "B",
      points: 15,
      difficulte: "facile",
      explication: "Les tableaux sont conçus pour organiser et afficher des informations structurées en lignes et colonnes."
    },
    {
      id: 1304,
      question: "Quelle est la structure minimale correcte pour un tableau HTML basique ?",
      options: { 
        A: "<table><td>cellule</td></table>", 
        B: "<table><tr><td>cellule</td></tr></table>", 
        C: "<table><th>cellule</th></table>", 
        D: "<tr><td>cellule</td></tr>" 
      },
      reponse_correcte: "B",
      points: 15,
      difficulte: "moyen",
      explication: "La structure minimale est <table> contenant <tr> (ligne) qui contient <td> (cellule)."
    }
  ],
  14: [ 
    {
      id: 1401,
      question: "Quel est le rôle principal de la section <head> en HTML ?",
      options: { 
        A: "Afficher le contenu principal de la page", 
        B: "Contenir des métadonnées sur la page (non visible)", 
        C: "Définir la structure des articles", 
        D: "Créer des liens hypertextes" 
      },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "La section <head> contient des métadonnées (informations sur la page) qui ne sont pas visibles directement par l'utilisateur."
    },
    {
      id: 1402,
      question: "Quelle balise définit le titre d'une page qui apparaît dans l'onglet du navigateur ?",
      options: { A: "<header>", B: "<h1>", C: "<title>", D: "<head>" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "La balise <title> définit le titre de la page, visible dans l'onglet du navigateur."
    },
    {
      id: 1403,
      question: "À quoi sert la balise <meta charset='UTF-8'> ?",
      options: { 
        A: "Définir la police d'écriture", 
        B: "Définir l'encodage des caractères", 
        C: "Créer une redirection", 
        D: "Définir la langue de la page" 
      },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "Cette balise définit l'encodage des caractères en UTF-8, permettant d'afficher correctement tous les caractères."
    },
    {
      id: 1404,
      question: "Quelle balise utilise-t-on pour lier un fichier CSS externe ?",
      options: { A: "<style>", B: "<css>", C: "<link>", D: "<script>" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "La balise <link> avec l'attribut rel='stylesheet' permet de lier un fichier CSS externe."
    },
    {
      id: 1405,
      question: "Pourquoi la balise <head> est-elle importante pour le SEO ?",
      options: { 
        A: "Elle affiche des mots-clés visibles", 
        B: "Les moteurs de recherche utilisent ses métadonnées pour comprendre la page", 
        C: "Elle contient tout le contenu indexable", 
        D: "Elle n'est pas importante pour le SEO" 
      },
      reponse_correcte: "B",
      points: 15,
      difficulte: "moyen",
      explication: "Les moteurs de recherche utilisent les métadonnées du <head> (title, description) pour comprendre et indexer votre contenu."
    },
    {
      id: 1406,
      question: "Quelle balise est utilisée pour définir une icône (favicon) dans l'onglet du navigateur ?",
      options: { A: "<icon>", B: "<favicon>", C: "<link rel='icon'>", D: "<meta icon>" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "La balise <link rel='icon'> permet d'ajouter une icône personnalisée dans l'onglet du navigateur."
    }
  ],
  15: [ 
    {
      id: 1501,
      question: "Que permet de faire la balise <video> en HTML5 ?",
      options: { 
        A: "Jouer uniquement des fichiers audio", 
        B: "Embedder des vidéos sans plug-ins externes", 
        C: "Créer des animations", 
        D: "Afficher des images" 
      },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "La balise <video> permet d'embedder des vidéos directement dans une page HTML sans nécessiter de plug-ins externes comme Flash."
    },
    {
      id: 1502,
      question: "Quel attribut permet d'afficher les contrôles de lecture (play, pause, volume) pour une vidéo ?",
      options: { A: "autoplay", B: "loop", C: "controls", D: "display" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "L'attribut 'controls' affiche les contrôles de lecture natifs du navigateur."
    },
    {
      id: 1503,
      question: "Quels sont les formats de fichiers multimédia les plus couramment supportés sur le web ?",
      options: { 
        A: "MP3 pour l'audio, MP4 pour la vidéo", 
        B: "WAV pour l'audio, AVI pour la vidéo", 
        C: "FLAC pour l'audio, MKV pour la vidéo", 
        D: "OGG pour l'audio, MOV pour la vidéo" 
      },
      reponse_correcte: "A",
      points: 10,
      difficulte: "facile",
      explication: "MP3 pour l'audio et MP4 pour la vidéo sont les formats les plus largement supportés à travers tous les navigateurs modernes."
    },
    {
      id: 1504,
      question: "Comment spécifier plusieurs formats pour une même vidéo afin d'assurer la compatibilité ?",
      options: { 
        A: "Utiliser plusieurs attributs src", 
        B: "Utiliser la balise <source>", 
        C: "Convertir la vidéo en un seul format universel", 
        D: "Utiliser la balise <track>" 
      },
      reponse_correcte: "B",
      points: 15,
      difficulte: "moyen",
      explication: "La balise <source> permet de spécifier plusieurs formats de média. Le navigateur choisit le premier format qu'il supporte."
    },
    {
      id: 1505,
      question: "Quelles étaient les méthodes utilisées avant HTML5 pour intégrer du multimédia ?",
      options: { 
        A: "<video> et <audio>", 
        B: "<source> et <track>", 
        C: "<object> et <embed>", 
        D: "<media> et <content>" 
      },
      reponse_correcte: "C",
      points: 15,
      difficulte: "moyen",
      explication: "Avant HTML5, on utilisait les balises <object> et <embed> avec des plug-ins externes comme Flash ou QuickTime."
    },
    {
      id: 1506,
      question: "Quel attribut de la balise <audio> permet d'ajouter les contrôles de lecture ?",
      options: { A: "play", B: "controls", C: "player", D: "buttons" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "L'attribut 'controls' ajoute les boutons play, pause et le contrôle du volume pour l'audio."
    },
    {
      id: 1507,
      question: "Pourquoi les balises <object> et <embed> sont-elles moins utilisées aujourd'hui ?",
      options: { 
        A: "Elles sont trop complexes à utiliser", 
        B: "HTML5 offre des solutions natives plus simples et plus sûres", 
        C: "Elles ne fonctionnent que sur Windows", 
        D: "Elles sont payantes" 
      },
      reponse_correcte: "B",
      points: 15,
      difficulte: "moyen",
      explication: "HTML5 propose les balises natives <video> et <audio> qui sont plus simples, plus sûres et ne nécessitent pas de plug-ins externes."
    },
    {
      id: 1508,
      question: "Quelle est la meilleure pratique pour l'expérience utilisateur concernant l'autoplay ?",
      options: { 
        A: "Toujours utiliser autoplay pour attirer l'attention", 
        B: "Éviter l'autoplay sauf si essentiel", 
        C: "Forcer l'autoplay avec le son", 
        D: "Utiliser autoplay uniquement sur mobile" 
      },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "Il est recommandé d'éviter l'autoplay car cela peut être intrusif pour l'utilisateur."
    },
    {
      id: 1509,
      question: "Que signifie HTML5 dans le contexte du multimédia ?",
      options: { 
        A: "HyperText Markup Language version 5", 
        B: "High-Tech Media Language 5", 
        C: "Hyper Transfer Media Language 5", 
        D: "Home Text Markup Language 5" 
      },
      reponse_correcte: "A",
      points: 10,
      difficulte: "facile",
      explication: "HTML5 signifie HyperText Markup Language version 5, qui a introduit les balises <video> et <audio> natives."
    },
    {
      id: 1510,
      question: "Quel attribut permet de lancer automatiquement une vidéo dès le chargement de la page ?",
      options: { A: "start", B: "autoplay", C: "auto", D: "play" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "L'attribut 'autoplay' démarre la vidéo automatiquement dès que la page est chargée."
    }
  ],
  16: [ 
    {
      id: 1601,
      question: "Quel est le rôle principal des CSS Media Queries ?",
      options: { 
        A: "Rendre les sites web plus rapides", 
        B: "Adapter les styles CSS à différents appareils et conditions", 
        C: "Créer des animations CSS", 
        D: "Optimiser les images" 
      },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "Les media queries permettent d'adapter les styles CSS en fonction des caractéristiques de l'appareil (taille d'écran, orientation, type d'affichage)."
    },
    {
      id: 1602,
      question: "Quelle est la syntaxe correcte pour une media query ?",
      options: { 
        A: "@media (max-width: 500px) { }", 
        B: "@query (max-width: 500px) { }", 
        C: "@responsive (max-width: 500px) { }", 
        D: "@screen (max-width: 500px) { }" 
      },
      reponse_correcte: "A",
      points: 10,
      difficulte: "facile",
      explication: "La syntaxe correcte utilise @media suivie de la condition entre parenthèses."
    },
    {
      id: 1603,
      question: "Le type d'appareil 'print' est utilisé pour :",
      options: { 
        A: "Les écrans d'ordinateur", 
        B: "Les impressions papier", 
        C: "Les lecteurs d'écran", 
        D: "Tous les appareils" 
      },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "@media print permet d'appliquer des styles spécifiques uniquement lors de l'impression."
    },
    {
      id: 1604,
      question: "Que signifie la condition 'orientation: landscape' ?",
      options: { 
        A: "L'écran est en mode portrait", 
        B: "L'écran est en mode paysage", 
        C: "L'écran est en noir et blanc", 
        D: "L'écran a une résolution élevée" 
      },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "landscape signifie que la largeur de l'écran est supérieure à sa hauteur (mode paysage)."
    },
    {
      id: 1605,
      question: "Comment combiner deux conditions avec un ET logique dans une media query ?",
      options: { 
        A: "@media (condition1) OR (condition2)", 
        B: "@media (condition1, condition2)", 
        C: "@media (condition1) and (condition2)", 
        D: "@media (condition1) && (condition2)" 
      },
      reponse_correcte: "C",
      points: 15,
      difficulte: "moyen",
      explication: "Le mot-clé 'and' permet de combiner plusieurs conditions avec un ET logique."
    },
    {
      id: 1606,
      question: "Quelle media query est la plus courante pour cibler les smartphones ?",
      options: { 
        A: "@media (max-width: 480px)", 
        B: "@media (min-width: 1024px)", 
        C: "@media (orientation: landscape)", 
        D: "@media print" 
      },
      reponse_correcte: "A",
      points: 10,
      difficulte: "facile",
      explication: "max-width: 480px est un breakpoint courant pour cibler les smartphones."
    },
    {
      id: 1607,
      question: "Que signifie 'min-width: 768px' ?",
      options: { 
        A: "Pour les écrans jusqu'à 768px", 
        B: "Pour les écrans de 768px et plus", 
        C: "Pour les écrans exactement à 768px", 
        D: "Pour les écrans inférieurs à 768px" 
      },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "min-width: 768px applique les styles aux écrans ayant une largeur minimale de 768px."
    },
    {
      id: 1608,
      question: "Comment combiner des conditions avec un OU logique dans une media query ?",
      options: { 
        A: "@media (condition1) or (condition2)", 
        B: "@media (condition1) and (condition2)", 
        C: "@media (condition1, condition2)", 
        D: "@media (condition1) || (condition2)" 
      },
      reponse_correcte: "C",
      points: 15,
      difficulte: "moyen",
      explication: "La virgule ',' sert d'opérateur OU dans les media queries."
    },
    {
      id: 1609,
      question: "Pourquoi l'ordre des règles CSS est-il important avec les media queries ?",
      options: { 
        A: "Les media queries n'ont pas besoin d'ordre spécifique", 
        B: "Les règles qui apparaissent plus tard l'emportent sur les précédentes", 
        C: "L'ordre n'a pas d'importance en CSS", 
        D: "Les media queries doivent toujours être en premier" 
      },
      reponse_correcte: "B",
      points: 15,
      difficulte: "moyen",
      explication: "En CSS, les règles définies plus tard l'emportent sur celles définies avant, même dans les media queries."
    },
    {
      id: 1610,
      question: "Quel est l'avantage des media queries pour les sites web modernes ?",
      options: { 
        A: "Elles permettent de créer des animations complexes", 
        B: "Elles sont la base du responsive design", 
        C: "Elles remplacent JavaScript", 
        D: "Elles améliorent uniquement le SEO" 
      },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "Les media queries sont la fondation du responsive design, permettant d'adapter l'affichage sur mobile, tablette et desktop."
    }
  ],
  18: [ 
    {
      id: 1801,
      question: "Quels sont les différents formats pour définir une couleur en CSS ?",
      options: { 
        A: "Uniquement les noms de couleurs", 
        B: "Noms de couleurs, HEX, RGB, HSL", 
        C: "Uniquement HEX et RGB", 
        D: "Uniquement les codes HEX" 
      },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "CSS offre plusieurs formats : les noms de couleurs (red), les codes HEX (#FF0000), RGB (rgb(255,0,0)) et HSL (hsl(0,100%,50%))."
    },
    {
      id: 1802,
      question: "Que signifie le code HEX #FF0000 ?",
      options: { A: "Vert", B: "Bleu", C: "Rouge", D: "Jaune" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "#FF0000 représente le rouge pur (FF = 255 en hexadécimal pour le rouge, 00 pour le vert et le bleu)."
    },
    {
      id: 1803,
      question: "Quelle est la syntaxe correcte pour RGB en CSS ?",
      options: { 
        A: "rgb(0-255, 0-255, 0-255)", 
        B: "rgb(0-100, 0-100, 0-100)", 
        C: "rgb(0-1, 0-1, 0-1)", 
        D: "rgb(0-360, 0-100%, 0-100%)" 
      },
      reponse_correcte: "A",
      points: 10,
      difficulte: "facile",
      explication: "RGB utilise trois valeurs entre 0 et 255 pour représenter l'intensité du rouge, du vert et du bleu."
    },
    {
      id: 1804,
      question: "Que permet d'ajouter RGBA par rapport à RGB ?",
      options: { 
        A: "La luminosité", 
        B: "L'opacité (transparence)", 
        C: "La saturation", 
        D: "La teinte" 
      },
      reponse_correcte: "B",
      points: 15,
      difficulte: "moyen",
      explication: "RGBA ajoute un canal alpha (A) qui contrôle l'opacité, de 0 (transparent) à 1 (opaque)."
    },
    {
      id: 1805,
      question: "Dans HSL, que représente la valeur H (Hue) ?",
      options: { 
        A: "La saturation (0-100%)", 
        B: "La luminosité (0-100%)", 
        C: "La teinte sur le cercle chromatique (0-360°)", 
        D: "La transparence" 
      },
      reponse_correcte: "C",
      points: 15,
      difficulte: "moyen",
      explication: "Hue (teinte) est un angle sur le cercle chromatique : 0° = rouge, 120° = vert, 240° = bleu."
    },
    {
      id: 1806,
      question: "Quelle propriété CSS permet de changer la couleur du texte ?",
      options: { A: "text-color", B: "font-color", C: "color", D: "background-color" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "La propriété 'color' définit la couleur du texte en CSS."
    },
    {
      id: 1807,
      question: "Comment écrire le code HEX pour la couleur blanche ?",
      options: { A: "#000000", B: "#FFFFFF", C: "#FF0000", D: "#00FF00" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "#FFFFFF (ou blanc) représente la valeur maximale pour le rouge, le vert et le bleu."
    },
    {
      id: 1808,
      question: "Quelle est la valeur minimale pour un canal RGB ?",
      options: { A: "1", B: "0", C: "50", D: "100" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "Dans RGB, chaque valeur peut aller de 0 (absence de couleur) à 255 (pleine intensité)."
    },
    {
      id: 1809,
      question: "Que signifie HSL ?",
      options: { 
        A: "High Saturation Light", 
        B: "Hue, Saturation, Lightness", 
        C: "Hex, Saturation, Lightness", 
        D: "Hue, Saturation, Luminance" 
      },
      reponse_correcte: "B",
      points: 10,
      difficulte: "moyen",
      explication: "HSL signifie Hue (teinte), Saturation (saturation), Lightness (luminosité)."
    },
    {
      id: 1810,
      question: "Pourquoi est-il important d'avoir un bon contraste entre texte et arrière-plan ?",
      options: { 
        A: "Pour que le site soit plus beau", 
        B: "Pour l'accessibilité des utilisateurs malvoyants", 
        C: "Pour le référencement SEO", 
        D: "Pour accélérer le chargement" 
      },
      reponse_correcte: "B",
      points: 15,
      difficulte: "moyen",
      explication: "Un bon contraste améliore la lisibilité pour tous, en particulier pour les personnes malvoyantes ou daltoniennes."
    }
  ]
    };

    return questionsMap[courseId] || [];
  }, []);

  
  const loadQuestions = useCallback(async (courseId: number) => {
    try {
      setLoadingQuestions(true);
      const response = await api.get(`/courses/${courseId}/questions?mode=audio`);
      const questionsData = response.data;
      
      if (questionsData && questionsData.length > 0) {
        const formattedQuestions = questionsData.map((q: any) => ({
          id: q.id,
          question: q.question,
          options: q.options || {},
          reponse_correcte: q.reponse_correcte,
          points: q.points || 10,
          difficulte: q.difficulte || 'moyen',
          explication: q.explication
        }));
        setQuestions(formattedQuestions);
      } else {
        const defaultQuestions = getDefaultQuestionsForCourse(courseId);
        setQuestions(defaultQuestions);
      }
    } catch (error) {
      console.error('Erreur chargement questions:', error);
      const defaultQuestions = getDefaultQuestionsForCourse(courseId);
      setQuestions(defaultQuestions);
    } finally {
      setLoadingQuestions(false);
    }
  }, [getDefaultQuestionsForCourse]);

  
  useEffect(() => {
    const loadCourses = async () => {
      try {
        setLoading(true);
        const allCourses = await courseService.getAllCourses();
        setCourses(allCourses);
        
        
        await loadAudioFiles();
      } catch (error) {
        console.error('Erreur chargement cours:', error);
      } finally {
        setLoading(false);
      }
    };
    
    loadCourses();
    const savedNotes = localStorage.getItem('audio_notes');
    if (savedNotes) setNotes(savedNotes);
  }, []);

  
  useEffect(() => {
    if (selectedCourse && currentAudioFile) {
      const content = getAudioContentForCourse(selectedCourse, currentAudioFile);
      setAudioContent(content);
    }
  }, [selectedCourse, currentAudioFile, getAudioContentForCourse]);

  
  useEffect(() => {
    if (courses.length > 0 && currentAudioFile) {
      
      const courseMapping: Record<string, number> = {
        'html_basics.mp3': 6,
        'html_liens.mp3': 11,
        'html_img.mp3': 12,
        'html_formulaires.mp3': 8,
        'html_semantique.mp3': 9,
        'html_mise_en_page_flexBox_grid.mp3': 10,
        'html_tableau.mp3': 13,
        'html_head.mp3': 14,
        'html_multimedia.mp3': 15,
        'html_responsive_media.mp3': 16,
        'html_css_selectors.mp3': 17,
        'html_css_colors.mp3': 18,
        'html_css_background.mp3': 19,
        'html_css_border.mp3': 20,
        'html_css_margin.mp3': 22,   
        'html_css_padding.mp3': 23,
        'html_css_text.mp3': 24,
        'html_css_fonts.mp3': 25,
        'html_css_links.mp3': 26,
        'html_css_lists.mp3': 27,
        'html_css_tables.mp3': 28,
        'html_css_display_visibility.mp3': 29,
        'html_css_positioning.mp3': 30,
        'html_css_overflow.mp3': 31,
        'html_css_float.mp3': 32,
        'html_js_introduction.mp3': 33,
        'html_js_variables.mp3': 34,
        'html_js_datatypes.mp3': 35,
        'html_js_operators.mp3': 36,
        'html_js_if_conditions.mp3': 37,
        'html_js_loops.mp3': 38,
        'html_js_strings_methods.mp3': 39,
        'html_js_numbers_methods.mp3': 40,
        'html_js_functions.mp3': 41,
        'html_js_objects.mp3': 42,
        'html_js_arrays.mp3': 43,
        'html_js_sets.mp3': 44,
        'html_js_maps.mp3': 45,
        'html_js_math_objects.mp3': 46,
        'html_js_regex.mp3': 47,
        'html_js_events.mp3': 48
      };
      
      const courseId = courseMapping[currentAudioFile];
      if (courseId) {
        const course = courses.find(c => c.id === courseId);
        if (course) {
          setSelectedCourse(course);
        } else if (courses.length > 0) {
          setSelectedCourse(courses[0]);
        }
      } else if (courses.length > 0) {
        setSelectedCourse(courses[0]);
      }
    }
  }, [currentAudioFile, courses]);


useEffect(() => {
  if (selectedCourse && selectedCourse.id) {
    loadQuestions(selectedCourse.id);
    
    if (user?.id) {
      loadMistakesFromDB(user.id, selectedCourse.id);
    }
  }
}, [selectedCourse, loadQuestions, user?.id]);

  
  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const handleTimeUpdate = () => setCurrentTime(audio.currentTime);
    const handleLoadedMetadata = () => setDuration(audio.duration);
    const handleError = () => setAudioError(`Impossible de charger le fichier audio: ${currentAudioFile}`);

    audio.addEventListener('timeupdate', handleTimeUpdate);
    audio.addEventListener('loadedmetadata', handleLoadedMetadata);
    audio.addEventListener('error', handleError);

    return () => {
      audio.removeEventListener('timeupdate', handleTimeUpdate);
      audio.removeEventListener('loadedmetadata', handleLoadedMetadata);
      audio.removeEventListener('error', handleError);
    };
  }, [currentAudioFile]);

  const handleAudioFileChange = (file: string) => {
    setCurrentAudioFile(file);
    setAudioError(null);
    setCurrentTime(0);
    setDuration(0);
    setQuizSubmitted(false);
    setUserAnswers({});
    setQuizScore(0);
  };

  const seekToTime = (timeInSeconds: number) => {
    if (audioRef.current) {
      audioRef.current.currentTime = timeInSeconds;
      audioRef.current.play();
    }
  };

  const formatTime = (time: number) => {
    if (isNaN(time) || !isFinite(time)) return '0:00';
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  const saveNotes = () => {
    localStorage.setItem('audio_notes', notes);
    alert('Notes sauvegardées !');
  };

  const handleAnswerSelect = (questionId: number, answer: string) => {
    setUserAnswers(prev => ({ ...prev, [questionId]: answer }));
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
  const responses = [];
  const wrongQuestionsList: { question: string; questionId: number }[] = [];

  for (const q of questions) {
    maxScore += q.points;
    const userAnswer = userAnswers[q.id];
    const isCorrect = userAnswer === q.reponse_correcte;
    if (isCorrect) {
      totalScore += q.points;
    } else {
      wrongQuestionsList.push({ 
        question: q.question, 
        questionId: q.id 
      });
      console.log('❌ Erreur enregistrée:', q.question);
    }
    
    responses.push({
      question_id: q.id,
      reponse_utilisateur: userAnswer || '',
      est_correcte: isCorrect,
      temps_reponse: 30
    });
  }

  console.log('📝 Total des erreurs:', wrongQuestionsList.length);

  
  if (wrongQuestionsList.length > 0) {
    await saveMistakesToDB(user.id, selectedCourse.id, wrongQuestionsList);
    await loadMistakesFromDB(user.id, selectedCourse.id);
    
    
    const wrongQuestionTexts = wrongQuestionsList.map(w => w.question);
    await analyzeMistakesAndRecommend(wrongQuestionTexts);
  }

  const percentage = (totalScore / maxScore) * 100;
  const isSuccess = percentage >= 70;
  const timeSpent = Math.max(Math.floor(currentTime), 1);
  const completionRate = duration > 0 ? (currentTime / duration) * 100 : 100;

  const resultData = {
    utilisateur_id: user.id,
    cours_id: Number(selectedCourse.id),
    mode: 'audio',
    score_quiz: Number(percentage.toFixed(2)),
    temps_passe: timeSpent,
    taux_completion: Number(completionRate.toFixed(2)),
    est_reussi: isSuccess,
    feedback: isSuccess 
      ? `Félicitations ! Score: ${percentage.toFixed(1)}%` 
      : `Continuez à pratiquer. Score: ${percentage.toFixed(1)}%`
  };

  try {
    const resultResponse = await api.post('/results', resultData);
    const resultId = resultResponse.data.id;
    setQuizResultId(resultId);

    for (const response of responses) {
      await api.post('/reponses', {
        resultat_id: resultId,
        question_id: response.question_id,
        reponse_utilisateur: response.reponse_utilisateur,
        est_correcte: response.est_correcte,
        temps_reponse: response.temps_reponse
      });
    }

    setQuizScore(percentage);
    setQuizSubmitted(true);
    
    const correctCount = responses.filter(r => r.est_correcte).length;
    
    
    let successMessage = `✅ Quiz soumis avec succès !\nScore: ${percentage.toFixed(1)}%\nRéponses correctes: ${correctCount}/${responses.length}`;
    if (wrongQuestionsList.length > 0) {
      successMessage += `\n\n🤖 Tuteur IA: Analyse de vos ${wrongQuestionsList.length} erreur(s) en cours...\nLes recommandations apparaîtront sous le quiz.`;
    }
    alert(successMessage);
  } catch (error: any) {
    console.error('❌ Erreur:', error);
    alert(`Erreur: ${error.response?.data?.detail || 'Erreur inconnue'}`);
  }
};

  const resetQuiz = () => {
    setUserAnswers({});
    setQuizSubmitted(false);
    setQuizScore(0);
    setQuizResultId(null);
    setShowExplanation({});
  };

  if (loading || loadingAudio) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="text-4xl mb-4">🎧</div>
          <div className="text-xl text-gray-600">Chargement des cours audio...</div>
        </div>
      </div>
    );
  }

  const progress = duration > 0 ? (currentTime / duration) * 100 : 0;
  const displayContent = audioContent || {
    title: 'Cours HTML',
    description: 'Apprenez les bases du HTML',
    chapters: [],
    transcript: [],
    audioFile: currentAudioFile
  };

  return (
  <div className="flex min-h-screen bg-gray-100">
    
    <aside 
      className={`fixed left-0 top-0 h-full bg-white shadow-xl z-30 transition-all duration-300 ${
        sidebarOpen ? 'w-80' : 'w-16'
      } overflow-y-auto`}
    >
      
      <div className="sticky top-0 bg-white border-b p-4">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 rounded-lg hover:bg-gray-100 transition"
          >
            {sidebarOpen ? '◀' : '▶'}
          </button>
          {sidebarOpen && <h2 className="text-lg font-bold text-gray-800">🎵 Cours audio</h2>}
        </div>
      </div>

      {sidebarOpen && (
        <div className="p-5">
          
          <div className="mb-4">
            <input
              type="text"
              placeholder="🔍 Rechercher un cours..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 text-sm"
            />
          </div>

          
          <nav className="space-y-1 max-h-[calc(100vh-200px)] overflow-y-auto">
            {filteredCourses.map((course) => {
              const audioFile = audioFiles.find(f => 
                f.name.includes(course.titre.toLowerCase().replace(/ /g, '_')) || 
                (course.id === 6 && f.name === 'html_basics.mp3') ||
                (course.id === 11 && f.name === 'html_liens.mp3') ||
                (course.id === 12 && f.name === 'html_img.mp3') ||
                (course.id === 8 && f.name === 'html_formulaires.mp3') ||
                (course.id === 9 && f.name === 'html_semantique.mp3') ||
                (course.id === 10 && f.name === 'html_mise_en_page_flexBox_grid.mp3') ||
                (course.id === 13 && f.name === 'html_tableau.mp3') ||
                (course.id === 14 && f.name === 'html_head.mp3') ||
                (course.id === 15 && f.name === 'html_multimedia.mp3') ||
                (course.id === 16 && f.name === 'html_responsive_media.mp3') ||
                (course.id === 17 && f.name === 'html_css_selectors.mp3') ||
                (course.id === 18 && f.name === 'html_css_colors.mp3') ||
                (course.id === 19 && f.name === 'html_css_background.mp3') ||
                (course.id === 20 && f.name === 'html_css_border.mp3') ||
                (course.id === 22 && f.name === 'html_css_margin.mp3') ||
                (course.id === 23 && f.name === 'html_css_padding.mp3') ||
                (course.id === 24 && f.name === 'html_css_text.mp3') ||
                (course.id === 25 && f.name === 'html_css_fonts.mp3') ||
                (course.id === 26 && f.name === 'html_css_links.mp3') ||
                (course.id === 27 && f.name === 'html_css_lists.mp3') ||
                (course.id === 28 && f.name === 'html_css_tables.mp3') ||
                (course.id === 29 && f.name === 'html_css_display_visibility.mp3') ||
                (course.id === 30 && f.name === 'html_css_positioning.mp3') ||
                (course.id === 31 && f.name === 'html_css_overflow.mp3') ||
                (course.id === 32 && f.name === 'html_css_float.mp3') ||
                (course.id === 33 && f.name === 'html_js_introduction.mp3') ||
                (course.id === 34 && f.name === 'html_js_variables.mp3') ||
                (course.id === 35 && f.name === 'html_js_datatypes.mp3') ||
                (course.id === 36 && f.name === 'html_js_operators.mp3') ||
                (course.id === 37 && f.name === 'html_js_if_conditions.mp3') ||
                (course.id === 38 && f.name === 'html_js_loops.mp3') ||
                (course.id === 39 && f.name === 'html_js_strings_methods.mp3') ||
                (course.id === 40 && f.name === 'html_js_numbers_methods.mp3') ||
                (course.id === 41 && f.name === 'html_js_functions.mp3') ||
                (course.id === 42 && f.name === 'html_js_objects.mp3') ||
                (course.id === 43 && f.name === 'html_js_arrays.mp3') ||
                (course.id === 44 && f.name === 'html_js_sets.mp3') ||
                (course.id === 45 && f.name === 'html_js_maps.mp3') ||
                (course.id === 46 && f.name === 'html_js_math_objects.mp3') ||
                (course.id === 47 && f.name === 'html_js_regex.mp3') ||
                (course.id === 48 && f.name === 'html_js_events.mp3')
              );
              
              const isSelected = selectedCourse?.id === course.id;
              let courseIcon = '🎵';
              if (course.id === 6) courseIcon = '📝';
              else if (course.id === 11) courseIcon = '🔗';
              else if (course.id === 12) courseIcon = '🖼️';
              else if (course.id === 8) courseIcon = '📝';
              else if (course.id === 9) courseIcon = '🏗️';
              else if (course.id === 10) courseIcon = '🎨';
              else if (course.id >= 17 && course.id <= 32) courseIcon = '🎨';
              else if (course.id >= 33 && course.id <= 48) courseIcon = '🚀';
              
              return (
                <button
                  key={course.id}
                  onClick={() => {
                    if (audioFile) {
                      handleAudioFileChange(audioFile.name);
                    } else if (audioFiles.length > 0) {
                      handleAudioFileChange(audioFiles[0].name);
                    }
                    setSelectedCourse(course);
                  }}
                  className={`w-full text-left p-3 rounded-lg transition-all duration-200 ${
                    isSelected 
                      ? 'bg-green-50 border-l-4 border-green-500 text-green-700' 
                      : 'hover:bg-gray-50 text-gray-700'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <span className="text-xl">{courseIcon}</span>
                    <div className="flex-1">
                      <p className="font-medium text-sm">{course.titre}</p>
                      <p className="text-xs text-gray-500 mt-0.5">
                        {course.difficulte || 'Débutant'} • {course.duree || 15} min
                      </p>
                    </div>
                    {isSelected && <span className="text-green-500 text-xs">▶</span>}
                  </div>
                </button>
              );
            })}
          </nav>

          
          <div className="mt-6 pt-4 border-t border-gray-100 space-y-2">
            <button
              onClick={generatePersonalizedQuiz}
              disabled={generatingQuiz || !selectedCourse}
              className="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition disabled:opacity-50 text-sm"
            >
              {generatingQuiz ? '⏳ Génération...' : '🎯 Quiz Personnalisé'}
            </button>
            <button
              onClick={generateBertQuiz}
              disabled={generatingQuiz || !selectedCourse}
              className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50 text-sm"
            >
              {generatingQuiz ? '⏳ Génération...' : '🤖 Quiz IA'}
            </button>
            {!examMode ? (
    <button
      onClick={generateFinalExam}
      disabled={generatingExam || !selectedCourse}
      className="w-full px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition disabled:opacity-50 text-sm mt-2"
    >
      {generatingExam ? '⏳ Génération...' : '📝 Examen Final IA'}
    </button>
  ) : (
    <button
      onClick={cancelExam}
      className="w-full px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition text-sm mt-2"
    >
      ❌ Annuler l'examen
    </button>
  )}

   
  <button
    onClick={async () => {
      if (mistakeQuestions.length > 0) {
        await analyzeMistakesAndRecommend(mistakeQuestions);
      } else {
        alert('Aucune erreur enregistrée pour ce cours');
      }
    }}
    disabled={mistakeQuestions.length === 0}
    className="w-full px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition disabled:opacity-50 text-sm mt-2"
  >
    🤖 Tuteur IA - Recommandations
  </button>


  <button
  onClick={showMistakeStats}
  className="w-full px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition text-sm mt-2"
>
  📊 Voir mes statistiques d'erreurs
</button>

            {mistakeQuestions.length > 0 && (
              <div className="text-center text-xs text-orange-600 bg-orange-50 p-2 rounded-lg mt-2">
                📝 {mistakeQuestions.length} erreur(s) enregistrée(s)
              </div>
              
            )}
            {quizGenerationMode === 'personalized' && (
              <div className="text-center text-xs text-green-600 bg-green-50 p-2 rounded-lg">
                🎯 Mode personnalisé
              </div>
            )}
            {quizGenerationMode === 'bert' && (
              <div className="text-center text-xs text-blue-600 bg-blue-50 p-2 rounded-lg">
                🤖 Mode IA
              </div>
            )}
          </div>
        </div>
        
      )}

     
    </aside>

   <main className={`flex-1 transition-all duration-300 ${sidebarOpen ? 'ml-80' : 'ml-16'}`}>
      
      
      {examMode ? (
        <div className="max-w-4xl mx-auto py-8 px-6 space-y-8">
          
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
              <div className="bg-white rounded-xl shadow-md p-8 text-center">
                <div className="text-6xl mb-4">{examResult.passed ? '🎓' : '📚'}</div>
                <h2 className="text-2xl font-bold mb-2">Résultat de l'examen</h2>
                <p className="text-5xl font-bold text-purple-600 mb-2">{examResult.percentage.toFixed(1)}%</p>
                <p className="mb-4">
                  {examResult.passed 
                    ? '✅ Félicitations ! Vous avez réussi l\'examen.' 
                    : '⚠️ Vous n\'avez pas atteint le seuil de réussite (70%).'}
                </p>
                <p className="text-gray-500">Score: {examResult.score} / {examResult.total} points</p>
              </div>

              {examResult.answers.filter((a: any) => !a.isCorrect).length > 0 && (
                <div className="bg-yellow-50 rounded-xl shadow-md p-6">
                  <h3 className="text-xl font-bold text-yellow-800 mb-4">
                    📊 Analyse des erreurs ({examResult.answers.filter((a: any) => !a.isCorrect).length})
                  </h3>
                  <div className="space-y-3 max-h-96 overflow-y-auto">
                    {examResult.answers.filter((a: any) => !a.isCorrect).map((answer: any, idx: number) => (
                      <div key={idx} className="border-b border-yellow-200 pb-3">
                        <p className="font-semibold">❌ {answer.questionText}</p>
                        <p className="text-sm">Votre réponse: <span className="font-mono">{answer.selectedAnswer}</span></p>
                        <p className="text-sm">Bonne réponse: <span className="font-mono text-green-600">{answer.correctAnswer}</span></p>
                        {answer.explanation && (
                          <p className="text-xs text-gray-600 mt-1">💡 {answer.explanation}</p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="flex gap-3">
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
                    generateFinalExam();
                  }}
                  className="flex-1 px-6 py-3 bg-purple-600 text-white rounded-lg font-semibold hover:bg-purple-700 transition"
                >
                  🔁 Recommencer l'examen
                </button>
              </div>
            </div>
          ) : (
            
            <div className="bg-white rounded-xl shadow-md p-8">
              <div className="mb-6 pb-4 border-b">
                <p className="text-gray-600">L'examen contient <strong>{examQuestions.length}</strong> questions</p>
                <p className="text-sm text-gray-500 mt-1">Score minimum requis: <strong className="text-purple-600">70%</strong></p>
              </div>
              
              <div className="space-y-6 max-h-[60vh] overflow-y-auto pr-2">
                {examQuestions.map((q, idx) => (
                  <div key={q.id} className="border rounded-lg p-4 hover:shadow-md transition">
                    <p className="font-semibold mb-3">
                      Question {idx + 1} <span className="text-sm text-gray-500">({q.points} points - {q.difficulte})</span>
                    </p>
                    <p className="mb-4">{q.question}</p>
                    <div className="space-y-2 ml-4">
                      {Object.entries(q.options).map(([key, value]) => (
                        <label key={key} className="flex items-center gap-3 cursor-pointer hover:bg-gray-50 p-2 rounded">
                          <input
                            type="radio"
                            name={`exam_question_${q.id}`}
                            value={key}
                            checked={examAnswers[q.id] === key}
                            onChange={() => setExamAnswers(prev => ({ ...prev, [q.id]: key }))}
                            className="w-4 h-4 text-purple-600"
                          />
                          <span className="text-sm">{key}: {value}</span>
                        </label>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
              
              <button
                onClick={submitExam}
                disabled={Object.keys(examAnswers).length !== examQuestions.length}
                className="w-full mt-6 px-6 py-3 bg-purple-600 text-white rounded-lg font-semibold hover:bg-purple-700 transition disabled:opacity-50"
              >
                📤 Soumettre l'examen
              </button>
              
              {Object.keys(examAnswers).length !== examQuestions.length && (
                <p className="text-sm text-yellow-600 mt-3 text-center">
                  ⚠️ {Object.keys(examAnswers).length}/{examQuestions.length} questions répondues
                </p>
              )}
            </div>
          )}
        </div>
      ) : (
        
        <div className="max-w-6xl mx-auto py-8 px-6 space-y-8">
          
          <div className="bg-gradient-to-r from-green-500 to-green-700 rounded-2xl p-6 text-white">
            <h1 className="text-3xl font-bold mb-2">🔊 Apprentissage par Audio</h1>
            <p className="opacity-90">Apprenez HTML à travers des leçons audio interactives</p>
          </div>

          
          <div className="bg-white rounded-xl shadow-md p-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">🎵 Sélectionner une leçon audio</label>
            <select
              value={currentAudioFile}
              onChange={(e) => handleAudioFileChange(e.target.value)}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-green-500"
            >
              {audioFiles.map(audio => {
                const nameMapping: Record<string, string> = {
                  'html_basics': '📖 Formatage du Texte en HTML',
                  'html_liens': '🔗 Les Liens Hypertextes en HTML',
                  'html_img': '🖼️ Images en HTML',
                  'html_formulaires': '📝 Formulaires HTML Avancés',
                  'html_semantique': '🏗️ HTML5 Sémantique - Structures Modernes',
                  'html_mise_en_page_flexBox_grid': '🎨 CSS - Flexbox & Grid (Mise en Page Avancée)',
                  'html_tableau': '📊 Les Tableaux en HTML',
                  'html_head': '🧩 HTML Head - Métadonnées & SEO',
                  'html_multimedia': '🎬 HTML Multimédia - Vidéo & Audio',
                  'html_responsive_media': '📱 CSS Media Queries - Responsive Design',
                  'html_css_selectors': '🎯 CSS - Sélecteurs Simples (Element, ID, Class)',
                  'html_css_colors': '🎨 CSS - Couleurs (Noms, HEX, RGB, HSL)',
                  'html_css_background': '🖼️ CSS - Images d\'Arrière-plan (Background)',
                  'html_css_border': '🖼️ CSS - Bordures (Border)',
                  'html_css_margin': '📐 CSS - Marges (Margin)',
                  'html_css_padding': '📦 CSS - Padding (Remplissage)',
                  'html_css_text': '📝 CSS - Propriétés du Texte (Text)',
                  'html_css_fonts': '🔤 CSS - Propriétés des Polices (Font)',
                  'html_css_links': '🔗 CSS - Styliser les Liens (Links)',
                  'html_css_lists': '📋 CSS - Styliser les Listes (Lists)',
                  'html_css_tables': '📊 CSS - Styliser les Tableaux (Tables)',
                  'html_css_display_visibility': '👁️ CSS - Display & Visibility',
                  'html_css_positioning': '📍 CSS - Positionnement (Positioning)',
                  'html_css_overflow': '📦 CSS - Overflow (Dépassement)',
                  'html_css_float': '🌊 CSS - Float (Flottement)',
                  'html_js_introduction': '🚀 JavaScript - Introduction',
                  'html_js_variables': '📦 JavaScript - Variables',
                  'html_js_datatypes': '🔢 JavaScript - Types de Données',
                  'html_js_operators': '➕ JavaScript - Opérateurs',
                  'html_js_if_conditions': '🤔 JavaScript - Conditions (If/Else)',
                  'html_js_loops': '🔄 JavaScript - Boucles (Loops)',
                  'html_js_strings_methods': '📝 JavaScript - Chaînes (Strings)',
                  'html_js_numbers_methods': '🔢 JavaScript - Nombres (Numbers)',
                  'html_js_functions': '🎯 JavaScript - Fonctions (Functions)',
                  'html_js_objects': '🧍 JavaScript - Objets (Objects)',
                  'html_js_arrays': '🗃️ JavaScript - Tableaux (Arrays)',
                  'html_js_sets': '🔢 JavaScript - Sets (Ensembles)',
                  'html_js_maps': '🗺️ JavaScript - Maps (Dictionnaires)',
                  'html_js_math_objects': '🧮 JavaScript - Math (Objets Mathématiques)',
                  'html_js_regex': '🔍 JavaScript - Regex (Expressions Régulières)',
                  'html_js_events': '🎯 JavaScript - Events (Handlers vs Listeners)'
                };
                
                const displayName = nameMapping[audio.name.replace('.mp3', '')] || audio.name.replace('.mp3', '').replace(/_/g, ' ');
                
                return <option key={audio.name} value={audio.name}>{displayName}</option>;
              })}
            </select>
            
            {selectedCourse && (
              <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                <h2 className="text-xl font-bold text-gray-800">{displayContent.title}</h2>
                <p className="text-gray-600 mt-1">{displayContent.description}</p>
                <div className="flex gap-4 mt-2">
                  <span className="text-sm text-gray-500">📊 Niveau: {selectedCourse.difficulte || 'Débutant'}</span>
                  <span className="text-sm text-gray-500">🎵 Fichier: {currentAudioFile}</span>
                </div>
              </div>
            )}
          </div>

          
          <div className="bg-white rounded-xl shadow-lg p-8">
            <h3 className="text-xl font-bold mb-4">🎵 Lecteur Audio - {displayContent.title}</h3>

            {audioError && (
              <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-lg border border-red-300">
                <strong>⚠️ Erreur:</strong> {audioError}
              </div>
            )}

            <audio
              ref={audioRef}
              src={`${AUDIO_BASE_URL}/${currentAudioFile}`}
              controls
              className="w-full"
              preload="auto"
            />

            <div className="mt-4">
              <div className="flex justify-between text-sm text-gray-600 mb-1">
                <span>{formatTime(currentTime)}</span>
                <span>{formatTime(duration)}</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-green-500 h-2 rounded-full transition-all" style={{ width: `${progress}%` }} />
              </div>
            </div>

            <div className="text-center text-sm text-gray-500 mt-2">
              Progression: {Math.floor(progress)}%
            </div>
          </div>

          
          {displayContent.chapters.length > 0 && (
            <div className="bg-white rounded-xl shadow-md p-6">
              <h3 className="text-xl font-bold mb-4">📋 Chapitres</h3>
              <div className="space-y-2">
                {displayContent.chapters.map((chapter, idx) => (
                  <div
                    key={idx}
                    onClick={() => seekToTime(chapter.time)}
                    className={`flex items-center p-3 rounded-lg cursor-pointer transition ${
                      currentTime >= chapter.time && (!displayContent.chapters[idx + 1] || currentTime < displayContent.chapters[idx + 1].time)
                        ? 'bg-green-50 border-l-4 border-green-500'
                        : 'hover:bg-gray-50'
                    }`}
                  >
                    <div className="min-w-[60px] font-bold text-green-600">{chapter.timeStr}</div>
                    <div className="flex-1 ml-4">{chapter.title}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          
          {displayContent.transcript.length > 0 && (
            <div className="bg-white rounded-xl shadow-md p-6">
              <h3 className="text-xl font-bold mb-4">📝 Transcription</h3>
              <div className="bg-gray-50 rounded-lg p-4 max-h-[400px] overflow-y-auto">
                {displayContent.transcript.map((segment, idx) => (
                  <div
                    key={idx}
                    onClick={() => seekToTime(segment.time)}
                    className={`p-3 rounded-lg cursor-pointer transition mb-2 ${
                      Math.abs(currentTime - segment.time) < 5
                        ? 'bg-yellow-50 border-l-4 border-yellow-500'
                        : 'hover:bg-gray-100'
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <span className="min-w-[60px] font-medium text-green-600">{segment.timeStr}</span>
                      <p className="flex-1 text-gray-700">{segment.text}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          
          <div className="bg-white rounded-xl shadow-md p-6">
            <h3 className="text-xl font-bold mb-4">🎤 Prendre des notes</h3>
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Écrivez vos notes importantes ici..."
                  className="w-full h-40 p-3 border rounded-lg resize-none focus:ring-2 focus:ring-green-500"
                />
                <button onClick={saveNotes} className="mt-2 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600">
                  💾 Sauvegarder les notes
                </button>
              </div>
              <div className="bg-purple-50 rounded-lg p-4">
                <h4 className="font-semibold text-purple-800 mb-2">🎙️ Note vocale</h4>
                <p className="text-sm text-purple-700 mb-3">Fonctionnalité d'enregistrement vocal à venir.</p>
              </div>
            </div>
          </div>

         
          <div className="bg-gradient-to-r from-purple-500 to-purple-700 rounded-xl p-8 text-white">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-2xl font-bold">🎯 Quiz - {displayContent.title}</h3>
              {quizGenerationMode === 'personalized' && <span className="text-xs bg-green-500 px-3 py-1 rounded-full">Personnalisé</span>}
              {quizGenerationMode === 'bert' && <span className="text-xs bg-blue-500 px-3 py-1 rounded-full">Généré par IA</span>}
            </div>
            <p className="mb-6">Testez vos connaissances sur {displayContent.title}</p>

            
            <div className="flex gap-3 mb-6">
              <button
                onClick={generatePersonalizedQuiz}
                disabled={generatingQuiz || !selectedCourse}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition disabled:opacity-50"
              >
                {generatingQuiz ? '⏳...' : '🎯 Quiz Personnalisé'}
              </button>
              <button
                onClick={generateBertQuiz}
                disabled={generatingQuiz || !selectedCourse}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
              >
                {generatingQuiz ? '⏳...' : '🤖 Quiz IA'}
              </button>
            </div>

            
            {mistakeQuestions.length > 0 && !quizSubmitted && (
              <div className="mb-4 p-2 bg-yellow-500/30 rounded-lg text-center">
                <span className="text-sm">📝 {mistakeQuestions.length} erreur(s) enregistrée(s) pour ce cours</span>
              </div>
            )}

            {loadingQuestions ? (
              <div className="text-center py-8">Chargement des questions...</div>
            ) : questions && questions.length > 0 ? (
              !quizSubmitted ? (
                <>
                  {questions.map((q, idx) => (
                    <div key={q.id} className="bg-white/10 rounded-lg p-4 mb-4">
                      <p className="font-semibold mb-3">Question {idx + 1}: {q.question}</p>
                      <div className="space-y-2 ml-4">
                        {Object.entries(q.options).map(([key, value]) => (
                          <label key={key} className="flex items-center gap-3 cursor-pointer">
                            <input
                              type="radio"
                              name={`question_${q.id}`}
                              value={key}
                              checked={userAnswers[q.id] === key}
                              onChange={() => setUserAnswers(prev => ({ ...prev, [q.id]: key }))}
                              className="w-4 h-4"
                            />
                            <span>{key}: {value}</span>
                          </label>
                        ))}
                      </div>
                    </div>
                  ))}
                  <button
                    onClick={handleSubmitQuiz}
                    disabled={Object.keys(userAnswers).length !== questions.length || !isAuthenticated}
                    className="w-full mt-4 px-6 py-3 bg-white text-purple-600 rounded-lg font-semibold hover:bg-gray-100 transition disabled:opacity-50"
                  >
                    📤 Soumettre le quiz
                  </button>
                  {!isAuthenticated && (
                    <p className="text-sm text-yellow-200 mt-2 text-center">
                      ⚠️ Connectez-vous pour soumettre le quiz et sauvegarder votre progression
                    </p>
                  )}
                </>
              ) : (
                <div className="bg-white/10 rounded-lg p-6 text-center">
                  <div className="text-4xl mb-2">📊</div>
                  <p className="text-2xl font-bold mb-2">
                    Score: {quizScore} / {questions.length}
                  </p>
                  <p className="text-lg mb-4">
                    Pourcentage: {((quizScore / questions.length) * 100).toFixed(1)}%
                  </p>
                  <button
                    onClick={() => {
                      setQuizSubmitted(false);
                      setUserAnswers({});
                    }}
                    className="px-4 py-2 bg-white text-purple-600 rounded-lg hover:bg-gray-100"
                  >
                    🔄 Recommencer le quiz
                  </button>
                </div>
              )
            ) : (
              <div className="text-center py-8 bg-white/10 rounded-lg">
                <p>Aucune question disponible pour ce cours.</p>
                <div className="flex gap-3 justify-center mt-4">
                  <button onClick={generateBertQuiz} disabled={generatingQuiz} className="px-4 py-2 bg-blue-500 rounded-lg hover:bg-blue-600">
                    🤖 Générer quiz IA
                  </button>
                  <button onClick={generatePersonalizedQuiz} disabled={generatingQuiz} className="px-4 py-2 bg-green-500 rounded-lg hover:bg-green-600">
                    🎯 Quiz personnalisé
                  </button>
                </div>
              </div>
            )}
          </div>

          
{showRecommendations && (
  <div className="bg-gradient-to-r from-indigo-500 to-purple-600 rounded-xl p-6 text-white">
    <div className="flex items-center justify-between mb-4">
      <div className="flex items-center gap-3">
        <div className="text-3xl">🤖</div>
        <div>
          <h3 className="text-xl font-bold">Tuteur IA</h3>
          <p className="text-sm opacity-90">Recommandations personnalisées basées sur vos erreurs</p>
        </div>
      </div>
      <button
        onClick={() => setShowRecommendations(false)}
        className="text-white/70 hover:text-white transition"
      >
        ✕
      </button>
    </div>
    
    {loadingRecommendations ? (
      <div className="flex items-center justify-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
        <span className="ml-3">Analyse de vos résultats en cours...</span>
      </div>
    ) : recommendations.length > 0 ? (
      <div className="space-y-3">
        <p className="text-sm mb-2">
          🎯 Basé sur vos erreurs, voici les cours recommandés par notre IA :
        </p>
        {recommendations.map((rec, idx) => (
          <div 
            key={idx}
            onClick={() => navigateToRecommendedCourse(rec.cours_id)}
            className="bg-white/10 rounded-lg p-4 cursor-pointer hover:bg-white/20 transition-all duration-200 group"
          >
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <span className="text-xl">
                    {rec.direct_match ? '🎯' : '📚'}
                  </span>
                  <h4 className="font-semibold group-hover:underline">
                    {rec.cours_titre}
                  </h4>
                </div>
                <p className="text-sm opacity-80 mt-1">{rec.description}</p>
                {rec.nb_erreurs > 0 && (
                  <div className="flex items-center gap-2 mt-2">
                    <span className="text-xs bg-yellow-500/30 px-2 py-0.5 rounded-full">
                      🔴 {rec.nb_erreurs} erreur(s) liée(s)
                    </span>
                    <span className="text-xs bg-green-500/30 px-2 py-0.5 rounded-full">
                      Score de pertinence: {(rec.score * 100).toFixed(0)}%
                    </span>
                  </div>
                )}
              </div>
              <div className="text-right">
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
          
          <div className="grid grid-cols-4 gap-4">
            <button onClick={() => window.location.href = '/courses'} className="px-4 py-2 bg-gray-100 rounded-lg hover:bg-gray-200">📚 Catalogue</button>
            <button onClick={() => window.location.href = '/learning/video'} className="px-4 py-2 bg-gray-100 rounded-lg hover:bg-gray-200">🎬 Vidéo</button>
            <button onClick={() => window.location.href = '/learning/text'} className="px-4 py-2 bg-gray-100 rounded-lg hover:bg-gray-200">📖 Texte</button>
            <button onClick={() => window.location.href = '/'} className="px-4 py-2 bg-gray-100 rounded-lg hover:bg-gray-200">🏠 Accueil</button>
          </div>
        </div>
      )}
    </main>
  </div>
);
};

export default AudioLearningPage;
