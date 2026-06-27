/* eslint-disable @typescript-eslint/no-unused-vars */
/* eslint-disable react-hooks/exhaustive-deps */
/* eslint-disable @typescript-eslint/no-explicit-any */

import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { courseService } from '../services/courseService';
import type { Course } from '../services/courseService';
import api from '../services/api';
import { bertQuizService, bertRecommendationService } from '../services/bertService';
import { mistakeService } from '../services/mistakeService'

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
  const [sidebarOpen, setSidebarOpen] = useState(true);

  
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
  const [searchTerm, setSearchTerm] = useState('');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadCourses();
    const savedProgress = localStorage.getItem('text_reading_progress');
    if (savedProgress) {
      setReadingProgress(parseInt(savedProgress));
    }
  }, []);

  useEffect(() => {
  if (selectedCourse && selectedCourse.id && !examMode) {
    loadRegularQuiz();
    loadQuestionsForCourse(selectedCourse.id);
    
    if (user?.id) {
      loadMistakesFromDB(user.id, selectedCourse.id);
    }
  }
}, [selectedCourse, examMode, user?.id]);


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
  };

  const generateExam = async () => {
    await generateBertExam();
  };

  const cancelExam = () => {
    resetExamState();
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
    const answersList: ExamAnswer[] = [];
    
    for (const q of examQuestions) {
      maxScore += q.points;
      const userAnswer = examAnswers[q.id];
      const isCorrect = userAnswer === q.reponse_correcte;
      if (isCorrect) totalScore += q.points;
      
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
    
    try {
      await api.post('/results', {
        utilisateur_id: user?.id,
        cours_id: selectedCourse.id,
        mode: 'texte_exam',
        score_quiz: percentage,
        temps_passe: Math.floor(readingProgress / 10),
        taux_completion: readingProgress,
        est_reussi: passed,
        feedback: passed ? `Examen réussi! Score: ${percentage.toFixed(1)}%` : `Score: ${percentage.toFixed(1)}%`
      });
      
      await analyzeMistakesAndRecommend(answersList);
      setShowRecommendations(true);
    } catch (error) {
      console.error('Erreur:', error);
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
  };

  const handleProgressChange = (progress: number) => {
    setReadingProgress(progress);
    localStorage.setItem('text_reading_progress', progress.toString());
  };

  const handleAnswerSelect = (questionId: number, answer: string) => {
    setUserAnswers(prev => ({ ...prev, [questionId]: answer }));
  };

  const handleExamAnswerSelect = (questionId: number, answer: string) => {
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
      console.log('❌ Erreur enregistrée:', q.question);
    }
    
    responses.push({
      question_id: q.id,
      reponse_utilisateur: userAnswer || '',
      est_correcte: isCorrect,
      temps_reponse: 30
    });
  }
  
  console.log('📝 Total des erreurs:', wrongQuestions.length);

  
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
    alert(`✅ Quiz soumis avec succès !\nScore: ${percentage.toFixed(1)}%\nRéponses correctes: ${correctCount}/${responses.length}`);
  } catch (error: any) {
    console.error('❌ Erreur:', error);
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
    console.log(`🤖 Tuteur IA analyse ${wrongQuestions.length} erreur(s)...`);
    
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

  
  const filteredCourses = courses.filter(course =>
    course.titre.toLowerCase().includes(searchTerm.toLowerCase())
  );

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
    <div className="flex min-h-screen bg-gray-100">
      
      <aside 
        className={`fixed left-0 top-0 h-full bg-white shadow-xl z-30 transition-all duration-300 ${
          sidebarOpen ? 'w-80' : 'w-16'
        } overflow-y-auto`}
      >
        
        <div className="sticky top-0 bg-white border-b p-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 rounded-lg hover:bg-gray-100 transition"
            >
              {sidebarOpen ? '◀' : '▶'}
            </button>
            {sidebarOpen && (
              <h2 className="text-lg font-bold text-gray-800">📚 Cours disponibles</h2>
            )}
          </div>
        </div>

        
        {sidebarOpen && (
          <div className="p-4 border-b">
            <div className="relative">
              <input
                type="text"
                placeholder="🔍 Rechercher un cours..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>
          </div>
        )}

        
        <nav className="py-4">
          {filteredCourses.map((course) => (
            <button
              key={course.id}
              onClick={() => handleCourseSelect(course)}
              className={`
                w-full text-left p-3 transition-all duration-200
                ${sidebarOpen ? 'px-6' : 'px-2 flex justify-center'}
                ${selectedCourse?.id === course.id 
                  ? 'bg-purple-50 border-l-4 border-purple-500 text-purple-700' 
                  : 'hover:bg-gray-50 text-gray-700'}
              `}
            >
              <div className="flex items-center gap-3">
                <span className="text-xl">
                  {course.id === 6 && '📝'}
                  {course.id === 11 && '🔗'}
                  {course.id === 8 && '📋'}
                  {course.id === 9 && '🏗️'}
                  {course.id === 10 && '🎨'}
                  {course.id === 12 && '🖼️'}
                  {![6, 11, 8, 9, 10, 12].includes(course.id) && '📘'}
                </span>
                {sidebarOpen && (
                  <div className="flex-1">
                    <p className="font-medium text-sm">{course.titre}</p>
                    <p className="text-xs text-gray-500 mt-0.5">
                      {course.difficulte || 'Débutant'} • {course.duree || 20} min
                    </p>
                  </div>
                )}
              </div>
            </button>
          ))}
        </nav>

        
        {sidebarOpen && (
          <div className="sticky bottom-0 bg-white border-t p-4 mt-4 space-y-2">
            
            <button
              onClick={generatePersonalizedQuiz}
              disabled={generatingQuiz || !selectedCourse}
              className="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {generatingQuiz ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  Génération...
                </>
              ) : (
                <>🎯 Quiz Personnalisé (Erreurs)</>
              )}
            </button>
            
    <button
      onClick={async () => {
        if (mistakeQuestions.length > 0) {
          const wrongQuestions = mistakeQuestions.map(q => ({ question: q, questionId: 0 }));
          await saveMistakesToDB(user?.id || 0, selectedCourse?.id || 0, wrongQuestions);
          await analyzeMistakesAndRecommendFromTexts(mistakeQuestions);
        } else {
          alert('Aucune erreur enregistrée pour ce cours');
        }
      }}
      disabled={mistakeQuestions.length === 0}
      className="w-full px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition disabled:opacity-50 flex items-center justify-center gap-2"
    >
      🤖 Tuteur IA - Recommandations
    </button>

            <button
      onClick={showMistakeStats}
      className="w-full px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition text-sm"
    >
      📊 Statistiques d'erreurs
    </button>
            
            
            <button
              onClick={generateBertQuiz}
              disabled={generatingQuiz || !selectedCourse}
              className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {generatingQuiz ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  Génération...
                </>
              ) : (
                <>🤖 Générer Quiz IA</>
              )}
            </button>
            
            
            {!examMode && (
              <button
                onClick={generateExam}
                disabled={generatingExam || !selectedCourse}
                className="w-full px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {generatingExam ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    Génération...
                  </>
                ) : (
                  <>📝 Examen final</>
                )}
              </button>
            )}
            
            {examMode && (
              <button
                onClick={cancelExam}
                className="w-full px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition"
              >
                ❌ Annuler l'examen
              </button>
            )}
            
            
            {quizGenerationMode === 'bert' && !examMode && questions.length > 0 && (
              <div className="text-xs text-center text-blue-600 bg-blue-50 p-2 rounded-lg mt-2">
                🤖 Quiz généré par IA
              </div>
            )}
            {quizGenerationMode === 'personalized' && !examMode && questions.length > 0 && (
              <div className="text-xs text-center text-green-600 bg-green-50 p-2 rounded-lg mt-2">
                🎯 Quiz personnalisé (basé sur vos erreurs)
              </div>
            )}
            {mistakeQuestions.length > 0 && !examMode && (
              <div className="text-xs text-center text-orange-600 bg-orange-50 p-2 rounded-lg mt-2">
                📝 {mistakeQuestions.length} erreur(s) enregistrée(s)
              </div>
            )}
          </div>
        )}
      </aside>

      
      <main 
        className={`flex-1 transition-all duration-300 ${sidebarOpen ? 'ml-80' : 'ml-16'}`}
      >
        <div className="max-w-4xl mx-auto py-8 px-6 space-y-8">
          
          <div className="bg-gradient-to-r from-purple-500 to-purple-700 rounded-2xl p-6 text-white">
            <div className="flex justify-between items-center">
              <div>
                <h1 className="text-3xl font-bold mb-2">
                  {examMode ? '📝 Examen Final' : '📖 Apprentissage par Texte'}
                </h1>
                <p className="opacity-90">
                  {examMode 
                    ? `Évaluez vos connaissances sur ${selectedCourse?.titre}`
                    : 'Apprenez HTML à travers des leçons écrites détaillées'}
                </p>
              </div>
              {!examMode && (
                <div className="flex gap-2">
                  <button
                    onClick={generatePersonalizedQuiz}
                    disabled={generatingQuiz || !selectedCourse}
                    className="px-3 py-2 bg-green-600 rounded-lg hover:bg-green-700 transition text-sm flex items-center gap-1"
                  >
                    {generatingQuiz ? '⏳' : '🎯'} Perso
                  </button>
                  <button
                    onClick={generateBertQuiz}
                    disabled={generatingQuiz || !selectedCourse}
                    className="px-3 py-2 bg-blue-600 rounded-lg hover:bg-blue-700 transition text-sm flex items-center gap-1"
                  >
                    {generatingQuiz ? '⏳' : '🤖'} IA
                  </button>
                </div>
              )}
            </div>
          </div>

          
          {!examMode && selectedCourse && (
            <div className="bg-white rounded-xl shadow-md p-6">
              <div className="flex items-start justify-between">
                <div>
                  <h2 className="text-xl font-bold text-gray-800">{selectedCourse.titre}</h2>
                  <p className="text-gray-600 mt-1">{selectedCourse.description || 'Aucune description disponible'}</p>
                  <div className="flex gap-4 mt-3">
                    <span className="text-sm text-gray-500">📊 Niveau: {selectedCourse.difficulte || 'Débutant'}</span>
                    <span className="text-sm text-gray-500">⏱️ Durée: {selectedCourse.duree || 25} min</span>
                  </div>
                </div>
                {readingProgress === 100 && (
                  <div className="text-green-500 text-sm bg-green-50 px-3 py-1 rounded-full">
                    ✅ Terminé
                  </div>
                )}
              </div>
            </div>
          )}

          
          {!examMode && (
            <div className="bg-white rounded-xl shadow-md p-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold">📊 Progression de lecture</h3>
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
                  className="mt-4 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition text-sm"
                >
                  ✅ Marquer comme terminé
                </button>
              )}
            </div>
          )}

          
          {!examMode && selectedCourse && (
            <div className="bg-white rounded-xl shadow-md p-8">
              <div className="prose max-w-none">
                {selectedCourse.contenu ? (
                  <div dangerouslySetInnerHTML={{ __html: selectedCourse.contenu }} />
                ) : (
                  <div className="text-gray-500 italic">
                    Le contenu de ce cours sera bientôt disponible.
                  </div>
                )}
              </div>
            </div>
          )}

          
          {!examMode && (
            <div className="bg-gradient-to-r from-purple-500 to-purple-700 rounded-xl p-8 text-white">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-2xl font-bold">🎯 Quiz de révision</h3>
                {quizGenerationMode === 'bert' && (
                  <span className="text-xs bg-blue-500 px-3 py-1 rounded-full">Généré par IA</span>
                )}
                {quizGenerationMode === 'personalized' && (
                  <span className="text-xs bg-green-500 px-3 py-1 rounded-full">Personnalisé</span>
                )}
              </div>
              <p className="mb-6">Testez vos connaissances sur {selectedCourse?.titre}</p>

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
                        <p className="font-semibold mb-3">
                          Question {idx + 1} ({q.points} points - {q.difficulte})
                        </p>
                        <p className="mb-3">{q.question}</p>
                        <div className="space-y-2">
                          {Object.entries(q.options).map(([key, value]) => (
                            <label key={key} className="flex items-center gap-3 cursor-pointer">
                              <input
                                type="radio"
                                name={`question_${q.id}`}
                                value={key}
                                checked={userAnswers[q.id] === key}
                                onChange={() => handleAnswerSelect(q.id, key)}
                                className="w-4 h-4"
                              />
                              <span>{key}: {value}</span>
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
                      className="w-full mt-4 px-6 py-3 bg-white text-purple-600 rounded-lg font-semibold hover:bg-gray-100 transition disabled:opacity-50"
                    >
                      📤 Soumettre le quiz
                    </button>
                  </>
                ) : (
                  <div className="bg-white/10 rounded-lg p-6 text-center">
                    <div className="text-5xl mb-4">🎉</div>
                    <h4 className="text-2xl font-bold mb-2">Résultats du quiz</h4>
                    <p className="text-3xl font-bold mb-2">{quizScore.toFixed(1)}%</p>
                    <p className="mb-4">
                      {quizScore >= 70 ? '✅ Félicitations !' : '⚠️ Revoyez la leçon et réessayez.'}
                    </p>
                    <div className="flex flex-wrap gap-2 justify-center">
                      <button
                        onClick={resetQuiz}
                        className="px-6 py-2 bg-white text-purple-600 rounded-lg hover:bg-gray-100"
                      >
                        🔄 Recommencer
                      </button>
                      <button
                        onClick={generateBertQuiz}
                        disabled={generatingQuiz}
                        className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
                      >
                        {generatingQuiz ? '⏳...' : '🤖 Nouveau quiz IA'}
                      </button>
                      <button
                        onClick={generatePersonalizedQuiz}
                        disabled={generatingQuiz}
                        className="px-6 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600"
                      >
                        {generatingQuiz ? '⏳...' : '🎯 Quiz personnalisé'}
                      </button>
                    </div>
                  </div>
                )
              ) : (
                <div className="text-center py-8 bg-white/10 rounded-lg">
                  <p>📝 Aucune question disponible.</p>
                  <div className="flex gap-2 justify-center mt-4">
                    <button
                      onClick={generateBertQuiz}
                      disabled={generatingQuiz}
                      className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
                    >
                      🤖 Générer quiz IA
                    </button>
                    <button
                      onClick={generatePersonalizedQuiz}
                      disabled={generatingQuiz}
                      className="px-6 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600"
                    >
                      🎯 Quiz personnalisé
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}

          
{showRecommendations && !examMode && (
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
            onClick={() => navigateToCourse(rec.cours_id)}
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


          
          {examMode && (
            <div className="bg-gradient-to-r from-indigo-500 to-indigo-700 rounded-xl p-8 text-white">
              <h3 className="text-2xl font-bold mb-4">📝 Examen Final</h3>
              <p className="mb-2">Cours: {selectedCourse?.titre}</p>
              <p className="text-sm mb-6">Score minimum requis: 70%</p>

              {generatingExam ? (
                <div className="text-center py-12">
                  <div className="text-4xl mb-4">⏳</div>
                  <p>Génération de votre examen personnalisé...</p>
                </div>
              ) : examSubmitted && examResult ? (
                <div className="space-y-6">
                  <div className="bg-white/10 rounded-lg p-6 text-center">
                    <div className="text-6xl mb-4">{examResult.passed ? '🎓' : '📚'}</div>
                    <h4 className="text-2xl font-bold mb-2">Résultat de l'examen</h4>
                    <p className="text-5xl font-bold mb-2">{examResult.percentage.toFixed(1)}%</p>
                    <p className="mb-4">
                      {examResult.passed 
                        ? '✅ Félicitations ! Vous avez réussi l\'examen.' 
                        : '⚠️ Vous n\'avez pas atteint le seuil de réussite (70%).'}
                    </p>
                    <p className="text-sm">
                      Score: {examResult.score} / {examResult.total} points
                    </p>
                  </div>

                  {examResult.answers.filter((a: ExamAnswer) => !a.isCorrect).length > 0 && (
                    <div className="bg-yellow-500/20 rounded-lg p-4">
                      <h4 className="font-bold mb-3">
                        📊 Analyse des erreurs ({examResult.answers.filter((a: ExamAnswer) => !a.isCorrect).length})
                      </h4>
                      <div className="space-y-2 max-h-60 overflow-y-auto">
                        {examResult.answers.filter((a: ExamAnswer) => !a.isCorrect).map((answer: ExamAnswer, idx: number) => (
                          <div key={idx} className="bg-white/10 rounded p-2 text-sm">
                            <p className="font-semibold">❌ {answer.questionText.substring(0, 80)}...</p>
                            <p>Votre réponse: {answer.selectedAnswer} | Bonne réponse: {answer.correctAnswer}</p>
                            {answer.explanation && (
                              <p className="text-xs mt-1 opacity-80">💡 {answer.explanation.substring(0, 150)}</p>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {showRecommendations && (
                    <div className="bg-blue-500/20 rounded-lg p-4">
                      <h4 className="font-bold mb-3">🤖 Recommandations personnalisées</h4>
                      {loadingRecommendations ? (
                        <p className="text-center py-4">Analyse de vos résultats...</p>
                      ) : recommendations.length > 0 ? (
                        <div className="space-y-2">
                          <p className="text-sm mb-2">Basé sur vos erreurs, voici les cours à réviser :</p>
                          {recommendations.map((rec, idx) => (
                            <div 
                              key={idx}
                              onClick={() => navigateToCourse(rec.cours_id)}
                              className="bg-white/10 rounded-lg p-3 cursor-pointer hover:bg-white/20 transition"
                            >
                              <div className="flex justify-between items-center">
                                <div>
                                  <p className="font-semibold">
                                    {rec.direct_match && '🔴 '}
                                    {rec.cours_titre}
                                  </p>
                                  <p className="text-xs opacity-80">{rec.description}</p>
                                </div>
                                <div className="text-right">
                                  <span className="text-xs bg-white/20 px-2 py-1 rounded">
                                    Score: {(rec.score * 100).toFixed(0)}%
                                  </span>
                                </div>
                              </div>
                            </div>
                          ))}
                          <p className="text-xs text-center mt-2">
                            Cliquez sur un cours pour le réviser immédiatement
                          </p>
                        </div>
                      ) : (
                        <p>Aucune recommandation spécifique. Continuez votre apprentissage !</p>
                      )}
                    </div>
                  )}

                  <div className="flex gap-3">
                    <button
                      onClick={cancelExam}
                      className="flex-1 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition"
                    >
                      🔄 Retour aux cours
                    </button>
                    <button
                      onClick={() => {
                        setExamSubmitted(false);
                        setExamResult(null);
                        setShowRecommendations(false);
                        generateExam();
                      }}
                      className="flex-1 px-4 py-2 bg-white text-indigo-600 rounded-lg font-semibold hover:bg-gray-100 transition"
                    >
                      🔁 Recommencer l'examen
                    </button>
                  </div>
                </div>
              ) : (
                <>
                  <p className="text-sm mb-4">L'examen contient {examQuestions.length} questions.</p>
                  {examQuestions.map((q, idx) => (
                    <div key={q.id} className="bg-white/10 rounded-lg p-4 mb-4">
                      <p className="font-semibold mb-3">
                        Question {idx + 1} ({q.points} points - {q.difficulte})
                      </p>
                      <p className="mb-3">{q.question}</p>
                      <div className="space-y-2">
                        {Object.entries(q.options).map(([key, value]) => (
                          <label key={key} className="flex items-center gap-3 cursor-pointer">
                            <input
                              type="radio"
                              name={`exam_question_${q.id}`}
                              value={key}
                              checked={examAnswers[q.id] === key}
                              onChange={() => handleExamAnswerSelect(q.id, key)}
                              className="w-4 h-4"
                            />
                            <span>{key}: {value}</span>
                          </label>
                        ))}
                      </div>
                    </div>
                  ))}
                  <button
                    onClick={submitExam}
                    disabled={Object.keys(examAnswers).length !== examQuestions.length}
                    className="w-full px-6 py-3 bg-white text-indigo-600 rounded-lg font-semibold hover:bg-gray-100 transition disabled:opacity-50"
                  >
                    📤 Soumettre l'examen
                  </button>
                  {Object.keys(examAnswers).length !== examQuestions.length && (
                    <p className="text-sm text-yellow-200 mt-2 text-center">
                      ⚠️ {Object.keys(examAnswers).length}/{examQuestions.length} questions répondues
                    </p>
                  )}
                </>
              )}
            </div>
          )}

          
          <div className="grid grid-cols-4 gap-4">
            <button
              onClick={() => window.location.href = '/courses'}
              className="px-4 py-2 bg-gray-100 rounded-lg hover:bg-gray-200 transition text-sm"
            >
              📚 Catalogue
            </button>
            <button
              onClick={() => window.location.href = '/learning/video'}
              className="px-4 py-2 bg-gray-100 rounded-lg hover:bg-gray-200 transition text-sm"
            >
              🎬 Vidéo
            </button>
            <button
              onClick={() => window.location.href = '/learning/audio'}
              className="px-4 py-2 bg-gray-100 rounded-lg hover:bg-gray-200 transition text-sm"
            >
              🔊 Audio
            </button>
            <button
              onClick={() => window.location.href = '/'}
              className="px-4 py-2 bg-gray-100 rounded-lg hover:bg-gray-200 transition text-sm"
            >
              🏠 Accueil
            </button>
          </div>
        </div>
      </main>
    </div>
  );
};

export default TextLearningPage;