/* eslint-disable @typescript-eslint/no-unused-vars */
/* eslint-disable react-hooks/exhaustive-deps */
/* eslint-disable @typescript-eslint/no-explicit-any */
/* eslint-disable */

import { useState, useEffect ,useRef,useCallback} from 'react';
import { useAuth } from '../contexts/AuthContext';
import { courseService } from '../services/courseService';
import type { Course } from '../services/courseService';
import api from '../services/api';
import { mistakeService } from '../services/mistakeService';
import { bertQuizService } from '../services/bertService';
import { bertRecommendationService } from '../services/bertService';
import { useNavigate } from 'react-router-dom';
import { LearningProvider, LearningContextType } from '../contexts/LearningContext';
import { useOutletContext } from 'react-router-dom';

interface Question {
  id: number;
  question: string;
  options: Record<string, string>;
  reponse_correcte: string;
  points: number;
  difficulte: string;
  explication?: string;
}

interface Recommendation {
  cours_id: string;
  cours_titre: string;
  score: number;
  description: string;
  direct_match: boolean;
  nb_erreurs: number;
}

const VideoLearningPage = () => {
  const { isAuthenticated, user } = useAuth();
  const [courses, setCourses] = useState<Course[]>([]);
  const [selectedCourse, setSelectedCourse] = useState<Course | null>(null);
  const [loading, setLoading] = useState(true);
  const [videoProgress, setVideoProgress] = useState(0);
  const [quizSubmitted, setQuizSubmitted] = useState(false);
  const [quizScore, setQuizScore] = useState(0);
  const [userAnswers, setUserAnswers] = useState<Record<number, string>>({});
  const [showExplanation, setShowExplanation] = useState<Record<number, boolean>>({});
  const [questions, setQuestions] = useState<Question[]>([]);
  const [loadingQuestions, setLoadingQuestions] = useState(false);
  const [quizResultId, setQuizResultId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [notes, setNotes] = useState('');
  const [playbackSpeed, setPlaybackSpeed] = useState(1.0);
  const [quality, setQuality] = useState('720p');
  const [generatingQuiz, setGeneratingQuiz] = useState(false);
const [quizGenerationMode, setQuizGenerationMode] = useState<'default' | 'bert' | 'personalized'>('default');
const [mistakeQuestions, setMistakeQuestions] = useState<string[]>([]);

  const [examMode, setExamMode] = useState(false);
const [examQuestions, setExamQuestions] = useState<Question[]>([]);
const [examSubmitted, setExamSubmitted] = useState(false);
const [examResult, setExamResult] = useState<any>(null);
const [examAnswers, setExamAnswers] = useState<Record<number, string>>({});
const [generatingExam, setGeneratingExam] = useState(false);
const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
const [showRecommendations, setShowRecommendations] = useState(false);
const [loadingRecommendations, setLoadingRecommendations] = useState(false);
const [selectedCategory, setSelectedCategory] = useState<string>('all');
const [isCategoryDropdownOpen, setIsCategoryDropdownOpen] = useState(false);
const dropdownRef = useRef<HTMLDivElement>(null);
const navigate = useNavigate();
const { setLearningContextValue } = useOutletContext<{ 
    setLearningContextValue: (value: LearningContextType) => void 
  }>();



 const generateCertificate = async (examResultData: any, courseName: string) => {
  if (!user) return;

  try {
    const response = await api.post('/certificates/generate', {
      user_id: user.id,
      course_id: selectedCourse?.id,
      score: examResultData.percentage,
      course_name: 'Formation Complète HTML, CSS & JavaScript',  
      mode: 'video',
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

 
  const videoCourseIds = [6, 11, 12, 8, 9, 10, 13, 14, 15, 16, 17, 18, 19, 20, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48];
  
  const coursesCompleted = courses.filter(c => videoCourseIds.includes(c.id));

  
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
    const displayTitle = course.titre.length > 35 ? course.titre.substring(0, 35) + '...' : course.titre;
    ctx.fillText(`✅ ${displayTitle}`, col1X, startY + idx * rowHeight);
  });
  
  col2Courses.forEach((course, idx) => {
    const displayTitle = course.titre.length > 35 ? course.titre.substring(0, 35) + '...' : course.titre;
    ctx.fillText(`✅ ${displayTitle}`, col2X, startY + idx * rowHeight);
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


  

const getCourseCategories = () => {
  return {
    HTML: {
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

useEffect(() => {
  const handleClickOutside = (event: MouseEvent) => {
    if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
      setIsCategoryDropdownOpen(false);
    }
  };
  document.addEventListener('mousedown', handleClickOutside);
  return () => document.removeEventListener('mousedown', handleClickOutside);
}, []);


const getFilteredCourses = () => {
  const categories = getCourseCategories();
  const allVideoCourseIds = new Set<number>();
  
  
  Object.values(categories).forEach(cat => {
    cat.courses.forEach(c => allVideoCourseIds.add(c.id));
  });

  if (selectedCategory === 'all') {
    return courses.filter(c => allVideoCourseIds.has(c.id));
  }

  const categoryData = categories[selectedCategory as keyof typeof categories];
  if (!categoryData) return [];
  
  const categoryIds = new Set(categoryData.courses.map(c => c.id));
  return courses.filter(c => categoryIds.has(c.id));
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
        return '🎬';
      }
    }
  }
  return '🎬';
};


function getDefaultOptionsForQuestion(question: string): Record<string, string> {
  if (!question || typeof question !== 'string') {
    return { A: "Option A", B: "Option B", C: "Option C", D: "Option D" };
  }
  
  const lowerQuestion = question.toLowerCase();
  
  
  if (lowerQuestion.includes("titre principal") || lowerQuestion.includes("h1")) {
    return { A: "<title>", B: "<h1>", C: "<head>", D: "<header>" };
  }
  
  
  if (lowerQuestion.includes("lien hypertexte") || lowerQuestion.includes("<a>")) {
    return { A: "<link>", B: "<a>", C: "<href>", D: "<url>" };
  }
  
  if (lowerQuestion.includes("attribut") && lowerQuestion.includes("url")) {
    return { A: "src", B: "url", C: "href", D: "link" };
  }
  
  if (lowerQuestion.includes("nouvel onglet") || lowerQuestion.includes("target")) {
    return { A: "target='_self'", B: "target='_blank'", C: "target='_new'", D: "target='_top'" };
  }
  
  
  if (lowerQuestion.includes("ligne dans un tableau")) {
    return { A: "</table>", B: "<tr>", C: "<th>", D: "<thead>" };
  }
  
  if (lowerQuestion.includes("cellule d'en-tête") || (lowerQuestion.includes("en-tête") && lowerQuestion.includes("tableau"))) {
    return { A: "<td>", B: "<tr>", C: "<th>", D: "<thead>" };
  }
  
  
  if (lowerQuestion.includes("champ obligatoire") || lowerQuestion.includes("required")) {
    return { A: "mandatory", B: "required", C: "obligatory", D: "force" };
  }
  
  if (lowerQuestion.includes("méthode http") && lowerQuestion.includes("formulaire")) {
    return { A: "GET", B: "POST", C: "PUT", D: "DELETE" };
  }
  
  
  if (lowerQuestion.includes("surligner")) {
    return { A: "<mark>", B: "<highlight>", C: "<strong>", D: "<em>" };
  }
  
  if (lowerQuestion.includes("pliable") || lowerQuestion.includes("dépliable")) {
    return { A: "<details> et <summary>", B: "<collapse> et <expand>", C: "<fold> et <unfold>", D: "<hide> et <show>" };
  }
  
  if (lowerQuestion.includes("sémantique")) {
    return { A: "Meilleur SEO et accessibilité", B: "Chargement plus rapide", C: "Design plus joli", D: "Compatibilité avec plus de navigateurs" };
  }
  
  if (lowerQuestion.includes("thématiquement lié") || lowerQuestion.includes("section")) {
    return { A: "<div>", B: "<group>", C: "<section>", D: "<article>" };
  }
  
  if (lowerQuestion.includes("contenu principal") || lowerQuestion.includes("<main>")) {
    return { A: "0 fois", B: "1 fois", C: "2 fois", D: "Autant qu'on veut" };
  }
  
  if (lowerQuestion.includes("en-tête d'une page") || lowerQuestion.includes("header")) {
    return { A: "<head>", B: "<header>", C: "<h1>", D: "<top>" };
  }
  
  
  if (lowerQuestion.includes("sélecteur") && lowerQuestion.includes("paragraphes")) {
    return { A: "p", B: "#paragraph", C: ".paragraph", D: "<p>" };
  }
  
  if (lowerQuestion.includes("taille du texte") || lowerQuestion.includes("font-size")) {
    return { A: "text-size", B: "font-size", C: "size", D: "text-scale" };
  }
  
  if (lowerQuestion.includes("barrer le texte") || lowerQuestion.includes("line-through")) {
    return { A: "underline", B: "overline", C: "line-through", D: "none" };
  }
  
  if (lowerQuestion.includes("couleur du texte")) {
    return { A: "text-color", B: "font-color", C: "color", D: "background-color" };
  }
  
  if (lowerQuestion.includes("couleur de fond") || lowerQuestion.includes("background-color")) {
    return { A: "color", B: "bg-color", C: "background", D: "background-color" };
  }
  
  
  if (lowerQuestion.includes("modifier le contenu texte") || lowerQuestion.includes("innerHTML")) {
    return { A: "element.value = nouveauTexte", B: "element.innerHTML = nouveauTexte", C: "element.text = nouveauTexte", D: "element.content = nouveauTexte" };
  }
  
  if (lowerQuestion.includes("sélectionner") && lowerQuestion.includes("id")) {
    return { A: "getElementByClass()", B: "getElementById()", C: "querySelector()", D: "getElementsByTag()" };
  }
  
  if (lowerQuestion.includes("masquer") && lowerQuestion.includes("élément")) {
    return { A: "element.hide()", B: "element.style.display = 'none'", C: "element.visible = false", D: "element.remove()" };
  }
  
  
  if (lowerQuestion.includes("structure suivante") || (lowerQuestion.includes("liste.html") && lowerQuestion.includes("index.html"))) {
    return { A: "../index.html", B: "./index.html", C: "/index.html", D: "index.html" };
  }
  
  
  return { A: "Option A", B: "Option B", C: "Option C", D: "Option D" };
}



const analyzeMistakesAndRecommend = async (wrongQuestions: string[]) => {
  if (!user?.id || wrongQuestions.length === 0) {
    console.log('Aucune erreur à analyser');
    return;
  }
  
  setLoadingRecommendations(true);
  
  try {
    console.log(` Tuteur IA analyse ${wrongQuestions.length} erreur(s)...`);
    
    
    const response = await bertRecommendationService.recommendCourses(
      wrongQuestions, 
      0.5,  
      5     
    );
    
    if (response && response.recommendations && response.recommendations.length > 0) {
      setRecommendations(response.recommendations);
      setShowRecommendations(true);
      
      
      const toast = document.createElement('div');
      toast.className = 'fixed bottom-4 right-4 bg-blue-500 text-white px-4 py-2 rounded-lg shadow-lg z-50 animate-pulse';
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
      }
    }
  } catch (error) {
    console.error(' Erreur recommandation IA:', error);
    
    
    const fallbackRecs = generateFallbackRecommendations(wrongQuestions);
    if (fallbackRecs.length > 0) {
      setRecommendations(fallbackRecs);
      setShowRecommendations(true);
    }
  } finally {
    setLoadingRecommendations(false);
  }
};


const generateFallbackRecommendations = (wrongQuestions: string[]): Recommendation[] => {
  const recommendations: Recommendation[] = [];
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
    "css": {
      id: "17",
      title: "CSS - Les Sélecteurs",
      description: "Apprenez à cibler les éléments avec les sélecteurs CSS"
    },
    "javascript": {
      id: "33",
      title: "JavaScript - Introduction",
      description: "Découvrez les bases du JavaScript"
    }
  };
  
  const matchedCourses = new Set<string>();
  
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
  
  return recommendations.slice(0, 5);
};


const navigateToRecommendedCourse = (courseId: string) => {
  const course = courses.find(c => String(c.id) === courseId);
  if (course) {
    setSelectedCourse(course);
    setShowRecommendations(false);
    window.scrollTo({ top: 0, behavior: 'smooth' });
    
    setTimeout(() => loadQuestionsForCourse(course.id), 100);
    
    const toast = document.createElement('div');
    toast.className = 'fixed bottom-4 right-4 bg-green-500 text-white px-4 py-2 rounded-lg shadow-lg z-50';
    toast.textContent = `📚 Chargement du cours: ${course.titre}`;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 2000);
  }
};

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
        
        
        
        
        if (questionText.includes("sémantique")) {
          options = { A: "Meilleur SEO et accessibilité", B: "Chargement plus rapide",
                      C: "Design plus joli", D: "Compatibilité avec plus de navigateurs" };
          correctAnswer = "A";
        }
        
        else if (questionText.includes("<main>") || (questionText.includes("contenu principal") && questionText.includes("une fois"))) {
          options = { A: "0 fois", B: "1 fois", C: "2 fois", D: "Autant qu'on veut" };
          correctAnswer = "B";
        }
        
        else if (questionText.includes("méthode HTTP") && questionText.includes("formulaire")) {
          options = { A: "GET", B: "POST", C: "PUT", D: "DELETE" };
          correctAnswer = "A";
        }
        
        else if (questionText.includes("barrer le texte") || (questionText.includes("text-decoration") && questionText.includes("barrer"))) {
          options = { A: "underline", B: "overline", C: "line-through", D: "none" };
          correctAnswer = "C";
        }
        
        else if (questionText.includes("changer le contenu HTML") || (questionText.includes("méthode JavaScript") && questionText.includes("contenu HTML"))) {
          options = { A: "element.value = nouveauTexte", B: "element.innerHTML = nouveauTexte",
                      C: "element.text = nouveauTexte", D: "element.content = nouveauTexte" };
          correctAnswer = "B";
        }
        
        else if (questionText.includes("taille du texte") || questionText.includes("propriete CSS") && questionText.includes("taille")) {
          options = { A: "text-size", B: "font-size", C: "size", D: "text-scale" };
          correctAnswer = "B";
        }
        
        else if (questionText.includes("titre principal")) {
          options = { A: "<title>", B: "<h1>", C: "<head>", D: "<header>" };
          correctAnswer = "B";
        }
        
        else if (questionText.includes("thématiquement lié") || (questionText.includes("regroupe") && questionText.includes("contenu"))) {
          options = { A: "<div>", B: "<group>", C: "<section>", D: "<article>" };
          correctAnswer = "C";
        }
        
        else if (questionText.includes("sélecteur CSS") && questionText.includes("paragraphes")) {
          options = { A: "p", B: "#paragraph", C: ".paragraph", D: "<p>" };
          correctAnswer = "A";
        }
        
        else if (questionText.includes("cellule d'en-tête") && questionText.includes("tableau")) {
          options = { A: "<td>", B: "<tr>", C: "<th>", D: "<thead>" };
          correctAnswer = "C";
        }
        
        else if (questionText.includes("surligner")) {
          options = { A: "<mark>", B: "<highlight>", C: "<strong>", D: "<em>" };
          correctAnswer = "A";
        }
        
        else if (questionText.includes("pliable") || questionText.includes("dépliable")) {
          options = { A: "<details> et <summary>", B: "<collapse> et <expand>", 
                      C: "<fold> et <unfold>", D: "<hide> et <show>" };
          correctAnswer = "A";
        }
        
        else if (questionText.includes("modifier le contenu texte") || questionText.includes("innerHTML")) {
          options = { A: "element.value = nouveauTexte", B: "element.innerHTML = nouveauTexte",
                      C: "element.text = nouveauTexte", D: "element.content = nouveauTexte" };
          correctAnswer = "B";
        }
        
        else if (questionText.includes("lien hypertexte")) {
          options = { A: "<link>", B: "<a>", C: "<href>", D: "<url>" };
          correctAnswer = "B";
        }
        
        else if (questionText.includes("en-tête d'une page") || questionText.includes("header")) {
          options = { A: "<head>", B: "<header>", C: "<h1>", D: "<top>" };
          correctAnswer = "B";
        }
       
        else {
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
          
          if (!cleanValue || cleanValue.length < 1 || cleanValue === ':' || cleanValue === 'B' ||
              cleanValue === 'Option A' || cleanValue === 'Option B' || 
              cleanValue === 'Option C' || cleanValue === 'Option D') {
            const defaultValues = ["Première option valide", "Deuxième option valide", "Troisième option valide", "Quatrième option valide"];
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
      const defaultQs = getDefaultQuestionsForVideo();
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

const getDefaultQuestionsForVideo = (): Question[] => {
  return [
    {
      id: 1,
      question: "Quel est l'avantage principal des balises sémantiques HTML5 ?",
      options: { A: "Meilleur SEO et accessibilité", B: "Chargement plus rapide", C: "Design plus joli", D: "Compatibilité avec plus de navigateurs" },
      reponse_correcte: "A",
      points: 15,
      difficulte: "difficile",
      explication: "Les balises sémantiques améliorent le SEO et l'accessibilité."
    },
    {
      id: 2,
      question: "Combien de fois peut-on utiliser la balise <main> dans une page HTML ?",
      options: { A: "0 fois", B: "1 fois", C: "2 fois", D: "Autant qu'on veut" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "moyen",
      explication: "La balise <main> ne doit être utilisée qu'une seule fois par page."
    },
    {
      id: 3,
      question: "Quelle est la méthode HTTP par défaut pour un formulaire HTML ?",
      options: { A: "GET", B: "POST", C: "PUT", D: "DELETE" },
      reponse_correcte: "A",
      points: 10,
      difficulte: "facile",
      explication: "GET est la méthode par défaut pour les formulaires HTML."
    },
    {
      id: 4,
      question: "Quelle valeur de text-decoration permet de barrer le texte ?",
      options: { A: "underline", B: "overline", C: "line-through", D: "none" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "text-decoration: line-through ajoute une ligne qui traverse le texte."
    },
    {
      id: 5,
      question: "Quelle est la methode JavaScript pour changer le contenu HTML d'un element ?",
      options: { A: "element.value = nouveauTexte", B: "element.innerHTML = nouveauTexte", C: "element.text = nouveauTexte", D: "element.content = nouveauTexte" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "innerHTML permet de modifier le contenu HTML d'un élément."
    },
    {
      id: 6,
      question: "Quelle propriete CSS controle la taille du texte ?",
      options: { A: "text-size", B: "font-size", C: "size", D: "text-scale" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "font-size contrôle la taille du texte en CSS."
    },
    {
      id: 7,
      question: "Quelle balise utiliser pour le titre principal d'une page HTML ?",
      options: { A: "<title>", B: "<h1>", C: "<head>", D: "<header>" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "<h1> est utilisé pour le titre principal d'une page."
    },
    {
      id: 8,
      question: "Quelle balise HTML5 regroupe du contenu thématiquement lié ?",
      options: { A: "<div>", B: "<group>", C: "<section>", D: "<article>" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "moyen",
      explication: "<section> regroupe du contenu thématiquement lié."
    },
    {
      id: 9,
      question: "Quel est le sélecteur CSS qui cible TOUS les paragraphes d'une page ?",
      options: { A: "p", B: "#paragraph", C: ".paragraph", D: "<p>" },
      reponse_correcte: "A",
      points: 10,
      difficulte: "facile",
      explication: "Le sélecteur 'p' cible tous les paragraphes."
    },
    {
      id: 10,
      question: "Quelle balise HTML est utilisée pour une cellule d'en-tête dans un tableau ?",
      options: { A: "<td>", B: "<tr>", C: "<th>", D: "<thead>" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "<th> (table header) est utilisée pour les cellules d'en-tête."
    },
    {
      id: 11,
      question: "Quelle balise HTML5 est utilisée pour surligner du texte ?",
      options: { A: "<mark>", B: "<highlight>", C: "<strong>", D: "<em>" },
      reponse_correcte: "A",
      points: 10,
      difficulte: "facile",
      explication: "La balise <mark> est utilisée pour surligner du texte."
    },
    {
      id: 12,
      question: "Quelle est la balise HTML5 pour l'en-tête d'une page ou d'une section ?",
      options: { A: "<head>", B: "<header>", C: "<h1>", D: "<top>" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "<header> représente l'en-tête d'une page ou d'une section."
    }
  ];
};


const getDefaultExamQuestions = (): Question[] => {
  return [
    {
      id: 1,
      question: "Quel est l'avantage principal des balises sémantiques HTML5 ?",
      options: { A: "Meilleur SEO et accessibilité", B: "Chargement plus rapide", C: "Design plus joli", D: "Compatibilité avec plus de navigateurs" },
      reponse_correcte: "A",
      points: 15,
      difficulte: "difficile",
      explication: "Les balises sémantiques améliorent le SEO et l'accessibilité."
    },
    {
      id: 2,
      question: "Comment modifier le contenu texte d'un element HTML en JavaScript ?",
      options: { A: "element.value = nouveauTexte", B: "element.innerHTML = nouveauTexte", C: "element.text = nouveauTexte", D: "element.content = nouveauTexte" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "innerHTML permet de modifier le contenu HTML d'un élément."
    },
    {
      id: 3,
      question: "Combien de fois peut-on utiliser la balise <main> dans une page HTML ?",
      options: { A: "0 fois", B: "1 fois", C: "2 fois", D: "Autant qu'on veut" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "moyen",
      explication: "La balise <main> ne doit être utilisée qu'une seule fois par page."
    },
    {
      id: 4,
      question: "Quelle balise HTML est utilisée pour créer une ligne dans un tableau ?",
      options: { A: "<td>", B: "<td>", C: "<th>", D: "<thead>" },
      reponse_correcte: "A",
      points: 10,
      difficulte: "facile",
      explication: "La balise <td> (table row) définit une ligne dans un tableau."
    },
    {
      id: 5,
      question: "Quelle balise utiliser pour le titre principal d'une page HTML ?",
      options: { A: "<title>", B: "<h1>", C: "<head>", D: "<header>" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "<h1> est utilisé pour le titre principal d'une page."
    },
    {
      id: 6,
      question: "Quelle valeur de text-decoration permet de barrer le texte ?",
      options: { A: "underline", B: "overline", C: "line-through", D: "none" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "text-decoration: line-through ajoute une ligne qui traverse le texte."
    },
    {
      id: 7,
      question: "Quelle balise HTML est utilisée pour une cellule d'en-tête dans un tableau ?",
      options: { A: "<td>", B: "<tr>", C: "<th>", D: "<thead>" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "<th> (table header) est utilisée pour les cellules d'en-tête."
    },
    {
      id: 8,
      question: "Quelle est la methode JavaScript pour changer le contenu HTML d'un element ?",
      options: { A: "element.value = nouveauTexte", B: "element.innerHTML = nouveauTexte", C: "element.text = nouveauTexte", D: "element.content = nouveauTexte" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "innerHTML permet de modifier le contenu HTML d'un élément."
    },
    {
      id: 9,
      question: "Quelle est la balise HTML5 pour l'en-tête d'une page ou d'une section ?",
      options: { A: "<head>", B: "<header>", C: "<h1>", D: "<top>" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "<header> représente l'en-tête d'une page ou d'une section."
    },
    {
      id: 10,
      question: "Quel est le sélecteur CSS qui cible TOUS les paragraphes d'une page ?",
      options: { A: "p", B: "#paragraph", C: ".paragraph", D: "<p>" },
      reponse_correcte: "A",
      points: 10,
      difficulte: "facile",
      explication: "Le sélecteur 'p' cible tous les paragraphes."
    }
  ];
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
  const answersList: any[] = [];
  const wrongQuestionsList: { question: string; questionId: number }[] = [];

  console.log(`📝 Nombre de questions dans l'examen: ${examQuestions.length}`);

  
  for (const q of examQuestions) {
    maxScore += q.points || 10;
    const userAnswer = examAnswers[q.id];
    const isCorrect = userAnswer === q.reponse_correcte;
    if (isCorrect) {
      totalScore += q.points || 10;
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

  console.log(`📊 Résultat: Score=${totalScore}/${maxScore}, Pourcentage=${percentage.toFixed(1)}%, Passé=${passed}`);

 
  setExamResult({ score: totalScore, total: maxScore, percentage, passed, answers: answersList });
  setExamSubmitted(true);

  try {
    
    const resultData = {
      utilisateur_id: Number(user.id),  
      cours_id: Number(selectedCourse.id),  
      mode: 'video',  
      score_quiz: Number(percentage.toFixed(2)),
      temps_passe: Math.max(1, Math.floor(videoProgress / 2) || 1),
      taux_completion: Number(videoProgress > 0 ? videoProgress : 100),
      est_reussi: passed,
      feedback: passed 
        ? `Examen réussi! Score: ${percentage.toFixed(1)}%` 
        : `Score: ${percentage.toFixed(1)}%`
    };

    console.log('📤 Envoi des données au backend:', JSON.stringify(resultData, null, 2));

    const response = await api.post('/results', resultData);
    console.log('✅ Résultat enregistré:', response.data);

    
    if (wrongQuestionsList.length > 0 && user?.id && selectedCourse?.id) {
      await saveMistakesToDB(user.id, selectedCourse.id, wrongQuestionsList);
      await loadMistakesFromDB(user.id, selectedCourse.id);
      
      const wrongQuestionTexts = wrongQuestionsList.map(w => w.question);
      await analyzeMistakesAndRecommend(wrongQuestionTexts);
    }
    
    setShowRecommendations(true);

    
    let successMessage = `📝 Examen terminé!\nScore: ${percentage.toFixed(1)}%\n${passed ? '✅ Félicitations!' : '📚 Continuez à pratiquer!'}`;
    if (wrongQuestionsList.length > 0) {
      successMessage += `\n\n🤖 Tuteur IA: ${wrongQuestionsList.length} erreur(s) analysée(s).\nDes cours de révision vous sont recommandés.`;
    }
    alert(successMessage);

  } catch (error: any) {
    console.error(' Erreur:', error);
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

const cancelExam = () => {
  setExamMode(false);
  setExamSubmitted(false);
  setExamResult(null);
  setExamAnswers({});
  setExamQuestions([]);
  setGeneratingExam(false);
};


useEffect(() => {
  if (selectedCourse && selectedCourse.id && user?.id && mistakeQuestions.length > 0) {
    
    const timer = setTimeout(() => {
      if (mistakeQuestions.length > 0 && !showRecommendations) {
       
        const toast = document.createElement('div');
        toast.className = 'fixed bottom-4 right-4 bg-indigo-500 text-white px-4 py-2 rounded-lg shadow-lg z-50 cursor-pointer';
        toast.innerHTML = '🤖 Tuteur IA: Cliquez pour voir les cours recommandés';
        toast.onclick = () => {
          analyzeMistakesAndRecommend(mistakeQuestions);
          toast.remove();
        };
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 8000);
      }
    }, 3000);
    
    return () => clearTimeout(timer);
  }
}, [selectedCourse?.id, mistakeQuestions.length, user?.id, showRecommendations]);


useEffect(() => {
  if (selectedCourse && selectedCourse.id && !examMode) {
    
    let isMounted = true;
    
    const loadData = async () => {
      if (!isMounted) return;
      await loadQuestionsForCourse(selectedCourse.id);
      if (user?.id) {
        await loadMistakesFromDB(user.id, selectedCourse.id);
      }
    };
    
    loadData();
    
    return () => {
      isMounted = false;
    };
  }
}, [selectedCourse?.id, examMode, user?.id]);

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
🎬 Mode avec + erreurs: ${stats.mode_plus_erreurs || 'N/A'}
    `);
  } catch (error) {
    console.error('Erreur stats:', error);
    
    const mistakes = mistakeQuestions;
    alert(`
📊 STATISTIQUES D'ERREURS (locale):
━━━━━━━━━━━━━━━━━━━━━━━
📝 Total erreurs: ${mistakes.length}
⚠️ Non révisées: ${mistakes.length}
📚 Cours actuel: ${selectedCourse?.titre || 'N/A'}
🎬 Mode: Vidéo

📋 Liste des erreurs:
${mistakes.slice(0, 5).map((m, i) => `${i+1}. ${m.substring(0, 60)}...`).join('\n')}
    `);
  }
};

  
  const videoMapping: Record<number, { title: string; videoId: string; duration: string; description?: string }> = {
    6: { 
      title: "Formatage du Texte en HTML", 
      videoId: "LkZ-KqxgVQ4", 
      duration: "18:00",
      description: "Apprenez à formater le texte avec les balises HTML"
    },
    11: { 
      title: "Les Liens Hypertextes en HTML", 
      videoId: "gJ_G-gxQRRk", 
      duration: "30:00",
      description: "Maîtrisez la création de liens hypertextes"
    },
    12: { 
      title: "Les Images en HTML", 
      videoId: "FmoYRiepmOE", 
      duration: "25:00",
      description: "Apprenez à intégrer et optimiser des images en HTML"
    },
    8: {  
    title: "Formulaires HTML Avancés",
    videoId: "VLeERv_dR6Q",
    duration: "35:00",
    description: "Maîtrisez la création de formulaires HTML complexes avec validation intégrée"
  },
  9:{
    title:"Semantic HTML Explained (HTML5) | Tags, Structure, Accessibility & SEO",
    videoId:"MFOU30UJKuo",
    duration:"15:19",
    description:"Découvrez les balises sémantiques HTML5 (header, nav, main, article, section, aside, footer) pour une meilleure accessibilité et un meilleur référencement (SEO)."
  },
  10: { 
    title: "CSS Flexbox vs Grid EXPLAINED – The REAL Difference (With Examples)", 
    videoId: "HheRpUCYN9Q",  
    duration: "06:27",
    description: "Comprenez la différence fondamentale entre Flexbox (layout 1D) et Grid (layout 2D). À travers des exemples concrets (cartes, boutons, mise en page complète, en-tête et menu latéral), cette vidéo vous aide à choisir la bonne technologie pour chaque situation."
  },
  13: { 
    title: "HTML Tables - W3Schools Tutorial",
    videoId: "e62D-aayveY",
    duration: "02:29",
    description: "Apprenez à créer et utiliser des tableaux HTML pour organiser des données structurées sur vos pages web."
  },
  14: { 
    title: "HTML Head - Métadonnées et SEO",
    videoId: "WeuVX5x2MJE",
    duration: "01:32",
    description: "Découvrez la balise <head> et son importance pour le SEO, l'accessibilité et les métadonnées. Apprenez à utiliser les balises title, meta, link et script."
  },
  15: { 
    title: "HTML Multimedia - Video, Audio and Plug-ins",
    videoId: "3eSKo66Um9k",
    duration: "11:02",
    description: "Apprenez à intégrer et utiliser du contenu multimédia dans vos pages web. Découvrez les balises HTML5 <video> et <audio>, les formats supportés (MP3, MP4), et les méthodes héritées."
  },
  16: { 
    title: "Learn CSS Media Query In 7 Minutes",
    videoId: "yU7jJ3NbPdA",
    duration: "07:10",
    description: "Découvrez les CSS Media Queries, la façon la plus simple et la plus courante de créer un site web responsive. Apprenez la syntaxe et comment créer des designs responsives."
  },
  17: { 
    title: "CSS - Simple Selectors (Element, ID, Class)",
    videoId: "ZNskBxLVOfs",
    duration: "02:12",
    description: "Apprenez les trois sélecteurs CSS les plus courants : les sélecteurs d'élément, d'ID et de classe. Découvrez comment cibler précisément les éléments HTML à styliser."
  },
  18: { 
    title: "CSS - Colors Introduction - W3Schools.com",
    videoId: "q0uWmobMf6I",
    duration: "03:01",
    description: "Introduction aux couleurs en CSS. Apprenez les différents formats pour définir des couleurs : noms, HEX, RGB, et HSL. Comprenez comment appliquer des couleurs au texte, aux arrière-plans et aux autres éléments."
  },
  19: { 
    title: "CSS - Background Images - W3Schools.com",
    videoId: "FMyU_h8m-0c",
    duration: "01:26",
    description: "Apprenez à utiliser les images d'arrière-plan en CSS. Découvrez comment appliquer, positionner, répéter et dimensionner les images d'arrière-plan pour enrichir vos pages web."
  },
  20: { 
    title: "W3Schools CSS Border Tutorial",
    videoId: "xfkMw3mGHAc",
    duration: "08:50",
    description: "Apprenez à styliser, dimensionner et colorer les bordures autour des éléments HTML. Découvrez les différents styles (solid, dotted, dashed, double, groove, ridge, inset, outset), les épaisseurs, les couleurs, et comment appliquer des bordures différentes sur chaque côté."
  },
  22: { 
    title: "W3Schools CSS Margin Tutorial",
    videoId: "UlG0ZAM65fQ",
    duration: "04:16",
    description: "Apprenez à utiliser les marges en CSS pour contrôler l'espacement extérieur des éléments. Découvrez margin-top, margin-right, margin-bottom, margin-left, la propriété raccourcie, et le margin collapsing."
  },
  23: { 
    title: "W3Schools CSS Padding Tutorial",
    videoId: "V072uiG5FIg",
    duration: "03:57",
    description: "Apprenez à utiliser le padding en CSS pour contrôler l'espacement intérieur des éléments. Découvrez padding-top, padding-right, padding-bottom, padding-left, la propriété raccourcie, et les différentes unités."
  },
  24: { 
    title: "W3Schools CSS Text Tutorial",
    videoId: "jteI1EmNptY",
    duration: "06:24",
    description: "Apprenez à maîtriser les propriétés CSS pour la mise en forme du texte : alignement (text-align), décoration (text-decoration), transformation (text-transform), espacement (letter-spacing, word-spacing), hauteur de ligne (line-height), indentation (text-indent) et ombres (text-shadow)."
  },
  25: { 
    title: "W3Schools CSS Font Tutorial",
    videoId: "9jnaJgHg_IU",
    duration: "08:26",
    description: "Apprenez à maîtriser les propriétés CSS pour les polices : font-family, font-size, font-weight, font-style. Découvrez les familles génériques (serif, sans-serif, monospace), le système de fallback, les unités de taille et les bonnes pratiques pour l'accessibilité."
  },
  26: { 
    title: "W3Schools CSS Links Tutorial",
    videoId: "KM8J0J0DuQs",
    duration: "04:23",
    description: "Apprenez à styliser les liens hypertextes en CSS avec les pseudo-classes :link, :visited, :hover et :active. Découvrez l'importance de l'ordre des règles (LoVe HA!) et comment créer des liens interactifs."
  },
  27: { 
    title: "W3Schools CSS Lists Tutorial",
    videoId: "-AyiZNtT4JE",
    duration: "05:14",
    description: "Apprenez à styliser les listes HTML en CSS : list-style-type (changer les puces et numéros), list-style-position (position des marqueurs), list-style-image (images personnalisées), et la propriété raccourcie list-style."
  },
  28: { 
    title: "W3Schools CSS Tables Tutorial",
    videoId: "R73fiRbm2mM",
    duration: "05:13",
    description: "Apprenez à styliser les tableaux HTML en CSS : bordures, border-collapse, dimensions, alignement (text-align, vertical-align), padding, couleurs, arrière-plans et tableaux responsives."
  },
  29: { 
    title: "W3Schools CSS Display and Visibility Tutorial",
    videoId: "gVt4qcfNLto",
    duration: "04:57",
    description: "Apprenez la différence entre display et visibility en CSS. Découvrez visibility: hidden vs display: none, les éléments block vs inline, et comment créer des menus horizontaux."
  },
  30: { 
    title: "W3Schools CSS Positioning Tutorial",
    videoId: "kowh52NmZis",
    duration: "06:36",
    description: "Apprenez à maîtriser le positionnement CSS : static, relative, absolute, fixed et sticky. Découvrez comment contrôler précisément la position des éléments sur votre page, créer des menus fixes, des tooltips et des en-têtes collants."
  },
  31: { 
    title: "Learn CSS overflow in 3 minutes! 🌊",
    videoId: "d7cH8geV2dY",
    duration: "03:23",
    description: "Apprenez à maîtriser la propriété CSS overflow pour gérer le contenu qui dépasse de son conteneur. Découvrez les valeurs visible, hidden, clip, scroll et auto."
  },
  32: { 
    title: "W3Schools CSS Float Tutorial",
    videoId: "dK-NwjlhmqU",
    duration: "03:13",
    description: "Apprenez à utiliser la propriété CSS float pour positionner des éléments à gauche ou à droite, permettant au texte de s'enrouler autour. Découvrez comment créer des galeries d'images et utiliser la propriété clear."
  },
  33: { 
    title: "JavaScript - Introduction - W3Schools.com",
    videoId: "zofMnllkVfI",
    duration: "02:49",
    description: "Découvrez JavaScript, le langage de programmation du web. Apprenez à modifier le contenu HTML, les attributs, les styles CSS, ainsi qu'à masquer et afficher des éléments."
  },
  34: { 
    title: "JavaScript - Variables - W3Schools.com",
    videoId: "7xStNKTM3bE",
    duration: "03:38",
    description: "Apprenez à utiliser les variables en JavaScript : déclaration avec var, let, const, règles de nommage, types de données (nombres et chaînes), et opérateur d'assignation."
  },
  35: { 
    title: "Data Types - Beau teaches JavaScript",
    videoId: "808eYu9B9Yw",
    duration: "06:33",
    description: "Apprenez les 7 types de données fondamentaux en JavaScript : Boolean, Null, Undefined, Number, String, Symbol et Object. Découvrez comment chaque type se comporte et les différences entre null et undefined."
  },
  36: { 
    title: "JavaScript - Arithmetic Operators - W3Schools.com",
    videoId: "yEJ94pMiT-o",
    duration: "03:27",
    description: "Apprenez à utiliser les opérateurs JavaScript : arithmétiques (+, -, *, /, %, **), d'assignation, de comparaison et logiques. Découvrez la concaténation de chaînes et la différence entre addition et concaténation."
  },
  37: { 
    title: "If statements in JavaScript are easy 🤔",
    videoId: "PgUXiprlg1k",
    duration: "15:57",
    description: "Apprenez à utiliser les conditions en JavaScript : if, else, else if. Découvrez comment prendre des décisions dans votre code, utiliser les opérateurs de comparaison et logiques, et maîtriser les booléens."
  },
  38: { 
    title: "JavaScript Loops",
    videoId: "s9wW2PpJsmQ",
    duration: "06:48",
    description: "Apprenez à utiliser les boucles en JavaScript, en particulier la boucle for. Découvrez l'initialisation, la condition, l'incrément, comment compter de 0 à n, compter à rebours, filtrer avec des conditions internes, et parcourir des tableaux."
  },
   39: { 
    title: "String Methods - JavaScript Tutorial - w3Schools - Chapter-17 English",
    videoId: "hVS5p5zgBrs",
    duration: "12:01",
    description: "Apprenez à manipuler les chaînes de caractères en JavaScript. Découvrez les méthodes essentielles comme length, toUpperCase(), includes(), trim(), split() et leurs applications pratiques."
  },
  40: { 
    title: "JavaScript Numbers, Number Methods, isNaN | JavaScript Tutorial for Beginners",
    videoId: "3Ul9gYweEPs",
    duration: "06:01",
    description: "Apprenez à manipuler les nombres en JavaScript : entiers et décimaux, conversion de chaînes en nombres (Number(), parseFloat(), parseInt()), méthodes (isInteger(), toFixed()), et compréhension de NaN."
  },
  41: { 
    title: "JavaScript FUNCTIONS are easy! 📞",
    videoId: "HFaxylC7bUc",
    duration: "12:13",
    description: "Apprenez à utiliser les fonctions en JavaScript : déclaration, appel, paramètres, arguments, mot-clé return, fonctions mathématiques, vérification pair/impair, validation d'email."
  },
  42: { 
    title: "Learn JavaScript OBJECTS in 7 minutes! 🧍",
    videoId: "lo7o91qLzxc",
    duration: "07:00",
    description: "Apprenez à créer et utiliser des objets en JavaScript : collections de propriétés (données) et méthodes (fonctions), notation pointée, modélisation d'entités du monde réel."
  },
  43: { 
    title: "Learn JavaScript ARRAYS in 8 minutes! 🗃",
    videoId: "yQ1fz8LY354",
    duration: "08:05",
    description: "Apprenez à utiliser les tableaux en JavaScript : création, accès aux éléments avec indices, méthodes push/pop/unshift/shift, propriété length, indexOf, parcours avec for...of, tri avec sort et reverse."
  },
  44: { 
    title: "Set in JavaScript",
    videoId: "YiIKUhtqeRM",
    duration: "07:01",
    description: "Apprenez à utiliser les Sets en JavaScript : stockage de valeurs uniques, création avec new Set(), méthodes add(), has(), delete(), clear(), propriété size, parcours avec forEach() et for...of."
  },
  45: { 
    title: "Map in Javascript",
    videoId: "flveJ5_-iFA",
    duration: "07:34",
    description: "Apprenez à utiliser les Maps en JavaScript : stockage de paires clé-valeur, création avec new Map(), méthodes set(), get(), has(), delete(), clear(), propriété size, parcours avec forEach() et for...of, différence entre Map et Object."
  },
  46: { 
    title: "Why the Math object in JavaScript is useful 🧮",
    videoId: "uy-1WNqecnI",
    duration: "05:36",
    description: "Apprenez à utiliser l'objet Math en JavaScript : constantes (PI, E), méthodes d'arrondi (round, floor, ceil, trunc), puissances (pow), racines (sqrt), logarithmes, trigonométrie, valeur absolue (abs), signe (sign), maximum/minimum (max, min), et nombres aléatoires (random)."
  },
   47: { 
    title: "JavaScript Regular Expression | JavaScript Regex Tutorial",
    videoId: "9obK2d255mE",
    duration: "06:27",
    description: "Apprenez à utiliser les expressions régulières (RegEx) en JavaScript : création de regex, flags (g, i, m), méthodes test() et exec(), méthodes des chaînes match(), search(), replace(), classes de caractères, quantificateurs, validation d'email et extraction de données."
  },
  48: { 
    title: "Event Handlers vs Event Listeners in JavaScript 👨‍💻💯",
    videoId: "xogpUfUL5kY",
    duration: "04:57",
    description: "Apprenez la différence entre les gestionnaires d'événements (onclick) et les écouteurs d'événements (addEventListener) en JavaScript. Découvrez pourquoi les event listeners sont préférés pour les applications modernes."
  }
  };

  

  const jsEventsChapters = [
  { time: "00:00", title: "Introduction aux événements", duration: "0:12" },
  { time: "00:12", title: "Les événements : clics, survols, etc.", duration: "0:31" },
  { time: "00:43", title: "Utilisation des gestionnaires d'événements (onclick)", duration: "1:06" },
  { time: "01:49", title: "Utilisation des écouteurs d'événements (addEventListener)", duration: "1:11" },
  { time: "03:00", title: "Différence clé démontrée", duration: "1:18" },
  { time: "04:18", title: "Bonne pratique : préférer les écouteurs", duration: "0:28" },
  { time: "04:46", title: "Conclusion - Handlers vs Listeners", duration: "0:11" }
];

const jsEventsVideoPoints = [
  { time: "0:00", title: "Introduction", description: "Les événements permettent de réagir aux actions de l'utilisateur comme les clics de bouton." },
  { time: "0:43", title: "Event Handlers", description: "onclick ne permet qu'une seule fonction par événement. Les nouvelles assignations remplacent les précédentes." },
  { time: "1:49", title: "Event Listeners", description: "addEventListener peut attacher plusieurs fonctions au même événement." },
  { time: "3:00", title: "Différence clé", description: "Avec handlers, le second remplace le premier. Avec listeners, les deux s'exécutent." },
  { time: "4:18", title: "Bonne pratique", description: "Préférez les écouteurs d'événements aux gestionnaires pour plus de flexibilité." }
];

const jsEventsTranscript = [
  { time: "00:00", text: "Bienvenue dans ce cours sur les événements en JavaScript. Les événements permettent de réagir aux actions de l'utilisateur comme les clics de bouton ou les survols de souris." },
  { time: "00:12", text: "Les événements incluent des actions comme les clics de bouton ou les survols de souris. Il existe deux façons principales de les gérer." },
  { time: "00:43", text: "Les gestionnaires d'événements comme onclick ne permettent qu'une seule fonction par événement. Exemple avec un bouton qui affiche un message dans la console." },
  { time: "01:49", text: "Les écouteurs d'événements avec addEventListener permettent d'attacher plusieurs fonctions au même événement, ce qui les rend plus flexibles." },
  { time: "03:00", text: "La différence clé : avec deux handlers onclick, le second remplace le premier. Avec deux addEventListener, les deux s'exécutent. C'est démontré avec des exemples concrets." },
  { time: "04:18", text: "Bonne pratique : préférez les écouteurs d'événements aux gestionnaires. Ils sont plus flexibles et évolutifs pour les applications complexes." },
  { time: "04:46", text: "En conclusion, les handlers permettent une seule fonction par événement, les listeners permettent plusieurs fonctions. Les écouteurs d'événements sont recommandés pour le développement JavaScript moderne." }
];

  const jsRegexChapters = [
  { time: "00:00", title: "Introduction aux expressions régulières", duration: "0:20" },
  { time: "00:20", title: "Qu'est-ce qu'une expression régulière ?", duration: "0:45" },
  { time: "01:05", title: "Créer une expression régulière", duration: "1:05" },
  { time: "02:10", title: "Les flags (g, i, m)", duration: "0:50" },
  { time: "03:00", title: "Classes de caractères", duration: "1:15" },
  { time: "04:15", title: "Exemples pratiques : validation email", duration: "1:35" },
  { time: "05:50", title: "Méthodes match, search, replace", duration: "0:40" },
  { time: "06:30", title: "Conclusion - Regex pour le traitement de texte", duration: "0:00" }
];

const jsRegexVideoPoints = [
  { time: "0:00", title: "Introduction", description: "Les regex sont des séquences qui définissent des motifs de recherche." },
  { time: "1:05", title: "Création", description: "Littéral /pattern/ ou constructeur new RegExp()." },
  { time: "2:10", title: "Flags", description: "g (global), i (insensible à la casse), m (multiligne)." },
  { time: "3:00", title: "Classes", description: "[a-z] lettres, [0-9] chiffres, \\d chiffres, \\w alphanumérique, \\s espace." },
  { time: "4:15", title: "Validation email", description: "Regex pour vérifier la présence de @ et d'un domaine valide." },
  { time: "5:50", title: "Méthodes", description: "match() tableau, search() index, replace() remplacement." }
];

const jsRegexTranscript = [
  { time: "00:00", text: "Bienvenue dans ce cours sur les expressions régulières en JavaScript. Les expressions régulières sont des séquences de caractères qui définissent des motifs de recherche." },
  { time: "00:20", text: "Une expression régulière permet de rechercher, extraire ou remplacer du texte dans une chaîne. C'est un outil puissant pour la manipulation de texte." },
  { time: "01:05", text: "On peut créer une regex de deux façons : avec le littéral /pattern/ ou avec le constructeur new RegExp. Le littéral est recommandé pour sa simplicité." },
  { time: "02:10", text: "Les flags modifient le comportement de la recherche. g pour global (trouve toutes les occurrences), i pour insensible à la casse, m pour multiligne." },
  { time: "03:00", text: "Les classes de caractères : [a-z] pour les lettres minuscules, [0-9] pour les chiffres, \\d pour les chiffres, \\w pour les caractères alphanumériques, \\s pour les espaces." },
  { time: "04:15", text: "Exemple pratique : validation d'email. Une regex peut vérifier qu'un email contient @ et un domaine valide. On utilise la méthode test() pour valider." },
  { time: "05:50", text: "match() retourne un tableau des correspondances. search() retourne l'index de la première correspondance. replace() remplace les correspondances par un nouveau texte." },
  { time: "06:30", text: "En conclusion, les regex sont un outil puissant pour le traitement de texte. Utilisez-les pour la validation, la recherche et le formatage de données." }
];

  const jsMathChapters = [
  { time: "00:00", title: "Introduction à l'objet Math", duration: "0:06" },
  { time: "00:06", title: "Constantes Mathématiques (PI, E)", duration: "0:56" },
  { time: "01:02", title: "Méthodes d'arrondi (round, floor, ceil, trunc)", duration: "1:16" },
  { time: "02:18", title: "Puissances et racines (pow, sqrt)", duration: "0:35" },
  { time: "02:53", title: "Logarithmes (log, log10, log2)", duration: "0:13" },
  { time: "03:06", title: "Fonctions trigonométriques", duration: "0:38" },
  { time: "03:44", title: "Valeur absolue et signe (abs, sign)", duration: "0:43" },
  { time: "04:27", title: "Maximum et Minimum (max, min)", duration: "0:47" },
  { time: "05:14", title: "Conclusion - Outil puissant pour les maths", duration: "0:22" }
];

const jsMathVideoPoints = [
  { time: "0:00", title: "Introduction", description: "Math est un objet intégré avec constantes et méthodes pour les opérations mathématiques." },
  { time: "0:06", title: "Constantes", description: "Math.PI pour π, Math.E pour la constante d'Euler." },
  { time: "1:02", title: "Arrondis", description: "round (au plus proche), floor (vers le bas), ceil (vers le haut), trunc (supprime décimales)." },
  { time: "2:18", title: "Puissances", description: "Math.pow(x,y) élève x à la puissance y, Math.sqrt() racine carrée." },
  { time: "2:53", title: "Logarithmes", description: "Math.log() logarithme naturel, Math.log10() base 10, Math.log2() base 2." },
  { time: "3:06", title: "Trigonométrie", description: "Math.sin(), Math.cos(), Math.tan() travaillent avec radians." },
  { time: "3:44", title: "Valeur absolue", description: "Math.abs() retourne la valeur absolue, Math.sign() indique positif/négatif/zéro." },
  { time: "4:27", title: "Max et Min", description: "Math.max() trouve la plus grande valeur, Math.min() la plus petite." }
];

const jsMathTranscript = [
  { time: "00:00", text: "Bienvenue dans ce cours sur l'objet Math en JavaScript. Math est un objet intégré qui fournit des constantes et méthodes pour les opérations mathématiques." },
  { time: "00:06", text: "L'objet Math fournit des constantes utiles comme Math.PI pour le nombre pi et Math.E pour la constante d'Euler. Ces constantes évitent de les définir manuellement." },
  { time: "01:02", text: "Les méthodes d'arrondi : Math.round arrondit à l'entier le plus proche. Math.floor arrondit toujours vers le bas. Math.ceil arrondit toujours vers le haut. Math.trunc supprime la partie décimale." },
  { time: "02:18", text: "Math.pow permet d'élever un nombre à une puissance. Math.sqrt calcule la racine carrée. Par exemple, Math.pow(2,3) donne 8, Math.sqrt(16) donne 4." },
  { time: "02:53", text: "Math.log calcule le logarithme naturel. Math.log10 et Math.log2 calculent les logarithmes en base 10 et base 2." },
  { time: "03:06", text: "Les fonctions trigonométriques comme Math.sin, Math.cos, Math.tan travaillent avec des radians. Par exemple, pour 45 degrés, on convertit d'abord en radians." },
  { time: "03:44", text: "Math.abs retourne la valeur absolue d'un nombre. Math.sign indique si un nombre est positif, négatif ou nul, retournant 1, -1 ou 0." },
  { time: "04:27", text: "Math.max trouve la plus grande valeur parmi les arguments. Math.min trouve la plus petite. On peut aussi les utiliser avec l'opérateur spread sur un tableau." },
  { time: "05:14", text: "En conclusion, l'objet Math est un outil puissant pour les opérations mathématiques. Il fournit des constantes et méthodes essentielles pour les arrondis, puissances, racines, trigonométrie et comparaisons." }
];

  const jsMapsChapters = [
  { time: "00:00", title: "Introduction à Map", duration: "0:30" },
  { time: "00:30", title: "Map stocke des paires clé-valeur", duration: "0:42" },
  { time: "01:12", title: "Créer une Map avec new Map()", duration: "0:53" },
  { time: "02:05", title: "Ajouter des entrées avec set", duration: "0:55" },
  { time: "03:00", title: "Récupérer des valeurs avec get", duration: "0:45" },
  { time: "03:45", title: "Vérifier des clés avec has", duration: "0:35" },
  { time: "04:20", title: "Parcourir une Map avec forEach et for...of", duration: "1:50" },
  { time: "06:10", title: "Conclusion - Map vs Object", duration: "1:24" }
];

const jsMapsVideoPoints = [
  { time: "0:00", title: "Introduction", description: "Map stocke des paires clé-valeur et préserve l'ordre d'insertion." },
  { time: "1:12", title: "Création", description: "new Map() pour créer une Map. Exemple: codes de pays." },
  { time: "2:05", title: ".set()", description: "Ajoute une nouvelle paire clé-valeur. Peut être chaîné." },
  { time: "3:00", title: ".get()", description: "Retourne la valeur associée à une clé. undefined si inexistante." },
  { time: "3:45", title: ".has()", description: "Vérifie l'existence d'une clé. Retourne true ou false." },
  { time: "4:20", title: "Parcours", description: ".forEach() ou for...of avec déstructuration [key, value]." },
  { time: "6:10", title: "Map vs Object", description: "Map: tout type de clé, size, itérable. Object: clés string uniquement." }
];

const jsMapsTranscript = [
  { time: "00:00", text: "Bienvenue dans ce cours sur les Maps en JavaScript. Map est une structure de données qui stocke des paires clé-valeur, introduite avec ES6." },
  { time: "00:30", text: "Map stocke des paires clé-valeur. Contrairement aux objets, les clés peuvent être de n'importe quel type : chaînes, nombres, objets. L'ordre d'insertion est préservé." },
  { time: "01:12", text: "Pour créer une Map, on utilise le constructeur new Map. On peut aussi l'initialiser avec un tableau de paires clé-valeur, par exemple pour stocker des codes de pays." },
  { time: "02:05", text: "La méthode set permet d'ajouter de nouvelles paires clé-valeur. On peut enchaîner les appels set car il retourne la Map elle-même." },
  { time: "03:00", text: "Pour récupérer une valeur, on utilise get avec la clé. Si la clé n'existe pas, get retourne undefined. C'est très utile pour accéder aux données stockées." },
  { time: "03:45", text: "has permet de vérifier si une clé existe dans la Map. Elle retourne true ou false. C'est utile avant d'appeler get pour éviter les undefined." },
  { time: "04:20", text: "Pour parcourir une Map, on peut utiliser forEach qui reçoit la valeur puis la clé. On peut aussi utiliser for...of qui déstructure chaque entrée en [clé, valeur]." },
  { time: "06:10", text: "En conclusion, Map est flexible et puissant. Différence clé avec Object : Map accepte tout type de clé, a une propriété size, et est directement itérable. Utilisez Map pour des dictionnaires avancés." }
];



  const jsSetsChapters = [
  { time: "00:00", title: "Introduction aux Sets", duration: "0:43" },
  { time: "00:43", title: "Pourquoi utiliser les Sets ?", duration: "0:43" },
  { time: "01:26", title: "Créer un Set (new Set)", duration: "1:11" },
  { time: "02:37", title: "Suppression automatique des doublons", duration: "0:32" },
  { time: "03:09", title: "Ajouter des valeurs avec add", duration: "0:57" },
  { time: "04:06", title: "Parcourir un Set avec forEach", duration: "1:52" },
  { time: "05:58", title: "Vérifier des valeurs avec has", duration: "0:36" },
  { time: "06:34", title: "Conclusion - Set vs Array", duration: "0:27" }
];

const jsSetsVideoPoints = [
  { time: "0:00", title: "Introduction", description: "Set est une structure de données qui stocke des valeurs uniques." },
  { time: "0:43", title: "Pourquoi Sets", description: "Les tableaux permettent les doublons, Set impose l'unicité. Utile pour filtrer les valeurs répétées." },
  { time: "1:26", title: "Création", description: "new Set() pour créer un Set. Exemple: 'bookkeeper' devient un Set de lettres uniques." },
  { time: "2:37", title: "Doublons", description: "Un mot de 10 caractères peut devenir un Set de seulement 6 lettres uniques." },
  { time: "3:09", title: ".add()", description: "Ajoute des valeurs. Les doublons sont ignorés. Fonctionne avec différents types." },
  { time: "4:06", title: "Parcours", description: ".forEach() ou for...of pour itérer. Pas d'indices, uniquement les valeurs." },
  { time: "5:58", title: ".has()", description: "Vérifie l'existence d'une valeur. Sensible à la casse." }
];

const jsSetsTranscript = [
  { time: "00:00", text: "Bienvenue dans ce cours sur les Sets en JavaScript. Set est une structure de données qui stocke des valeurs uniques. Contrairement aux tableaux, les Sets ne permettent pas les doublons." },
  { time: "00:43", text: "Les tableaux autorisent les doublons, mais Set impose l'unicité. C'est très utile pour filtrer les valeurs répétées dans une collection de données." },
  { time: "01:26", text: "Pour créer un Set, on utilise le constructeur new Set. Par exemple, en utilisant le mot 'bookkeeper', on obtient un Set de lettres uniques comme b, o, k, e, p, r." },
  { time: "02:37", text: "Le mot 'bookkeeper' a 10 caractères, mais Set ne stocke que 6 lettres uniques. Les doublons sont automatiquement ignorés lors de la création du Set." },
  { time: "03:09", text: "La méthode add permet d'insérer de nouvelles valeurs. Si on essaie d'ajouter un doublon, il est simplement ignoré. Set fonctionne avec différents types de données." },
  { time: "04:06", text: "Pour parcourir un Set, on utilise la méthode forEach. Il n'y a pas d'indices, l'itération se concentre uniquement sur les valeurs. On peut aussi utiliser la boucle for...of." },
  { time: "05:58", text: "La méthode has vérifie si une valeur existe dans le Set et retourne true ou false. Attention, la vérification est sensible à la casse, donc 'Pomme' et 'pomme' sont différents." },
  { time: "06:34", text: "En conclusion, Set stocke des valeurs uniques, préserve l'ordre d'insertion, et fournit des méthodes simples comme add, has, delete, clear et la propriété size. Contrairement aux tableaux, Set n'a pas d'indices." }
];

  const jsArraysChapters = [
  { time: "00:00", title: "Introduction aux tableaux", duration: "0:01" },
  { time: "00:01", title: "Les tableaux stockent plusieurs valeurs", duration: "1:05" },
  { time: "01:06", title: "Accéder aux éléments avec les indices", duration: "1:10" },
  { time: "02:16", title: "Méthodes push, pop, unshift, shift", duration: "0:56" },
  { time: "03:12", title: "La propriété length", duration: "0:51" },
  { time: "04:03", title: "Trouver des éléments avec indexOf", duration: "0:58" },
  { time: "05:01", title: "Parcourir un tableau avec for...of", duration: "2:19" },
  { time: "07:20", title: "Trier avec sort et inverser avec reverse", duration: "0:28" },
  { time: "07:48", title: "Conclusion - Tableaux pour organiser les données", duration: "0:17" }
];

const jsArraysVideoPoints = [
  { time: "0:00", title: "Introduction", description: "Les tableaux stockent plusieurs valeurs dans une seule variable, entre crochets." },
  { time: "1:06", title: "Accès aux éléments", description: "Les indices commencent à 0. Exemple: fruits[0] donne 'pomme'." },
  { time: "2:16", title: "Méthodes", description: "push (ajout fin), pop (retrait fin), unshift (ajout début), shift (retrait début)." },
  { time: "3:12", title: "length", description: "Propriété dynamique qui donne le nombre d'éléments." },
  { time: "4:03", title: "indexOf", description: "Retourne la position d'un élément, -1 si non trouvé." },
  { time: "5:01", title: "Parcours", description: "Boucle for...of pour parcourir proprement les valeurs." },
  { time: "7:20", title: "sort et reverse", description: "sort trie alphabétiquement, reverse inverse l'ordre." }
];

const jsArraysTranscript = [
  { time: "00:00", text: "Bienvenue dans ce cours sur les tableaux en JavaScript. Les tableaux sont des variables spéciales qui peuvent stocker plusieurs valeurs." },
  { time: "00:01", text: "Les valeurs sont placées entre crochets et séparées par des virgules. Les tableaux aident à organiser des collections de données." },
  { time: "01:06", text: "Pour accéder aux éléments, on utilise des indices qui commencent à 0. Par exemple, fruits[0] donne la première valeur du tableau." },
  { time: "02:16", text: "Les méthodes importantes : push ajoute à la fin, pop retire de la fin, unshift ajoute au début, shift retire du début." },
  { time: "03:12", text: "La propriété length donne le nombre d'éléments dans le tableau. Elle se met à jour dynamiquement quand on ajoute ou retire des éléments." },
  { time: "04:03", text: "indexOf retourne la position d'un élément dans le tableau. Si l'élément n'est pas trouvé, il retourne -1." },
  { time: "05:01", text: "Pour parcourir un tableau, on peut utiliser une boucle for classique ou la boucle for...of qui offre une syntaxe plus propre." },
  { time: "07:20", text: "sort permet de trier les éléments alphabétiquement, et reverse inverse l'ordre du tableau." },
  { time: "07:48", text: "En conclusion, les tableaux sont des structures polyvalentes pour gérer plusieurs valeurs. Ils sont essentiels en JavaScript." }
];

  const jsObjectsChapters = [
  { time: "00:00", title: "Introduction - Qu'est-ce qu'un objet ?", duration: "0:06" },
  { time: "00:06", title: "Les objets : collections de propriétés et méthodes", duration: "0:36" },
  { time: "00:42", title: "Créer un objet personne (SpongeBob)", duration: "1:05" },
  { time: "01:47", title: "Accéder aux propriétés avec dot notation", duration: "0:41" },
  { time: "02:28", title: "Ajouter un deuxième objet (Patrick)", duration: "1:37" },
  { time: "04:05", title: "Ajouter des méthodes (sayHello, eat)", duration: "1:24" },
  { time: "05:29", title: "Les objets exécutent des actions", duration: "1:02" },
  { time: "06:31", title: "Conclusion - Objets pour modéliser le réel", duration: "0:29" }
];

const jsObjectsVideoPoints = [
  { time: "0:00", title: "Introduction", description: "Les objets sont des collections de propriétés et de méthodes." },
  { time: "0:42", title: "Créer un objet", description: "Exemple avec SpongeBob : prénom, nom, âge, statut d'emploi." },
  { time: "1:47", title: "Accès aux propriétés", description: "Utilisez la notation pointée (personnage.prenom)." },
  { time: "2:28", title: "Objets multiples", description: "Chaque objet a besoin d'un nom unique (personnage1, personnage2)." },
  { time: "4:05", title: "Méthodes", description: "Ajoutez des fonctions comme direBonjour et manger pour représenter des actions." },
  { time: "5:29", title: "Actions", description: "Les méthodes permettent aux objets d'exécuter des comportements spécifiques." }
];

const jsObjectsTranscript = [
  { time: "00:00", text: "Bienvenue dans ce cours sur les objets en JavaScript. Les objets sont des collections de propriétés et de méthodes associées." },
  { time: "00:06", text: "Les propriétés décrivent les attributs comme le nom et l'âge. Les méthodes sont des fonctions liées à l'objet qui représentent des actions." },
  { time: "00:42", text: "Exemple avec SpongeBob : prénom, nom de famille, âge, statut d'emploi. Les propriétés sont définies comme des paires clé-valeur." },
  { time: "01:47", text: "Pour accéder aux propriétés, on utilise la notation pointée comme personnage.prenom. Cela fonctionne pour tous les attributs." },
  { time: "02:28", text: "On crée un objet Patrick avec des propriétés similaires. Chaque objet a besoin d'un nom unique comme personnage1, personnage2." },
  { time: "04:05", text: "On ajoute des méthodes comme direBonjour à SpongeBob et Patrick. On peut utiliser des expressions de fonction ou des fonctions fléchées." },
  { time: "05:29", text: "On ajoute une méthode manger avec des messages personnalisés pour chaque personnage. Les méthodes représentent les comportements." },
  { time: "06:31", text: "En conclusion, les objets combinent propriétés et méthodes. Ils sont utiles pour modéliser des entités du monde réel en JavaScript." }
];

  const jsFunctionsChapters = [
  { time: "00:00", title: "Introduction - Qu'est-ce qu'une fonction ?", duration: "0:07" },
  { time: "00:07", title: "Les fonctions comme blocs de code réutilisables", duration: "1:09" },
  { time: "01:16", title: "Appeler (invoquer) une fonction", duration: "0:48" },
  { time: "02:04", title: "Paramètres et arguments", duration: "2:40" },
  { time: "04:44", title: "Le mot-clé return", duration: "1:56" },
  { time: "06:40", title: "Fonctions mathématiques", duration: "0:57" },
  { time: "07:37", title: "Vérifier si un nombre est pair", duration: "1:59" },
  { time: "09:36", title: "Validation d'email avec includes()", duration: "2:34" },
  { time: "12:10", title: "Conclusion - Réutilisez vos fonctions", duration: "0:03" }
];

const jsFunctionsVideoPoints = [
  { time: "0:00", title: "Introduction", description: "Une fonction est un bloc de code réutilisable qui effectue une tâche spécifique." },
  { time: "1:16", title: "Appeler une fonction", description: "Utilisez le nom de la fonction suivi de parenthèses pour l'exécuter." },
  { time: "2:04", title: "Paramètres et arguments", description: "Les paramètres sont des placeholders dans la définition. Les arguments sont les valeurs passées." },
  { time: "4:44", title: "return", description: "return arrête la fonction et renvoie une valeur. Une fonction peut retourner n'importe quel type de données." },
  { time: "7:37", title: "Nombre pair/impair", description: "Utilisez l'opérateur modulo % pour vérifier si un nombre est pair." },
  { time: "9:36", title: "Validation email", description: "Utilisez includes() pour vérifier la présence du caractère '@'." }
];

const jsFunctionsTranscript = [
  { time: "00:00", text: "Bienvenue dans ce cours sur les fonctions en JavaScript. Les fonctions sont des blocs de code réutilisables qui effectuent des tâches spécifiques." },
  { time: "00:07", text: "Une fonction est déclarée une fois et peut être exécutée plusieurs fois quand on en a besoin. Exemple : une fonction 'Joyeux Anniversaire' qui affiche des paroles." },
  { time: "01:16", text: "Pour appeler une fonction, on utilise son nom suivi de parenthèses. Les fonctions peuvent être exécutées plusieurs fois. Les parenthèses sont essentielles." },
  { time: "02:04", text: "Les fonctions peuvent accepter des valeurs appelées arguments. Les paramètres sont des placeholders dans la fonction. Exemple : passer un nom et un âge pour personnaliser le message." },
  { time: "04:44", text: "Le mot-clé return permet à une fonction de renvoyer une valeur. Exemple : une fonction addition(x, y) retourne la somme. On peut stocker le résultat dans une variable." },
  { time: "06:40", text: "Les fonctions mathématiques : soustraction retourne la différence, multiplication retourne le produit, division retourne le quotient." },
  { time: "07:37", text: "Pour vérifier si un nombre est pair, on utilise l'opérateur modulo. On peut utiliser un if/else ou un opérateur ternaire pour une syntaxe plus concise." },
  { time: "09:36", text: "Pour valider un email, on crée une fonction qui vérifie si la chaîne contient le caractère '@' avec la méthode includes(). On peut utiliser un opérateur ternaire." },
  { time: "12:10", text: "En conclusion, les fonctions sont des blocs de code réutilisables. Les paramètres et arguments permettent la flexibilité, et return permet de produire des résultats." }
];



  const jsNumbersChapters = [
  { time: "00:00", title: "Introduction aux nombres", duration: "0:08" },
  { time: "00:08", title: "Entiers et décimaux", duration: "1:17" },
  { time: "01:25", title: "Comparaison de nombres", duration: "0:40" },
  { time: "02:05", title: "Convertir des chaînes en nombres", duration: "0:50" },
  { time: "02:55", title: "Conversion booléenne", duration: "0:16" },
  { time: "03:11", title: "Méthodes Number : isInteger, parseFloat, toFixed, parseInt", duration: "1:08" },
  { time: "04:19", title: "Enchaînement de méthodes", duration: "0:50" },
  { time: "05:09", title: "Comprendre NaN (isNaN vs Number.isNaN)", duration: "0:37" },
  { time: "05:46", title: "Conclusion", duration: "0:15" }
];

const jsNumbersVideoPoints = [
  { time: "0:00", title: "Introduction", description: "Les nombres peuvent être des entiers ou des décimaux (floats)." },
  { time: "1:25", title: "Comparaison", description: "Comparer des nombres et des chaînes avec la même valeur retourne false en raison du type différent." },
  { time: "2:05", title: "Conversion", description: "Number() convertit une chaîne en nombre. Les conversions invalides retournent NaN." },
  { time: "2:55", title: "Booléens", description: "Number(true) = 1, Number(false) = 0." },
  { time: "3:11", title: "Méthodes", description: "Number.isInteger(), parseFloat(), toFixed(), parseInt()." },
  { time: "5:09", title: "NaN", description: "Number.isNaN() est plus fiable que isNaN() pour détecter NaN." }
];

const jsNumbersTranscript = [
  { time: "00:00", text: "Bienvenue dans ce cours sur les nombres en JavaScript. Les nombres sont l'un des types de données les plus fondamentaux." },
  { time: "00:08", text: "JavaScript gère deux types de nombres : les entiers (nombres sans virgule) et les décimaux (nombres avec virgule). Le langage ignore les zéros finaux sauf si le nombre contient des décimales." },
  { time: "01:25", text: "La comparaison entre entiers et décimaux montre des différences. Comparer un nombre et une chaîne avec la même valeur retourne false en raison de la différence de type." },
  { time: "02:05", text: "La fonction Number() convertit une chaîne en nombre. Si la conversion échoue, elle retourne NaN, ce qui signifie 'Not a Number'." },
  { time: "02:55", text: "Number(true) retourne 1, Number(false) retourne 0. Cela montre que true équivaut à 1 et false à 0 en JavaScript." },
  { time: "03:11", text: "Les méthodes importantes : Number.isInteger() vérifie si une valeur est un entier, parseFloat() convertit en décimal, toFixed() limite les décimales et retourne une chaîne, parseInt() extrait un entier." },
  { time: "04:19", text: "On peut chaîner les méthodes pour plus d'efficacité. Notez que toFixed() retourne déjà une chaîne, donc toString() est souvent redondant." },
  { time: "05:09", text: "NaN est une valeur spéciale. Number.isNaN() vérifie si la valeur est NaN ET de type number. isNaN() globale vérifie seulement si la valeur n'est pas un nombre, ce qui peut être trompeur." },
  { time: "05:46", text: "En conclusion, apprenez à manipuler les nombres avec ces méthodes. Utilisez Number.isNaN() plutôt que isNaN() pour éviter les confusions." }
];

  const jsStringMethodsChapters = [
  { time: "00:00", title: "Introduction aux chaînes de caractères", duration: "0:22" },
  { time: "00:22", title: "Définition et importance des strings", duration: "1:23" },
  { time: "01:45", title: "Pourquoi les méthodes des chaînes sont importantes", duration: "1:23" },
  { time: "03:08", title: "Méthodes de base : length, toUpperCase, includes", duration: "1:09" },
  { time: "04:17", title: "Exemple pratique : trim()", duration: "1:39" },
  { time: "05:56", title: "Exemple pratique : includes()", duration: "1:19" },
  { time: "07:15", title: "Exemple pratique : split()", duration: "3:21" },
  { time: "10:36", title: "Conclusion - Maîtriser les méthodes des chaînes", duration: "1:25" }
];

const jsStringMethodsVideoPoints = [
  { time: "0:00", title: "Introduction", description: "Les chaînes sont des séquences de caractères utilisées pour stocker et traiter du texte." },
  { time: "1:45", title: "Importance", description: "Validation d'emails, extraction de hashtags, formatage de données, nettoyage de texte." },
  { time: "3:08", title: "Méthodes de base", description: ".length (nombre de caractères), .toUpperCase() (majuscules), .includes() (recherche booléenne)." },
  { time: "4:17", title: ".trim()", description: "Supprime les espaces au début et à la fin. Idéal pour nettoyer les entrées utilisateur." },
  { time: "5:56", title: ".includes()", description: "Recherche une sous-chaîne, retourne true/false. Utile pour analyser des avis." },
  { time: "7:15", title: ".split()", description: "Convertit une chaîne en tableau. Exemple : CSV en tableau, extraction d'username d'email." }
];

const jsStringMethodsTranscript = [
  { time: "00:00", text: "Bienvenue dans ce cours sur les chaînes de caractères en JavaScript. Les chaînes sont des séquences de caractères utilisées pour stocker et traiter du texte." },
  { time: "00:22", text: "Les chaînes sont délimitées par des guillemets simples ou doubles. Elles sont immuables, ce qui signifie que toute modification crée une nouvelle chaîne." },
  { time: "01:45", text: "Les méthodes des chaînes sont essentielles pour valider les entrées comme les emails et mots de passe, extraire des hashtags, formater des numéros de téléphone, et nettoyer des données." },
  { time: "03:08", text: "length compte le nombre de caractères. toUpperCase convertit tout en majuscules. includes vérifie si une sous-chaîne existe et retourne true ou false." },
  { time: "04:17", text: "trim supprime les espaces au début et à la fin d'une chaîne. C'est très utile pour nettoyer les entrées utilisateur dans les formulaires." },
  { time: "05:56", text: "includes recherche des mots spécifiques dans un texte. Elle retourne un booléen, ce qui est utile pour analyser des avis ou des commentaires." },
  { time: "07:15", text: "split convertit une chaîne CSV en tableau en découpant au niveau des virgules. On peut aussi l'utiliser pour extraire le nom d'utilisateur d'un email." },
  { time: "10:36", text: "Pour maîtriser les chaînes, apprenez la syntaxe, les arguments et les types de retour des méthodes. Pratiquez avec au moins 10 méthodes essentielles." }
];

  const jsLoopsChapters = [
  { time: "00:00", title: "Introduction - Pourquoi utiliser des boucles", duration: "0:04" },
  { time: "00:04", title: "Pourquoi les boucles sont importantes", duration: "0:50" },
  { time: "00:54", title: "Structure de la boucle for", duration: "1:22" },
  { time: "02:16", title: "Déroulement d'une boucle for", duration: "1:28" },
  { time: "03:44", title: "Suivi des itérations", duration: "0:54" },
  { time: "04:38", title: "Variations de boucles", duration: "1:16" },
  { time: "05:54", title: "Conclusion - Flexibilité des boucles", duration: "0:54" }
];

const jsLoopsVideoPoints = [
  { time: "0:00", title: "Introduction", description: "Les boucles permettent de répéter des actions efficacement sans code répétitif." },
  { time: "0:54", title: "Structure for", description: "Initialisation (let i=0), condition (i<5), incrément (i++)." },
  { time: "2:16", title: "Déroulement", description: "La boucle s'exécute tant que la condition est vraie, i s'incrémente après chaque itération." },
  { time: "3:44", title: "Itérations", description: "i prend les valeurs 0,1,2,3,4. La boucle s'arrête quand i=5." },
  { time: "4:38", title: "Variations", description: "Démarrer à 1, utiliser if interne pour filtrer (nombres impairs), boucle inversée avec i--." }
];

const jsLoopsTranscript = [
  { time: "00:00", text: "Bienvenue dans ce cours sur les boucles en JavaScript. Les boucles permettent de répéter des actions efficacement sans écrire de code répétitif." },
  { time: "00:04", text: "Répéter du code manuellement est inefficace. Les boucles automatisent la répétition avec une syntaxe plus propre et plus lisible." },
  { time: "00:54", text: "Une boucle for comporte trois parties : l'initialisation avec let i = 0, la condition avec i < 5, et l'incrément avec i++. Le code s'exécute tant que la condition est vraie." },
  { time: "02:16", text: "La boucle s'exécute tant que la condition est vraie. i s'incrémente après chaque itération. Par exemple, elle peut afficher Hello World cinq fois." },
  { time: "03:44", text: "La console affiche les valeurs de i de 0 à 4. La condition devient fausse quand i atteint 5, et la boucle s'arrête." },
  { time: "04:38", text: "On peut commencer à 1 et continuer tant que i <= 5. On peut utiliser if à l'intérieur pour n'afficher que les nombres impairs. On peut aussi faire une boucle inversée en commençant à 5 et en décrémentant." },
  { time: "05:54", text: "Les boucles sont flexibles pour différents scénarios. Les boucles inversées sont moins courantes mais utiles dans certains problèmes. Expérimentez avec les boucles." }
];

  const jsConditionsChapters = [
  { time: "00:00", title: "Introduction aux conditions", duration: "0:10" },
  { time: "00:10", title: "Pourquoi les programmes ont besoin de prendre des décisions", duration: "0:28" },
  { time: "00:38", title: "L'instruction if de base", duration: "0:34" },
  { time: "01:12", title: "Ajouter else (bloc alternatif)", duration: "0:33" },
  { time: "01:45", title: "Utiliser else if (multiples conditions)", duration: "0:45" },
  { time: "02:30", title: "Exemple pratique : système de notation", duration: "0:35" },
  { time: "03:05", title: "Conclusion - Résumé des conditions", duration: "0:25" }
];

const jsConditionsVideoPoints = [
  { time: "0:00", title: "Introduction", description: "Les conditions permettent aux programmes de prendre des décisions." },
  { time: "0:38", title: "if", description: "Exécute un bloc de code si la condition est vraie." },
  { time: "1:12", title: "else", description: "Fournit un bloc alternatif si la condition du if est fausse." },
  { time: "1:45", title: "else if", description: "Permet de vérifier plusieurs conditions à la suite." },
  { time: "2:30", title: "Exemple pratique", description: "Système de notation avec différentes fourchettes de notes." },
  { time: "3:05", title: "Conclusion", description: "if, else if et else sont les fondations de la prise de décision en JavaScript." }
];

const jsConditionsTranscript = [
  { time: "00:00", text: "Bienvenue dans ce cours sur les conditions en JavaScript. Les conditions permettent aux programmes de prendre des décisions en fonction de différentes situations." },
  { time: "00:10", text: "Les programmes ont souvent besoin de faire des choix. Par exemple, vérifier si un utilisateur est majeur avant de lui donner accès à un contenu." },
  { time: "00:38", text: "L'instruction if est l'outil de base. Exemple : if (nombre > autreNombre) { console.log('Condition vraie'); }. Le code s'exécute seulement si la condition est vraie." },
  { time: "01:12", text: "else fournit un bloc alternatif. Si la condition est fausse, le bloc else s'exécute. Exemple : if (majeur) { accès } else { refus }." },
  { time: "01:45", text: "else if permet de vérifier plusieurs conditions à la suite. Par exemple, pour un système de notation : note >= 90 pour Excellent, note >= 80 pour Très bien, etc." },
  { time: "02:30", text: "Dans un système de notation réel, on utilise plusieurs conditions pour couvrir toutes les fourchettes de notes, du A+ au F." },
  { time: "03:05", text: "if, else if et else sont les fondations de la prise de décision en JavaScript. Entraînez-vous avec différentes conditions." }
];

  const jsOperatorsChapters = [
  { time: "00:00", title: "Introduction aux opérateurs JavaScript", duration: "0:15" },
  { time: "00:15", title: "L'opérateur d'assignation (=)", duration: "0:30" },
  { time: "00:45", title: "Opérateurs arithmétiques (+, -, *, /, %, **)", duration: "0:30" },
  { time: "01:15", title: "Opérateurs d'assignation composés (+=, -=, *=, /=)", duration: "0:30" },
  { time: "01:45", title: "Opérateurs de comparaison (==, ===, !=, >, <)", duration: "0:30" },
  { time: "02:15", title: "Opérateurs logiques (&&, ||, !)", duration: "0:30" },
  { time: "02:45", title: "Concaténation de chaînes avec +", duration: "0:30" },
  { time: "03:15", title: "Conclusion - Bonnes pratiques", duration: "0:12" }
];

const jsOperatorsVideoPoints = [
  { time: "0:00", title: "Introduction", description: "Les opérateurs permettent d'effectuer des calculs et des comparaisons." },
  { time: "0:15", title: "Assignation (=)", description: "Assigne une valeur à une variable. let x = 10." },
  { time: "0:45", title: "Arithmétiques", description: "+ addition, - soustraction, * multiplication, / division, % modulo, ** exponentiation." },
  { time: "1:15", title: "Assignation composée", description: "+=, -=, *=, /= combinent opération et assignation. x += 5 équivaut à x = x + 5." },
  { time: "1:45", title: "Comparaison", description: "== (égalité valeur), === (égalité valeur et type), !=, >, <, >=, <=." },
  { time: "2:15", title: "Logiques", description: "&& (ET), || (OU), ! (NON). Retournent true ou false." },
  { time: "2:45", title: "Concaténation", description: "+ concatène les chaînes. 'Bonjour' + ' monde' = 'Bonjour monde'." }
];

const jsOperatorsTranscript = [
  { time: "00:00", text: "Bienvenue dans ce cours sur les opérateurs JavaScript. Les opérateurs permettent d'effectuer des calculs mathématiques, des comparaisons et des opérations logiques." },
  { time: "00:15", text: "L'opérateur d'assignation = assigne une valeur à une variable. Par exemple, let x = 10 assigne la valeur 10 à la variable x." },
  { time: "00:45", text: "Les opérateurs arithmétiques incluent + pour l'addition, - pour la soustraction, * pour la multiplication, / pour la division, % pour le modulo (reste), et ** pour l'exponentiation." },
  { time: "01:15", text: "Les opérateurs d'assignation composés comme +=, -=, *=, /= permettent de combiner une opération arithmétique avec une assignation. x += 5 équivaut à x = x + 5." },
  { time: "01:45", text: "Les opérateurs de comparaison comparent deux valeurs. == compare la valeur, === compare la valeur et le type. >, <, >=, <= comparent les grandeurs." },
  { time: "02:15", text: "Les opérateurs logiques sont && (ET), || (OU) et ! (NON). Ils sont utilisés pour combiner des conditions et retournent true ou false." },
  { time: "02:45", text: "L'opérateur + sert aussi à concaténer des chaînes. 'Bonjour' + ' ' + 'monde' donne 'Bonjour monde'. Attention: 5 + '5' donne '55', pas 10." },
  { time: "03:15", text: "En conclusion, utilisez === plutôt que == pour éviter les conversions de type implicites. Les opérateurs sont essentiels pour manipuler les données." }
];

  const jsDataTypesChapters = [
  { time: "00:00", title: "Introduction aux types de données", duration: "0:12" },
  { time: "00:12", title: "Boolean - Vrai ou Faux", duration: "0:51" },
  { time: "01:03", title: "Null - La valeur nulle", duration: "0:34" },
  { time: "01:37", title: "Undefined - Variable non assignée", duration: "0:55" },
  { time: "02:32", title: "Number - Nombres", duration: "0:39" },
  { time: "03:11", title: "String - Chaînes de caractères", duration: "0:36" },
  { time: "03:47", title: "Symbol - Identifiants uniques (ES6)", duration: "1:47" },
  { time: "05:34", title: "Object - Collections clé-valeur", duration: "0:51" },
  { time: "06:25", title: "Conclusion - Résumé des types", duration: "0:08" }
];

const jsDataTypesVideoPoints = [
  { time: "0:00", title: "Introduction", description: "JavaScript possède sept types de données fondamentaux." },
  { time: "0:12", title: "Boolean", description: "Représente vrai (true) ou faux (false). Exemple : data = true." },
  { time: "1:03", title: "Null", description: "Valeur d'assignation signifiant 'aucune valeur'. Se comporte comme 0 en math." },
  { time: "1:37", title: "Undefined", description: "Variable déclarée mais non assignée. Les opérations donnent NaN." },
  { time: "2:32", title: "Number", description: "Valeurs numériques, entières ou décimales. Exemple : 3.6 + 6.4 = 10." },
  { time: "3:11", title: "String", description: "Texte entre guillemets. Concaténation possible avec l'opérateur +." },
  { time: "3:47", title: "Symbol", description: "Identifiants uniques et immuables (ES6). Deux symboles identiques ne sont pas égaux." },
  { time: "5:34", title: "Object", description: "Collection de paires clé-valeur pour structurer des données complexes." }
];

const jsDataTypesTranscript = [
  { time: "00:00", text: "Bienvenue dans ce cours sur les types de données en JavaScript. JavaScript possède sept types de données fondamentaux." },
  { time: "00:12", text: "Boolean représente une valeur logique, vrai ou faux. Par exemple, true pour 'les booléens règnent', false pour 'les booléens sont ennuyeux'." },
  { time: "01:03", text: "Null est une valeur d'assignation signifiant 'aucune valeur'. Dans les opérations mathématiques, null se comporte comme 0." },
  { time: "01:37", text: "Undefined signifie qu'une variable a été déclarée mais non assignée. Les opérations avec undefined donnent NaN, 'Not a Number'." },
  { time: "02:32", text: "Number représente n'importe quelle valeur numérique, entière ou décimale. Par exemple, 3.6 plus 6.4 donne 10." },
  { time: "03:11", text: "String représente du texte entre guillemets. Les chaînes peuvent être concaténées, par exemple 'Bonjour ' + 'monde'." },
  { time: "03:47", text: "Symbol est un type introduit en ES6 pour créer des identifiants uniques et immuables. Deux symboles avec la même description ne sont pas égaux." },
  { time: "05:34", text: "Object est une collection de paires clé-valeur. Par exemple, on peut créer une voiture avec les propriétés make, model et year." },
  { time: "06:25", text: "En conclusion, maîtrisez ces types pour mieux comprendre comment les valeurs sont stockées. Pratiquez et utilisez votre code pour le bien." }
];

  const jsVariablesChapters = [
  { time: "00:00", title: "Introduction - Que sont les variables ?", duration: "0:06" },
  { time: "00:06", title: "Les variables comme conteneurs de données", duration: "0:27" },
  { time: "00:33", title: "Déclaration des variables (var, let, const)", duration: "0:50" },
  { time: "01:23", title: "Règles de nommage (identifiants)", duration: "0:36" },
  { time: "01:59", title: "L'opérateur d'assignation (=)", duration: "0:31" },
  { time: "02:30", title: "Types de données (nombres et chaînes)", duration: "0:38" },
  { time: "03:08", title: "Conclusion - let vs const vs var", duration: "0:30" }
];

const jsVariablesVideoPoints = [
  { time: "0:00", title: "Introduction", description: "Les variables sont des conteneurs qui stockent des données en mémoire." },
  { time: "0:33", title: "var, let, const", description: "Trois façons de déclarer : var (ancien), let (modifiable), const (non modifiable)." },
  { time: "1:23", title: "Règles de nommage", description: "Lettres, chiffres, $, _. Commence par lettre, $ ou _. Pas de mots réservés." },
  { time: "1:59", title: "Assignation", description: "= assigne une valeur. x = x + 3 met à jour la valeur de x." },
  { time: "2:30", title: "Types de données", description: "Nombres (sans guillemets) et chaînes (entre guillemets). Concaténation vs addition." },
  { time: "3:08", title: "Conclusion", description: "Utilisez const par défaut, let si besoin de changement, évitez var." }
];

const jsVariablesTranscript = [
  { time: "00:00", text: "Bienvenue dans ce cours sur les variables en JavaScript. Les variables sont des conteneurs qui permettent de stocker des données en mémoire." },
  { time: "00:06", text: "On peut imaginer une variable comme une boîte dans laquelle on met une valeur. Par exemple, goldCoins = 5, diamonds = 6, pizzaCoupons = 0." },
  { time: "00:33", text: "Il existe trois façons de déclarer une variable. var est l'ancienne méthode à éviter. let est pour les variables dont la valeur peut changer. const est pour les valeurs qui ne changent pas." },
  { time: "01:23", text: "Les noms de variables peuvent contenir des lettres, chiffres, $ et _. Ils doivent commencer par une lettre, $ ou _. Les mots réservés comme let ou const sont interdits." },
  { time: "01:59", text: "L'opérateur d'assignation = assigne une valeur à une variable. Ce n'est pas un signe d'égalité. Par exemple, x = x + 3 met à jour la valeur de x." },
  { time: "02:30", text: "Les nombres s'écrivent sans guillemets. Les chaînes de texte s'écrivent entre guillemets. Attention : '5' + 10 donne 510 (concaténation), pas 15." },
  { time: "03:08", text: "En conclusion, utilisez const par défaut. Si la valeur doit changer, utilisez let. Évitez var qui est déprécié. Les variables sont des conteneurs flexibles." }
];

  const jsIntroductionChapters = [
  { time: "00:00", title: "Qu'est-ce que JavaScript ?", duration: "0:15" },
  { time: "00:15", title: "JavaScript peut modifier le contenu HTML", duration: "0:30" },
  { time: "00:45", title: "JavaScript peut modifier les attributs HTML", duration: "0:30" },
  { time: "01:15", title: "JavaScript peut modifier les styles CSS", duration: "0:30" },
  { time: "01:45", title: "JavaScript peut masquer des éléments", duration: "0:30" },
  { time: "02:15", title: "JavaScript peut afficher des éléments masqués", duration: "0:25" },
  { time: "02:40", title: "Conclusion - JavaScript donne vie au web", duration: "0:09" }
];

const jsIntroductionVideoPoints = [
  { time: "0:00", title: "Introduction", description: "JavaScript est le langage de programmation du web. Il rend les pages interactives et dynamiques." },
  { time: "0:15", title: "getElementById & innerHTML", description: "Modifier le contenu HTML : document.getElementById('demo').innerHTML = 'nouveau texte'." },
  { time: "0:45", title: "Modifier les attributs", description: "JavaScript peut changer les attributs HTML, comme src d'une image pour allumer/éteindre une lampe." },
  { time: "1:15", title: "Modifier les styles CSS", description: "Changer les styles : element.style.color = 'red', element.style.fontSize = '35px'." },
  { time: "1:45", title: "Masquer des éléments", description: "element.style.display = 'none' pour masquer un élément." },
  { time: "2:15", title: "Afficher des éléments", description: "element.style.display = 'block' pour réafficher un élément masqué." }
];

const jsIntroductionTranscript = [
  { time: "00:00", text: "Bienvenue dans ce cours d'introduction à JavaScript. JavaScript est le langage de programmation du web. Il permet de rendre les pages web interactives et dynamiques." },
  { time: "00:15", text: "JavaScript peut modifier le contenu HTML. La méthode getElementById permet de trouver un élément HTML et de modifier son contenu avec innerHTML." },
  { time: "00:45", text: "JavaScript peut également modifier les attributs HTML. On peut changer l'attribut src d'une image pour allumer ou éteindre une lampe." },
  { time: "01:15", text: "JavaScript peut modifier les styles CSS. En changeant la propriété style.color, on peut changer la couleur du texte. style.fontSize permet d'agrandir le texte." },
  { time: "01:45", text: "JavaScript peut masquer des éléments HTML en modifiant la propriété display. Avec element.style.display = 'none', l'élément disparaît de la page." },
  { time: "02:15", text: "Pour réafficher un élément masqué, on utilise element.style.display = 'block'. Cela permet de créer des boutons pour afficher ou masquer du contenu." },
  { time: "02:40", text: "En conclusion, JavaScript est le langage qui donne vie aux pages web. Il peut tout modifier : contenu HTML, attributs, styles CSS, masquer et afficher des éléments." }
];

  const cssFloatChapters = [
  { time: "00:00", title: "Introduction à float", duration: "0:07" },
  { time: "00:07", title: "Flotter des éléments à gauche ou à droite", duration: "0:32" },
  { time: "00:39", title: "Flotter des images avec texte", duration: "0:33" },
  { time: "01:12", title: "Galeries d'images avec float", duration: "0:41" },
  { time: "01:53", title: "Interaction avec les éléments texte", duration: "0:31" },
  { time: "02:24", title: "La propriété clear", duration: "0:40" },
  { time: "03:04", title: "Conclusion - Clearfix et bonnes pratiques", duration: "0:09" }
];

const cssFloatVideoPoints = [
  { time: "0:00", title: "Introduction", description: "Float permet de positionner un élément à gauche ou à droite, avec texte qui s'enroule autour." },
  { time: "0:39", title: "Images flottantes", description: "Image flottante à droite ou gauche avec texte qui s'enroule autour automatiquement." },
  { time: "1:12", title: "Galerie d'images", description: "Plusieurs éléments flottants s'alignent côte à côte si l'espace le permet." },
  { time: "1:53", title: "Interaction texte", description: "Les titres et texte peuvent s'enrouler à côté des éléments flottants." },
  { time: "2:24", title: "clear", description: "clear: left; right; both; empêche les flottements sur les côtés spécifiés." },
  { time: "3:04", title: "Clearfix", description: "Technique pour éviter l'effondrement des conteneurs parents d'éléments flottants." }
];

const cssFloatTranscript = [
  { time: "00:00", text: "Bienvenue dans ce cours sur la propriété CSS float. Float permet de positionner un élément à gauche ou à droite, permettant au texte et aux autres éléments de s'enrouler autour." },
  { time: "00:07", text: "Les éléments peuvent flotter à gauche ou à droite. Les autres éléments s'enroulent autour de l'élément flottant. C'est très utile pour les images dans du texte." },
  { time: "00:39", text: "Par exemple, une image flottante à droite avec le texte qui s'enroule à gauche. Si on change float de droite à gauche, l'image se déplace mais le texte continue de s'enrouler." },
  { time: "01:12", text: "Avec plusieurs éléments flottants, ils s'alignent les uns à côté des autres si l'espace le permet. C'est idéal pour créer des galeries d'images qui s'adaptent au redimensionnement." },
  { time: "01:53", text: "Lorsqu'on ajoute un titre entre des images flottantes, le texte s'enroule à côté d'elles. Cela montre comment les flottants affectent les éléments suivants." },
  { time: "02:24", text: "La propriété clear empêche les éléments flottants d'apparaître sur le côté gauche, droit, ou les deux. Cela garantit que les titres ne se retrouvent pas coincés à côté des images." },
  { time: "03:04", text: "En conclusion, float permet un contrôle précis de l'alignement. Pour les conteneurs parents d'éléments flottants, utilisez la technique clearfix. Consultez W3Schools pour plus d'exemples." }
];

  const cssOverflowChapters = [
  { time: "00:00", title: "Introduction à overflow", duration: "0:07" },
  { time: "00:07", title: "Qu'est-ce que le dépassement de contenu", duration: "1:02" },
  { time: "01:09", title: "overflow: visible (valeur par défaut)", duration: "0:12" },
  { time: "01:21", title: "overflow: hidden", duration: "0:24" },
  { time: "01:45", title: "overflow: clip", duration: "0:40" },
  { time: "02:25", title: "overflow: scroll", duration: "0:27" },
  { time: "02:52", title: "overflow: auto", duration: "0:15" },
  { time: "03:07", title: "Conclusion - Comment choisir", duration: "0:16" }
];

const cssOverflowVideoPoints = [
  { time: "0:00", title: "Introduction", description: "Overflow se produit lorsque le contenu dépasse les limites de son conteneur parent." },
  { time: "1:09", title: "visible", description: "Valeur par défaut. Le contenu qui dépasse s'affiche en dehors de la boîte." },
  { time: "1:21", title: "hidden", description: "Le contenu qui dépasse est coupé et caché. Reste accessible (copier-coller)." },
  { time: "1:45", title: "clip", description: "Similaire à hidden mais fonctionne avec overflow-clip-margin. Permet un dépassement partiel." },
  { time: "2:25", title: "scroll", description: "Ajoute des barres de défilement (verticales et horizontales) quel que soit le contenu." },
  { time: "2:52", title: "auto", description: "Ajoute des barres de défilement uniquement lorsque nécessaire. Solution recommandée." }
];

const cssOverflowTranscript = [
  { time: "00:00", text: "Bienvenue dans ce cours sur la propriété CSS overflow. Overflow se produit lorsque le contenu dépasse les limites de son conteneur parent." },
  { time: "00:07", text: "CSS offre différentes façons de gérer cette situation. Les valeurs principales sont visible, hidden, clip, scroll et auto." },
  { time: "01:09", text: "visible est la valeur par défaut. Le contenu qui dépasse s'affiche en dehors de la boîte, sans aucune restriction." },
  { time: "01:21", text: "hidden coupe et cache le contenu qui dépasse. Il reste accessible, par exemple par copier-coller, même s'il n'est pas visible." },
  { time: "01:45", text: "clip est similaire à hidden mais fonctionne avec overflow-clip-margin. Cela permet un dépassement partiel jusqu'à une certaine marge avant de cacher le reste." },
  { time: "02:25", text: "scroll ajoute des barres de défilement verticales et horizontales, quel que soit le contenu. Les barres apparaissent même si elles ne sont pas nécessaires." },
  { time: "02:52", text: "auto ajoute des barres de défilement uniquement lorsque c'est nécessaire. C'est la solution la plus propre et recommandée." },
  { time: "03:07", text: "En conclusion, utilisez visible pour le comportement normal, hidden pour masquer les débordements, clip pour un contrôle précis, scroll pour des barres permanentes, et auto pour des barres conditionnelles." }
];

  const cssPositioningChapters = [
  { time: "00:00", title: "Introduction au positionnement CSS", duration: "0:05" },
  { time: "00:05", title: "Les différentes valeurs de position", duration: "0:37" },
  { time: "00:42", title: "Position relative", duration: "0:41" },
  { time: "01:23", title: "Position absolute", duration: "0:48" },
  { time: "02:11", title: "Position fixed", duration: "0:47" },
  { time: "02:58", title: "Position sticky", duration: "0:47" },
  { time: "03:45", title: "Exemples pratiques", duration: "0:51" },
  { time: "04:36", title: "Conclusion - Résumé et bonnes pratiques", duration: "2:00" }
];

const cssPositioningVideoPoints = [
  { time: "0:00", title: "Introduction", description: "Le positionnement définit comment les éléments sont placés sur la page." },
  { time: "0:42", title: "Position relative", description: "Déplace l'élément par rapport à sa position normale, l'espace d'origine reste réservé." },
  { time: "1:23", title: "Position absolute", description: "Retire l'élément du flux, positionné par rapport à l'ancêtre positionné le plus proche." },
  { time: "2:11", title: "Position fixed", description: "Fixe l'élément par rapport à la fenêtre, reste visible lors du défilement." },
  { time: "2:58", title: "Position sticky", description: "Alterne entre relative et fixed selon le défilement, reste collé à un seuil." },
  { time: "3:45", title: "Propriétés de décalage", description: "top, right, bottom, left permettent de déplacer les éléments positionnés." },
  { time: "4:36", title: "z-index", description: "Contrôle l'ordre d'empilement. Fonctionne uniquement sur les éléments positionnés." }
];

const cssPositioningTranscript = [
  { time: "00:00", text: "Bienvenue dans ce cours sur le positionnement CSS. Le positionnement définit comment les éléments sont placés sur la page. Il existe cinq valeurs principales : static, relative, absolute, fixed et sticky." },
  { time: "00:05", text: "Par défaut, tous les éléments ont position: static. Cela signifie qu'ils suivent le flux normal de la page, dans l'ordre où ils apparaissent dans le HTML." },
  { time: "00:42", text: "position: relative permet de déplacer un élément par rapport à sa position normale. L'espace d'origine reste réservé. Utile pour des ajustements fins." },
  { time: "01:23", text: "position: absolute retire l'élément du flux normal. Il est positionné par rapport à son ancêtre positionné le plus proche. Sans ancêtre, il se positionne par rapport au body." },
  { time: "02:11", text: "position: fixed fixe l'élément par rapport à la fenêtre du navigateur. Il reste à la même place lors du défilement. Idéal pour les menus de navigation fixes." },
  { time: "02:58", text: "position: sticky alterne entre relative et fixed selon le défilement. L'élément reste collé à un seuil défini, par exemple en haut de la fenêtre." },
  { time: "03:45", text: "En pratique, on utilise relative pour créer un conteneur pour des éléments absolus, fixed pour les barres de navigation, et sticky pour les en-têtes de section." },
  { time: "04:36", text: "Les propriétés top, right, bottom, left permettent de déplacer les éléments positionnés. Fixed et sticky créent des éléments qui restent visibles pendant le défilement." }
];


  const cssDisplayVisibilityChapters = [
  { time: "00:00", title: "Introduction à Display et Visibility", duration: "0:08" },
  { time: "00:08", title: "Différence entre display et visibility", duration: "0:21" },
  { time: "00:29", title: "Masquer les éléments - visibility: hidden vs display: none", duration: "1:24" },
  { time: "01:53", title: "Éléments block vs inline", duration: "0:50" },
  { time: "02:43", title: "Exemple pratique: menu de navigation", duration: "0:22" },
  { time: "03:05", title: "Changer inline en block", duration: "1:21" },
  { time: "04:26", title: "Note importante - Sémantique vs Affichage", duration: "0:26" },
  { time: "04:52", title: "Conclusion - Résumé des différences", duration: "0:05" }
];

const cssDisplayVisibilityVideoPoints = [
  { time: "0:00", title: "Introduction", description: "display contrôle le rendu d'un élément, visibility contrôle la visibilité." },
  { time: "0:29", title: "visibility: hidden", description: "Cache l'élément mais conserve son espace dans la mise en page." },
  { time: "0:29", title: "display: none", description: "Supprime complètement l'élément, comme s'il n'existait pas." },
  { time: "1:53", title: "Éléments block", description: "Prennent toute la largeur, forcent un saut de ligne (ex: div, p, h1)." },
  { time: "1:53", title: "Éléments inline", description: "Prennent la largeur nécessaire, pas de saut de ligne (ex: span, a)." },
  { time: "2:43", title: "Menu horizontal", description: "Utiliser display: inline sur les li pour créer un menu horizontal." },
  { time: "3:05", title: "inline → block", description: "On peut transformer des éléments inline en block (ex: span, a)." },
  { time: "4:26", title: "Note importante", description: "Changer display affecte le rendu visuel, pas la sémantique." }
];

const cssDisplayVisibilityTranscript = [
  { time: "00:00", text: "Bienvenue dans ce cours sur les propriétés CSS display et visibility. Ces propriétés contrôlent comment les éléments sont affichés ou cachés sur la page." },
  { time: "00:08", text: "display contrôle comment et si un élément est rendu. visibility contrôle si un élément est visible mais conserve sa place dans la mise en page." },
  { time: "00:29", text: "visibility: hidden cache l'élément mais conserve l'espace qu'il occupe. display: none supprime complètement l'élément, comme s'il n'existait pas. Les autres éléments se repositionnent." },
  { time: "01:53", text: "Les éléments block prennent toute la largeur disponible et forcent un saut de ligne. Les éléments inline ne prennent que la largeur nécessaire et restent sur la même ligne." },
  { time: "02:43", text: "Pour créer un menu horizontal, on utilise display: inline sur les éléments li. Sans cette propriété, le menu s'affiche verticalement par défaut." },
  { time: "03:05", text: "On peut transformer des éléments inline comme span ou a en éléments block. Ils prennent alors toute la largeur et forcent des sauts de ligne." },
  { time: "04:26", text: "Note importante : changer display affecte le rendu visuel, pas la signification sémantique. Un élément inline transformé en block ne peut toujours pas contenir d'autres éléments block." },
  { time: "04:52", text: "En conclusion, utilisez visibility: hidden pour masquer en conservant l'espace, display: none pour supprimer complètement un élément, et display: inline pour créer des menus horizontaux." }
];

  const cssTablesChapters = [
  { time: "00:00", title: "Introduction aux tableaux CSS", duration: "0:07" },
  { time: "00:07", title: "Améliorer l'apparence des tableaux avec CSS", duration: "0:12" },
  { time: "00:19", title: "Bordures des tableaux", duration: "0:28" },
  { time: "00:47", title: "Fusion des bordures (border-collapse: collapse)", duration: "0:29" },
  { time: "01:16", title: "Dimensions du tableau (width, height)", duration: "0:45" },
  { time: "02:01", title: "Alignement du texte (text-align, vertical-align)", duration: "1:18" },
  { time: "03:19", title: "Espacement intérieur (padding)", duration: "0:33" },
  { time: "03:52", title: "Couleurs et arrière-plans", duration: "1:13" },
  { time: "05:05", title: "Conclusion - Bonnes pratiques", duration: "0:08" }
];

const cssTablesVideoPoints = [
  { time: "0:00", title: "Introduction", description: "CSS permet d'améliorer l'apparence des tableaux HTML avec bordures, couleurs, alignement, etc." },
  { time: "0:19", title: "Bordures", description: "border: 1px solid black; sur table, th, td. Problème : bordures doubles sans border-collapse." },
  { time: "0:47", title: "border-collapse", description: "border-collapse: collapse; fusionne les bordures doubles en une seule ligne." },
  { time: "1:16", title: "Dimensions", description: "width: 100% pour tableau pleine largeur, height pour ajuster la hauteur des en-têtes." },
  { time: "2:01", title: "Alignement", description: "text-align pour horizontal (left, center, right), vertical-align pour vertical (top, middle, bottom)." },
  { time: "3:19", title: "Padding", description: "padding ajoute de l'espace entre le contenu et la bordure, rendant le tableau plus aéré." },
  { time: "3:52", title: "Couleurs", description: "background-color pour l'arrière-plan, color pour le texte. Alternance de lignes avec nth-child(even)." },
  { time: "5:05", title: "Bonnes pratiques", description: "Utilisez border-collapse, padding, couleurs alternées, effet hover, et overflow-x: auto pour mobile." }
];

const cssTablesTranscript = [
  { time: "00:00", text: "Bienvenue dans ce cours sur le stylage des tableaux en CSS. Les tableaux HTML peuvent être améliorés avec CSS pour les rendre plus attrayants et plus faciles à lire." },
  { time: "00:07", text: "CSS offre de nombreuses propriétés pour améliorer l'apparence des tableaux : bordures, fusion des bordures, dimensions, alignement, espacement, couleurs." },
  { time: "00:19", text: "La propriété border permet d'ajouter des bordures aux tableaux et aux cellules. Mais attention, lorsque les bordures sont appliquées au tableau ET aux cellules, des bordures doubles apparaissent." },
  { time: "00:47", text: "La propriété border-collapse: collapse résout ce problème en fusionnant les bordures doubles en une seule ligne. C'est la première propriété à appliquer pour des tableaux propres." },
  { time: "01:16", text: "Les dimensions du tableau se contrôlent avec width et height. width: 100% permet au tableau d'occuper toute la largeur. On peut aussi ajuster la hauteur des en-têtes." },
  { time: "02:01", text: "L'alignement du texte se fait avec text-align pour l'horizontal (left, center, right) et vertical-align pour le vertical (top, middle, bottom). Les en-têtes sont centrés par défaut." },
  { time: "03:19", text: "La propriété padding ajoute de l'espace entre le contenu et la bordure de la cellule. Cela rend le tableau plus aéré et plus facile à lire." },
  { time: "03:52", text: "Les couleurs et arrière-plans améliorent le design. On peut colorer les en-têtes, alterner les couleurs des lignes avec nth-child(even), et ajouter un effet de survol avec hover." },
  { time: "05:05", text: "En conclusion, pour des tableaux professionnels : utilisez border-collapse: collapse, ajoutez du padding, utilisez des couleurs alternées, un effet de survol, et rendez les tableaux responsives sur mobile." }
];



  const cssListsChapters = [
  { time: "00:00", title: "Introduction aux listes en CSS", duration: "0:30" },
  { time: "00:30", title: "list-style-type - Changer les puces et numéros", duration: "0:30" },
  { time: "01:00", title: "Valeurs pour listes non ordonnées (disc, circle, square)", duration: "0:30" },
  { time: "01:30", title: "Valeurs pour listes ordonnées (decimal, roman, alpha)", duration: "0:30" },
  { time: "02:00", title: "list-style-position (inside vs outside)", duration: "0:30" },
  { time: "02:30", title: "list-style-image - Images personnalisées", duration: "0:30" },
  { time: "03:00", title: "Propriété raccourcie list-style", duration: "0:30" },
  { time: "03:30", title: "Supprimer les puces pour menus de navigation", duration: "0:30" },
  { time: "04:00", title: "Listes imbriquées et stylisation", duration: "0:30" },
  { time: "04:30", title: "Conclusion - Bonnes pratiques", duration: "0:44" }
];

const cssListsVideoPoints = [
  { time: "0:00", title: "Introduction", description: "Les listes HTML (ul et ol) peuvent être personnalisées pour améliorer l'apparence." },
  { time: "0:30", title: "list-style-type", description: "Propriété principale pour changer le type de marqueur (disc, circle, square, decimal, roman, etc.)." },
  { time: "1:00", title: "Listes non ordonnées", description: "Valeurs disponibles : disc (puce pleine), circle (puce creuse), square (carré), none (sans puce)." },
  { time: "1:30", title: "Listes ordonnées", description: "Valeurs : decimal (1,2,3), lower-roman (i,ii,iii), upper-roman (I,II,III), lower-alpha (a,b,c), upper-alpha (A,B,C)." },
  { time: "2:00", title: "list-style-position", description: "inside : marqueur dans le bloc texte, outside : marqueur à l'extérieur (par défaut)." },
  { time: "2:30", title: "list-style-image", description: "Remplace la puce standard par une image personnalisée. Toujours définir un fallback." },
  { time: "3:00", title: "list-style (shorthand)", description: "Propriété raccourcie : list-style: type position image; Exemple: list-style: square inside;." },
  { time: "3:30", title: "Menus de navigation", description: "Utilisez list-style-type: none + margin: 0; padding: 0; pour créer des menus." },
  { time: "4:00", title: "Listes imbriquées", description: "On peut styliser chaque niveau différemment avec des sélecteurs comme ul ul." },
  { time: "4:30", title: "Bonnes pratiques", description: "Pensez à l'accessibilité, utilisez des fallbacks pour les images, et testez sur différents appareils." }
];

const cssListsTranscript = [
  { time: "00:00", text: "Bienvenue dans ce cours sur le stylage des listes en CSS. Les listes HTML (ul et ol) peuvent être personnalisées pour améliorer l'apparence et la lisibilité de votre contenu." },
  { time: "00:30", text: "La propriété list-style-type permet de changer le type de marqueur. Pour les listes non ordonnées, on peut utiliser disc (puce pleine), circle (puce creuse), square (puce carrée), ou none (pas de puce)." },
  { time: "01:00", text: "Les puces par défaut sont disc. circle donne un cercle vide, square une forme carrée. Ces options permettent d'adapter le style à votre design." },
  { time: "01:30", text: "Pour les listes ordonnées, on peut utiliser decimal (1,2,3), decimal-leading-zero (01,02,03), lower-roman (i,ii,iii), upper-roman (I,II,III), lower-alpha (a,b,c) ou upper-alpha (A,B,C)." },
  { time: "02:00", text: "list-style-position contrôle l'emplacement du marqueur. outside place le marqueur à l'extérieur du bloc texte. inside le place à l'intérieur, le texte se décale pour s'aligner après la puce." },
  { time: "02:30", text: "list-style-image permet de remplacer la puce standard par une image personnalisée. Il est recommandé de toujours définir un fallback avec list-style-type au cas où l'image ne charge pas." },
  { time: "03:00", text: "La propriété raccourcie list-style combine type, position et image. Exemple : list-style: square inside url('puce.png'). Cela permet d'écrire du code plus concis." },
  { time: "03:30", text: "Pour créer des menus de navigation, on utilise souvent list-style-type: none pour supprimer les puces, puis on retire les marges et paddings par défaut avec margin: 0 et padding: 0." },
  { time: "04:00", text: "Pour les listes imbriquées, on peut styliser chaque niveau différemment. Par exemple, niveau 1 avec square, niveau 2 avec circle, niveau 3 avec disc." },
  { time: "04:30", text: "Bonnes pratiques : utilisez list-style-type: none pour les menus, privilégiez les images SVG pour list-style-image, utilisez des fallbacks, et pensez à l'accessibilité." }
];

  const cssLinksChapters = [
  { time: "00:00", title: "Introduction au stylage des liens CSS", duration: "0:03" },
  { time: "00:03", title: "Les liens peuvent être stylisés avec couleur, police, arrière-plan", duration: "0:25" },
  { time: "00:28", title: "Les quatre états d'un lien (link, visited, hover, active)", duration: "0:39" },
  { time: "01:07", title: "Changer les couleurs pour chaque état", duration: "1:02" },
  { time: "02:09", title: "L'ordre des règles CSS est important (LoVe HA!)", duration: "0:25" },
  { time: "02:34", title: "Décoration du texte (text-decoration)", duration: "0:30" },
  { time: "03:04", title: "Styliser l'arrière-plan et grouper les états", duration: "1:10" },
  { time: "04:14", title: "Conclusion - Expérimentez avec les liens", duration: "0:09" }
];

const cssLinksVideoPoints = [
  { time: "0:00", title: "Introduction", description: "Les liens hypertextes peuvent être stylisés avec couleur, police, arrière-plan, décoration selon leur état." },
  { time: "0:28", title: "Les 4 états d'un lien", description: "a:link (non visité), a:visited (visité), a:hover (survol), a:active (clic)." },
  { time: "1:07", title: "Couleurs par état", description: "Bleu pour non visité, rouge pour visité, orange au survol, vert au clic." },
  { time: "2:09", title: "Ordre LoVe HA!", description: "Link, Visited, Hover, Active. hover après link et visited, active après hover." },
  { time: "2:34", title: "text-decoration", description: "Retirer le soulignement par défaut ou ajouter des effets (underline, line-through)." },
  { time: "3:04", title: "Arrière-plan", description: "Ajouter des arrière-plans et grouper les états similaires pour un code plus propre." },
  { time: "4:14", title: "Conclusion", description: "Expérimentez avec les pseudo-classes et utilisez des transitions pour des effets fluides." }
];

const cssLinksTranscript = [
  { time: "00:00", text: "Bienvenue dans ce cours sur le stylage des liens en CSS. Les liens hypertextes peuvent être stylisés avec différentes propriétés CSS : couleur, police, arrière-plan, décoration, et plus encore." },
  { time: "00:03", text: "Chaque lien peut avoir un style différent selon son état. Les liens sont des éléments interactifs essentiels sur le web, et un bon stylage améliore l'expérience utilisateur." },
  { time: "00:28", text: "Il existe quatre états pour un lien. Le premier est a:link, le lien normal non visité. Ensuite a:visited, le lien déjà cliqué. Puis a:hover, le lien survolé par la souris. Enfin a:active, le lien au moment du clic." },
  { time: "01:07", text: "Pour chaque état, on peut changer la couleur. Par exemple, bleu pour les liens non visités, rouge pour les liens visités, orange au survol, et vert au moment du clic." },
  { time: "02:09", text: "L'ordre des règles CSS est crucial. La règle hover doit venir après link et visited. La règle active doit venir après hover. Retenez la règle mnémotechnique LoVe HA! : Link, Visited, Hover, Active." },
  { time: "02:34", text: "La propriété text-decoration permet de contrôler le soulignement. On peut retirer le soulignement par défaut avec text-decoration: none, ou ajouter des effets comme line-through au survol." },
  { time: "03:04", text: "On peut aussi styliser l'arrière-plan des liens. Pour optimiser le code, on peut grouper les états qui partagent les mêmes styles, comme link et visited ensemble, puis hover et active ensemble." },
  { time: "04:14", text: "En conclusion, expérimentez avec les différentes pseudo-classes. N'oubliez pas l'ordre LoVe HA! et utilisez les transitions pour des effets fluides." }
];

  const cssFontChapters = [
  { time: "00:00", title: "Introduction aux propriétés CSS des polices", duration: "0:08" },
  { time: "00:08", title: "Familles de polices (font-family) - génériques et spécifiques", duration: "0:53" },
  { time: "01:01", title: "Serif vs Sans-serif vs Monospace", duration: "0:56" },
  { time: "01:57", title: "Système de fallback pour les polices", duration: "1:14" },
  { time: "03:11", title: "Style de police (font-style: normal, italic, oblique)", duration: "0:49" },
  { time: "04:00", title: "Taille de police (font-size: px, em, rem)", duration: "3:19" },
  { time: "07:19", title: "Graisse de police (font-weight)", duration: "1:07" },
  { time: "08:26", title: "Conclusion - Bonnes pratiques et récapitulatif", duration: "0:00" }
];

const cssFontVideoPoints = [
  { time: "0:00", title: "Introduction", description: "Les propriétés font contrôlent l'apparence du texte : famille, taille, style, épaisseur." },
  { time: "0:08", title: "font-family", description: "Définit la police du texte. Familles génériques : serif, sans-serif, monospace, cursive, fantasy." },
  { time: "1:01", title: "Serif vs Sans-serif vs Monospace", description: "Serif a des empattements, sans-serif est plus moderne, monospace a largeur égale pour tous les caractères." },
  { time: "1:57", title: "Système de fallback", description: "Spécifiez plusieurs polices séparées par des virgules. Terminez toujours par une famille générique." },
  { time: "3:11", title: "font-style", description: "Contrôle l'italique. Valeurs : normal, italic (préféré), oblique." },
  { time: "4:00", title: "font-size", description: "Unités absolues (px) vs relatives (em, rem). Privilégiez les unités relatives pour l'accessibilité." },
  { time: "7:19", title: "font-weight", description: "Contrôle l'épaisseur : normal, bold, ou valeurs numériques 100-900 (400=normal, 700=bold)." },
  { time: "8:26", title: "Bonnes pratiques", description: "Utilisez fallback, privilégiez les unités relatives, préférez italic à oblique." }
];

const cssFontTranscript = [
  { time: "00:00", text: "Bienvenue dans ce cours sur les propriétés CSS des polices. Les propriétés font permettent de contrôler l'apparence du texte : famille, taille, style, épaisseur." },
  { time: "00:08", text: "font-family définit la police du texte. Il existe des familles génériques comme serif, sans-serif, monospace, et des polices spécifiques comme Arial ou Times New Roman." },
  { time: "01:01", text: "Serif : polices avec empattements (petites lignes décoratives), comme Times New Roman. Sans-serif : polices sans empattements, comme Arial, plus modernes. Monospace : tous les caractères ont la même largeur, idéal pour le code." },
  { time: "01:57", text: "Le système de fallback permet de spécifier plusieurs polices séparées par des virgules. Le navigateur essaie la première, puis la seconde. Toujours terminer par une famille générique." },
  { time: "03:11", text: "font-style contrôle si le texte est en italique. Les valeurs sont normal, italic, et oblique. Italic est préféré car mieux supporté que oblique." },
  { time: "04:00", text: "font-size définit la taille du texte. Les pixels sont des unités absolues, les em et rem sont relatives. Pour l'accessibilité, privilégiez les unités relatives qui permettent le redimensionnement." },
  { time: "07:19", text: "font-weight contrôle l'épaisseur du texte. Les valeurs possibles sont normal, bold, ou des valeurs numériques de 100 à 900. 400 équivaut à normal, 700 à bold." },
  { time: "08:26", text: "En conclusion, maîtrisez font-family avec fallback, privilégiez les unités relatives pour la taille, utilisez italic pour l'italique et les valeurs numériques pour la graisse." }
];

  
const cssTextChapters = [
  { time: "00:00", title: "Introduction aux propriétés texte en CSS", duration: "0:30" },
  { time: "00:30", title: "Alignement du texte (text-align)", duration: "0:30" },
  { time: "01:00", title: "Décoration du texte (text-decoration)", duration: "0:30" },
  { time: "01:30", title: "Transformation du texte (text-transform)", duration: "0:30" },
  { time: "02:00", title: "Espacement (letter-spacing, word-spacing)", duration: "0:30" },
  { time: "02:30", title: "Hauteur de ligne (line-height)", duration: "0:30" },
  { time: "03:00", title: "Indentation du texte (text-indent)", duration: "0:30" },
  { time: "03:30", title: "Ombres du texte (text-shadow)", duration: "0:30" },
  { time: "04:00", title: "Couleur du texte (color)", duration: "0:30" },
  { time: "04:30", title: "Exemples pratiques combinés", duration: "0:30" },
  { time: "05:00", title: "Bonnes pratiques et accessibilité", duration: "1:00" },
  { time: "06:00", title: "Conclusion - Récapitulatif", duration: "0:24" }
];


const cssTextVideoPoints = [
  { time: "0:00", title: "Introduction", description: "CSS offre de nombreuses propriétés pour styliser le texte sur vos pages web." },
  { time: "0:30", title: "text-align", description: "Contrôle l'alignement horizontal : left, right, center, justify." },
  { time: "1:00", title: "text-decoration", description: "Ajoute ou retire des effets décoratifs : underline, overline, line-through, none." },
  { time: "1:30", title: "text-transform", description: "Contrôle la casse : uppercase (majuscules), lowercase (minuscules), capitalize." },
  { time: "2:00", title: "Espacement", description: "letter-spacing pour l'espace entre lettres, word-spacing pour l'espace entre mots." },
  { time: "2:30", title: "line-height", description: "Définit la hauteur de ligne (interlignage) pour une meilleure lisibilité." },
  { time: "3:00", title: "text-indent", description: "Décale la première ligne d'un paragraphe, idéal pour les articles." },
  { time: "3:30", title: "text-shadow", description: "Ajoute une ombre portée au texte. Syntaxe : offset-x offset-y blur-radius color." },
  { time: "4:00", title: "color", description: "Définit la couleur du texte avec différents formats (noms, HEX, RGB, HSL)." },
  { time: "5:00", title: "Bonnes pratiques", description: "Utilisez line-height pour la lisibilité, text-transform pour uniformiser, gardez un effet au survol pour les liens." }
];


const cssTextTranscript = [
  { time: "00:00", text: "Bienvenue dans ce cours sur les propriétés CSS pour la mise en forme du texte. CSS offre de nombreuses propriétés pour styliser le texte : alignement, décoration, transformation, espacement, ombres, et bien plus encore." },
  { time: "00:30", text: "La propriété text-align contrôle l'alignement horizontal du texte. Les valeurs possibles sont left pour aligner à gauche, right pour aligner à droite, center pour centrer, et justify pour justifier le texte sur toute la largeur." },
  { time: "01:00", text: "text-decoration ajoute ou retire des effets décoratifs. underline souligne, overline ajoute une ligne au-dessus, line-through barre le texte, et none supprime toute décoration. Très utile pour les liens." },
  { time: "01:30", text: "text-transform contrôle la casse des lettres. uppercase met tout en majuscules, lowercase en minuscules, capitalize met la première lettre de chaque mot en majuscule." },
  { time: "02:00", text: "Pour l'espacement, letter-spacing contrôle l'espace entre les lettres, tandis que word-spacing contrôle l'espace entre les mots. Ces propriétés acceptent des valeurs en pixels ou en em." },
  { time: "02:30", text: "line-height définit la hauteur de ligne, c'est-à-dire l'interlignage. Une valeur de 1.4 à 1.6 est recommandée pour une bonne lisibilité." },
  { time: "03:00", text: "text-indent permet de décaler la première ligne d'un paragraphe. C'est très utile pour les articles de blog ou les paragraphes de texte longs." },
  { time: "03:30", text: "text-shadow ajoute une ombre portée au texte. La syntaxe est text-shadow: offset-x offset-y blur-radius color. Vous pouvez même ajouter plusieurs ombres séparées par des virgules." },
  { time: "04:00", text: "La propriété color définit la couleur du texte, avec plusieurs formats: noms de couleurs comme red, codes HEX comme #FF0000, RGB comme rgb(255,0,0), ou HSL." },
  { time: "04:30", text: "En pratique, vous pouvez combiner ces propriétés. Par exemple, un titre centré avec ombre, des liens sans soulignement qui s'affichent au survol, des paragraphes justifiés avec indentation." },
  { time: "05:00", text: "Bonnes pratiques : utilisez line-height pour améliorer la lisibilité, text-transform pour uniformiser la casse, et text-decoration: none sur les liens pour un design moderne tout en gardant un effet au survol." },
  { time: "06:00", text: "En conclusion, maîtrisez ces propriétés pour créer des typographies uniques et professionnelles. Expérimentez avec les combinaisons pour trouver le style parfait pour vos projets." }
];



  
const cssMarginChapters = [
  { time: "00:00", title: "Introduction aux marges CSS", duration: "0:12" },
  { time: "00:12", title: "Définition - l'espace extérieur", duration: "0:53" },
  { time: "01:05", title: "Propriétés individuelles (margin-top, right, bottom, left)", duration: "1:15" },
  { time: "02:20", title: "La propriété raccourcie margin", duration: "1:20" },
  { time: "03:40", title: "Auto margins pour centrer (margin: 0 auto)", duration: "0:36" },
  { time: "04:16", title: "Le margin collapsing - fusion des marges verticales", duration: "0:00" }
];

const cssPaddingChapters = [
  { time: "00:00", title: "Introduction au padding CSS", duration: "0:03" },
  { time: "00:03", title: "Définition - espace entre contenu et bordure", duration: "1:00" },
  { time: "01:03", title: "Définir le padding individuellement par côté", duration: "0:35" },
  { time: "01:38", title: "La propriété raccourcie padding", duration: "0:30" },
  { time: "02:08", title: "Unités et pourcentages pour le padding", duration: "1:28" },
  { time: "03:36", title: "Conclusion - à l'intérieur de la bordure", duration: "0:21" }
];


const cssMarginVideoPoints = [
  { time: "0:00", title: "Introduction", description: "Les marges créent de l'espace à l'extérieur de la bordure d'un élément, le poussant loin des autres éléments." },
  { time: "0:12", title: "Définition", description: "La marge est l'espace extérieur, transparente, sans couleur d'arrière-plan." },
  { time: "1:05", title: "Propriétés individuelles", description: "margin-top, margin-right, margin-bottom, margin-left permettent de contrôler chaque côté indépendamment." },
  { time: "2:20", title: "Propriété raccourcie", description: "1 valeur pour tous, 2 pour vertical/horizontal, 3 ou 4 pour réglages précis dans l'ordre horaire." },
  { time: "3:40", title: "Auto margins", description: "margin: 0 auto centre horizontalement un élément block avec une largeur définie." },
  { time: "4:16", title: "Margin collapsing", description: "Les marges verticales adjacentes se fusionnent en une seule marge (la plus grande)." }
];

const cssPaddingVideoPoints = [
  { time: "0:00", title: "Introduction", description: "Le padding crée de l'espace à l'intérieur d'un élément, entre son contenu et sa bordure." },
  { time: "0:03", title: "Définition", description: "Contrairement à la marge, le padding est à l'intérieur et peut avoir une couleur d'arrière-plan." },
  { time: "1:03", title: "Propriétés individuelles", description: "padding-top, padding-right, padding-bottom, padding-left pour contrôler chaque côté." },
  { time: "1:38", title: "Propriété raccourcie", description: "1 valeur pour quatre côtés, 2 pour vertical/horizontal, 3 ou 4 valeurs." },
  { time: "2:08", title: "Unités", description: "Pixels, ems, rems ou pourcentages (relatif à la largeur du parent)." },
  { time: "3:36", title: "Conclusion", description: "Padding augmente la taille totale de l'élément. Utilisez box-sizing: border-box pour l'inclure." }
];


const cssMarginTranscript = [
  { time: "00:00", text: "Bienvenue dans ce cours sur les marges en CSS. Les marges créent de l'espace à l'extérieur de la bordure d'un élément, le poussant loin des autres éléments." },
  { time: "00:12", text: "La marge est l'espace extérieur. Contrairement au padding, la marge est transparente et ne peut pas avoir de couleur d'arrière-plan." },
  { time: "01:05", text: "CSS permet de définir chaque marge individuellement avec margin-top, margin-right, margin-bottom et margin-left. Chaque côté peut avoir une valeur différente." },
  { time: "02:20", text: "La propriété raccourcie margin permet de définir les quatre marges en une seule ligne. Une valeur pour tous, deux pour vertical/horizontal, trois ou quatre pour des réglages précis dans l'ordre horaire." },
  { time: "03:40", text: "margin: auto est très utile pour centrer horizontalement des éléments block. L'élément doit avoir une largeur définie. margin: 0 auto est la syntaxe standard." },
  { time: "04:16", text: "Le margin collapsing est un comportement important : les marges verticales entre éléments adjacents se fusionnent en une seule marge, prenant la valeur la plus grande." }
];

const cssPaddingTranscript = [
  { time: "00:00", text: "Bienvenue dans ce cours sur le padding en CSS. Le padding crée de l'espace à l'intérieur d'un élément, entre son contenu et sa bordure." },
  { time: "00:03", text: "Contrairement à la marge, le padding est à l'intérieur de la bordure. Il peut avoir une couleur d'arrière-plan et rend l'élément plus spacieux intérieurement." },
  { time: "01:03", text: "Vous pouvez définir des paddings différents sur chaque côté avec padding-top, padding-right, padding-bottom et padding-left." },
  { time: "01:38", text: "La propriété raccourcie padding fonctionne comme margin : une valeur pour les quatre côtés, deux pour vertical/horizontal, trois ou quatre valeurs." },
  { time: "02:08", text: "Le padding peut être défini en pixels, ems, rems ou pourcentages. Les pourcentages sont calculés par rapport à la largeur de l'élément parent." },
  { time: "03:36", text: "En conclusion, utilisez padding pour aérer l'intérieur de vos éléments. Le padding augmente la taille totale de l'élément par défaut. Utilisez box-sizing: border-box pour l'inclure dans la largeur." }
];

  const cssBorderChapters = [
  { time: "00:00", title: "Introduction aux bordures CSS", duration: "0:20" },
  { time: "00:20", title: "Les styles de bordures (border-style) - Propriété fondamentale", duration: "0:17" },
  { time: "00:37", title: "Styles de base : none, dotted, dashed, solid, double", duration: "0:23" },
  { time: "01:00", title: "Styles 3D : groove, ridge, inset, outset", duration: "0:34" },
  { time: "01:34", title: "Les effets 3D en détail", duration: "0:56" },
  { time: "02:30", title: "La largeur des bordures (border-width)", duration: "0:30" },
  { time: "03:00", title: "La couleur des bordures (border-color)", duration: "1:17" },
  { time: "04:17", title: "Bordures différentes par côté", duration: "2:49" },
  { time: "07:06", title: "La propriété raccourcie (border)", duration: "0:34" },
  { time: "07:40", title: "Bordures côté-spécifiques raccourcies", duration: "0:52" },
  { time: "08:32", title: "Conclusion et bonnes pratiques", duration: "0:18" }
];

const cssBorderVideoPoints = [
  { time: "0:00", title: "Introduction", description: "Les bordures permettent d'ajouter des contours stylisés autour des éléments HTML. Elles peuvent être personnalisées en style, épaisseur et couleur." },
  { time: "0:20", title: "border-style", description: "Propriété fondamentale - sans style défini, la bordure ne s'affiche pas, même avec width et color." },
  { time: "0:37", title: "Styles de base", description: "none (pas de bordure), dotted (pointillés), dashed (tirets), solid (pleine), double (deux lignes parallèles)." },
  { time: "1:00", title: "Styles 3D", description: "groove (creusé), ridge (relief), inset (encastré), outset (saillant). L'effet dépend de la largeur et de la couleur." },
  { time: "2:30", title: "border-width", description: "Contrôle l'épaisseur : thin (fine), medium (moyenne), thick (épaisse), ou valeurs personnalisées en pixels." },
  { time: "3:00", title: "border-color", description: "Définit la couleur : noms, HEX, RGB, HSL, transparent. Par défaut, hérite de la couleur du texte." },
  { time: "4:17", title: "Bordures par côté", description: "Propriétés individuelles border-top, border-right, border-bottom, border-left pour des styles différents sur chaque côté." },
  { time: "7:06", title: "Propriété raccourcie border", description: "Combine style, largeur et couleur : border: 2px solid red. L'ordre des valeurs n'a pas d'importance." },
  { time: "7:40", title: "Bordures côté-spécifiques", description: "border-top, border-right, border-bottom, border-left pour des accents visuels subtils." },
  { time: "8:32", title: "Conclusion", description: "Maîtrisez les bordures pour enrichir vos designs. Consultez la référence W3Schools pour plus d'exemples." }
];

const cssBorderTranscript = [
  { time: "00:00", text: "Bienvenue dans ce cours sur les bordures CSS. Les bordures permettent d'ajouter des contours stylisés autour des éléments HTML. Elles peuvent être personnalisées en termes de style, d'épaisseur et de couleur." },
  { time: "00:20", text: "La propriété border-style est fondamentale. Sans style défini, les bordures ne s'affichent pas, même si vous définissez une largeur ou une couleur. C'est la propriété la plus importante à retenir." },
  { time: "00:37", text: "Les styles de base incluent : none pour pas de bordure, dotted pour des pointillés, dashed pour des tirets, solid pour une ligne pleine, et double pour deux lignes parallèles. Le style double divise l'épaisseur uniformément." },
  { time: "01:00", text: "Pour des effets 3D, nous avons groove qui donne un effet creusé, ridge pour un effet en relief, inset pour un effet encastré, et outset pour un effet saillant." },
  { time: "01:34", text: "Les effets 3D comme groove et ridge dépendent de la largeur et de la couleur de la bordure. Plus l'épaisseur est grande, plus l'effet 3D est prononcé. La couleur affecte également l'intensité de l'effet." },
  { time: "02:30", text: "La largeur des bordures se contrôle avec border-width. On peut utiliser des valeurs prédéfinies : thin pour fine, medium pour moyenne, thick pour épaisse, ou des valeurs personnalisées en pixels comme 2px, 5px." },
  { time: "03:00", text: "Les couleurs peuvent être définies avec des noms comme red, des codes HEX comme #FF0000, des valeurs RGB comme rgb(255,0,0), ou transparent. Par défaut, la bordure hérite de la couleur du texte si vous ne spécifiez pas de couleur." },
  { time: "04:17", text: "CSS permet d'appliquer des bordures différentes sur chaque côté. On peut utiliser des propriétés individuelles comme border-top-style, border-right-style, border-bottom-style, border-left-style, ou utiliser une seule propriété border-style avec plusieurs valeurs." },
  { time: "07:06", text: "La propriété raccourcie border combine style, largeur et couleur en une seule déclaration. Exemple : border: 2px solid red. L'ordre des valeurs n'a pas d'importance, vous pouvez écrire border: solid 2px red également." },
  { time: "07:40", text: "Pour des bordures côté-spécifiques, on utilise border-top, border-right, border-bottom, border-left. Cela permet de créer des accents visuels subtils, comme une ligne de sélection ou une alerte avec une bordure colorée sur le côté gauche." },
  { time: "08:32", text: "En conclusion, maîtrisez les bordures pour enrichir vos designs. Consultez la référence W3Schools pour plus d'exemples. Entraînez-vous avec différents styles, largeurs et couleurs pour créer des designs uniques." }
];

  const cssBackgroundChapters = [
  { time: "00:00", title: "Introduction aux images d'arrière-plan", duration: "0:10" },
  { time: "00:10", title: "La propriété background-image", duration: "0:10" },
  { time: "00:20", title: "Contrôle de la répétition (background-repeat)", duration: "0:15" },
  { time: "00:35", title: "Positionnement (background-position)", duration: "0:15" },
  { time: "00:50", title: "Dimensionnement (background-size: cover/contain)", duration: "0:15" },
  { time: "01:05", title: "Combinaison avec couleurs et fallback", duration: "0:15" },
  { time: "01:20", title: "Bonnes pratiques et récapitulatif", duration: "0:06" }
];

const cssBackgroundVideoPoints = [
  { time: "0:00", title: "Introduction", description: "Les images d'arrière-plan permettent d'ajouter des visuels attrayants derrière le contenu de vos pages web." },
  { time: "0:10", title: "background-image", description: "La propriété background-image: url('image.jpg'); permet de définir une image comme arrière-plan d'un élément." },
  { time: "0:20", title: "background-repeat", description: "no-repeat empêche la répétition, repeat-x répète horizontalement, repeat-y répète verticalement." },
  { time: "0:35", title: "background-position", description: "Contrôle l'emplacement : center, top, bottom, left, right, ou pourcentages." },
  { time: "0:50", title: "background-size", description: "cover couvre tout l'élément (peut rogner), contain montre l'image entière (peut laisser des espaces)." },
  { time: "1:05", title: "Couleur de fallback", description: "Toujours définir une couleur d'arrière-plan qui s'affiche pendant le chargement ou si l'image ne charge pas." },
  { time: "1:20", title: "Bonnes pratiques", description: "Optimisez vos images, utilisez cover pour les héros, testez sur mobile, assurez un bon contraste pour l'accessibilité." }
];

const cssBackgroundTranscript = [
  { time: "00:00", text: "Bienvenue dans ce cours sur les images d'arrière-plan en CSS. Les images d'arrière-plan permettent d'ajouter des visuels attrayants derrière le contenu de vos pages web." },
  { time: "00:10", text: "La propriété background-image permet de définir une image comme arrière-plan. Par exemple : background-image: url('image.jpg'); pour mettre une image derrière un élément." },
  { time: "00:20", text: "Par défaut, l'image se répète en mosaïque. background-repeat: no-repeat empêche la répétition. repeat-x répète horizontalement, repeat-y verticalement." },
  { time: "00:35", text: "background-position contrôle l'emplacement. Utilisez center, top, bottom, left, right, ou des pourcentages. background-position: center centre l'image parfaitement." },
  { time: "00:50", text: "background-size: cover redimensionne l'image pour couvrir tout l'élément, même si elle est rognée. contain montre l'image entière, mais peut laisser des espaces vides." },
  { time: "01:05", text: "Toujours définir une couleur d'arrière-plan de secours. Par exemple background-color: #333; Elle s'affiche pendant le chargement ou si l'image ne peut pas être chargée." },
  { time: "01:20", text: "Bonnes pratiques : optimisez vos images, utilisez cover pour les héros, testez sur mobile, et assurez un bon contraste entre l'arrière-plan et le texte pour l'accessibilité." }
];

  const cssColorsChapters = [
  { time: "00:00", title: "Introduction aux couleurs en CSS", duration: "0:20" },
  { time: "00:20", title: "Les noms de couleurs", duration: "0:20" },
  { time: "00:40", title: "Les codes HEX (hexadécimaux)", duration: "0:20" },
  { time: "01:00", title: "Les valeurs RGB", duration: "0:20" },
  { time: "01:20", title: "RGBA - Ajouter l'opacité", duration: "0:20" },
  { time: "01:40", title: "Les valeurs HSL (Hue, Saturation, Lightness)", duration: "0:20" },
  { time: "02:00", title: "HSLA - Opacité avec HSL", duration: "0:20" },
  { time: "02:20", title: "Comparaison des formats de couleurs", duration: "0:20" },
  { time: "02:40", title: "Bonnes pratiques et accessibilité", duration: "0:21" }
];

const cssColorsVideoPoints = [
  { time: "0:00", title: "Introduction", description: "Les couleurs sont essentielles pour donner vie à vos pages web. CSS offre plusieurs façons de définir les couleurs." },
  { time: "0:20", title: "Noms de couleurs", description: "Format le plus simple. CSS supporte 140 noms standards comme red, blue, green, yellow, etc. Idéal pour les couleurs de base." },
  { time: "0:40", title: "Codes HEX", description: "# suivi de 6 caractères hexadécimaux. #FF0000 = rouge, #00FF00 = vert, #0000FF = bleu. Format le plus utilisé en web design." },
  { time: "1:00", title: "RGB", description: "rgb(rouge, vert, bleu) avec valeurs 0-255. rgb(255,0,0) = rouge, rgb(0,255,0) = vert, rgb(0,0,255) = bleu." },
  { time: "1:20", title: "RGBA", description: "Ajoute un canal alpha pour l'opacité (0=transparent, 1=opaque). Ex: rgba(255,0,0,0.5) = rouge semi-transparent." },
  { time: "1:40", title: "HSL", description: "Hue (0-360°), Saturation (0-100%), Lightness (0-100%). Format plus intuitif pour créer des variations." },
  { time: "2:00", title: "HSLA", description: "HSL avec canal alpha pour l'opacité. Ex: hsla(240,100%,50%,0.5) = bleu semi-transparent." },
  { time: "2:20", title: "Comparaison", description: "Noms : simples mais limités. HEX/RGB : précis et universels. HSL : excellent pour les variations." },
  { time: "2:40", title: "Bonnes pratiques", description: "Utilisez des variables CSS, assurez un bon contraste pour l'accessibilité, testez sur différents écrans." }
];

const cssColorsTranscript = [
  { time: "00:00", text: "Bienvenue dans ce cours sur les couleurs en CSS. Les couleurs sont essentielles pour donner vie à vos pages web. CSS offre plusieurs façons de définir et manipuler les couleurs pour le texte, les arrière-plans, les bordures et bien plus encore." },
  { time: "00:20", text: "Les noms de couleurs sont le format le plus simple. CSS supporte 140 noms de couleurs standards comme red, blue, green, yellow, orange, purple, etc. C'est parfait pour les couleurs de base." },
  { time: "00:40", text: "Les codes HEX utilisent 6 caractères hexadécimaux précédés d'un #. Par exemple, #FF0000 pour le rouge, #00FF00 pour le vert, #0000FF pour le bleu. C'est le format le plus utilisé en web design." },
  { time: "01:00", text: "RGB définit une couleur par un mélange de rouge, vert et bleu. Chaque valeur est comprise entre 0 et 255. Exemple : rgb(255, 0, 0) donne du rouge pur, rgb(0, 255, 0) du vert." },
  { time: "01:20", text: "RGBA ajoute un quatrième paramètre pour l'opacité. La valeur alpha va de 0 (complètement transparent) à 1 (complètement opaque). Exemple : rgba(255, 0, 0, 0.5) donne du rouge semi-transparent." },
  { time: "01:40", text: "HSL est un format plus intuitif. H pour Hue (teinte) de 0 à 360°, S pour Saturation (0-100%), L pour Lightness (luminosité 0-100%). Par exemple, hsl(0, 100%, 50%) donne du rouge." },
  { time: "02:00", text: "HSLA fonctionne comme HSL mais avec un canal alpha pour l'opacité. Exemple : hsla(240, 100%, 50%, 0.5) donne du bleu semi-transparent. C'est très utile pour les overlays et les effets de transparence." },
  { time: "02:20", text: "Quel format choisir ? Les noms de couleurs sont simples mais limités. HEX et RGB sont précis et universels. HSL est excellent pour créer des variations de couleurs en ajustant la luminosité ou la saturation." },
  { time: "02:40", text: "Bonnes pratiques : utilisez des variables CSS pour les couleurs réutilisables, assurez un bon contraste entre texte et arrière-plan pour l'accessibilité, et testez vos couleurs sur différents écrans pour garantir une bonne expérience utilisateur." }
];

  const cssSelectorsChapters = [
  { time: "00:00", title: "Introduction aux sélecteurs CSS", duration: "0:20" },
  { time: "00:20", title: "Les sélecteurs d'élément (type selectors)", duration: "0:20" },
  { time: "00:40", title: "Les sélecteurs d'ID (#id)", duration: "0:20" },
  { time: "01:00", title: "Les sélecteurs de classe (.class)", duration: "0:20" },
  { time: "01:20", title: "Comparaison et bonnes pratiques", duration: "0:20" },
  { time: "01:40", title: "Exemples pratiques en code", duration: "0:20" },
  { time: "02:00", title: "Conclusion - Les blocs de construction du CSS", duration: "0:12" }
];

const cssSelectorsVideoPoints = [
  { time: "0:00", title: "Introduction", description: "Les sélecteurs CSS sont la base du stylage web. Ils permettent de cibler précisément les éléments HTML à styliser." },
  { time: "0:20", title: "Sélecteurs d'élément", description: "Cible toutes les occurrences d'une balise HTML spécifique. Exemple: p { color: red; } s'applique à tous les paragraphes." },
  { time: "0:40", title: "Sélecteurs d'ID", description: "Cible un élément unique avec #id. Chaque ID doit être unique dans la page. Exemple: #header { font-size: 20px; }" },
  { time: "1:00", title: "Sélecteurs de classe", description: "Cible plusieurs éléments avec .classname. Exemple: .highlight { background: yellow; }" },
  { time: "1:20", title: "Comparaison", description: "ID = unique (spécificité élevée) | Classe = réutilisable (recommandé) | Élément = global." },
  { time: "1:40", title: "Multi-classes", description: "Un élément peut avoir plusieurs classes : class='btn btn-primary large'. Très utile pour les composants." },
  { time: "2:00", title: "Conclusion", description: "Maîtriser ces trois sélecteurs est essentiel pour écrire du CSS efficace et maintenable." }
];

const cssSelectorsTranscript = [
  { time: "00:00", text: "Bienvenue dans ce cours sur les sélecteurs CSS simples. Les sélecteurs CSS sont la base du stylage web. Ils permettent de cibler précisément les éléments HTML à styliser." },
  { time: "00:20", text: "Le sélecteur d'élément cible toutes les occurrences d'une balise HTML spécifique. Par exemple, le sélecteur 'p' appliquera les styles à tous les paragraphes de la page. Exemple : p { color: red; }" },
  { time: "00:40", text: "Le sélecteur d'ID cible un élément unique dans la page, en utilisant la syntaxe #suivi du nom de l'ID. Chaque ID doit être unique. Exemple : #header { font-size: 20px; }" },
  { time: "01:00", text: "Le sélecteur de classe cible plusieurs éléments qui partagent le même nom de classe, avec la syntaxe .suivi du nom de la classe. Exemple : .highlight { background: yellow; }" },
  { time: "01:20", text: "La principale différence : un ID est unique sur la page, une classe peut être réutilisée plusieurs fois. Les classes sont plus flexibles et recommandées pour le styling, les IDs sont idéals pour les éléments uniques et le JavaScript." },
  { time: "01:40", text: "Dans la pratique, on utilise souvent les classes par défaut car elles sont réutilisables. Un élément peut même avoir plusieurs classes, séparées par des espaces, comme class='btn btn-primary large'." },
  { time: "02:00", text: "En conclusion, maîtriser les sélecteurs d'élément, d'ID et de classe est essentiel pour écrire du CSS efficace. Ce sont les blocs de construction du styling web. Entraînez-vous avec ces trois types de sélecteurs pour bien comprendre quand utiliser chacun." }
];


  const cssMediaQueryChapters = [
  { time: "00:00", title: "Introduction aux Media Queries", duration: "0:16" },
  { time: "00:16", title: "Syntaxe de base des Media Queries", duration: "1:00" },
  { time: "01:16", title: "Types d'appareils (screen, print, speech)", duration: "1:09" },
  { time: "02:25", title: "Exemple pratique avec max-width", duration: "0:55" },
  { time: "03:20", title: "Styles spécifiques à l'impression", duration: "1:12" },
  { time: "04:32", title: "L'ordre des règles CSS et la spécificité", duration: "0:02" },
  { time: "04:34", title: "Requêtes d'orientation (landscape/portrait)", duration: "0:51" },
  { time: "05:25", title: "Combinaison de conditions (ET et OU)", duration: "1:06" },
  { time: "06:31", title: "Les sélecteurs les plus utiles", duration: "0:26" },
  { time: "06:57", title: "Conclusion - Fondation du responsive design", duration: "0:13" }
];

const cssMediaQueryVideoPoints = [
  { time: "0:00", title: "Introduction", description: "Les media queries sont une partie essentielle du CSS moderne pour le responsive design." },
  { time: "0:16", title: "Syntaxe", description: "La syntaxe utilise @media suivie d'une condition et des styles entre accolades." },
  { time: "1:16", title: "Types d'appareils", description: "screen pour écrans, print pour impression, speech pour lecteurs d'écran, all pour tous." },
  { time: "2:25", title: "max-width", description: "La couleur du texte change : rouge par défaut, bleue quand la largeur est inférieure à 500px." },
  { time: "3:20", title: "Print styles", description: "Styles spécifiques à l'impression pour masquer les éléments non pertinents et économiser l'encre." },
  { time: "4:32", title: "Ordre CSS", description: "L'ordre des règles est important - les règles plus tardives l'emportent sur les précédentes." },
  { time: "4:34", title: "Orientation", description: "landscape pour paysage, portrait pour portrait - adaptez vos styles à la rotation de l'écran." },
  { time: "5:25", title: "Combinaisons", description: "'and' pour ET, virgule pour OU - exemple : (orientation: landscape) and (max-width: 600px)." },
  { time: "6:31", title: "Sélecteurs utiles", description: "max-width, min-width, orientation, print sont les plus couramment utilisés." },
  { time: "6:57", title: "Conclusion", description: "Les media queries sont la fondation du responsive design pour tous les appareils." }
];

const cssMediaQueryTranscript = [
  { time: "00:00", text: "Les CSS media queries sont essentielles pour la création de sites web responsives. Elles permettent d'adapter les styles CSS en fonction des caractéristiques de l'appareil : taille d'écran, orientation, type d'affichage." },
  { time: "00:16", text: "La syntaxe de base utilise @media suivie d'une condition et des styles entre accolades. Par exemple : @media (max-width: 500px) { body { color: blue; } }" },
  { time: "01:16", text: "Les différents types d'appareils incluent screen pour les écrans, print pour l'impression papier, speech pour les lecteurs d'écran, et all pour tous les appareils." },
  { time: "02:25", text: "Dans cet exemple pratique, la couleur du texte change. Par défaut elle est rouge. Mais lorsque la largeur d'écran est inférieure à 500 pixels, elle devient bleue." },
  { time: "03:20", text: "Les styles spécifiques à l'impression permettent de masquer les éléments non pertinents comme les menus de navigation, ou d'ajuster les couleurs pour économiser l'encre." },
  { time: "04:32", text: "L'ordre des règles CSS est très important. Les règles qui apparaissent plus tard dans la feuille de style l'emportent sur les précédentes, même à l'intérieur des media queries." },
  { time: "04:34", text: "Les requêtes d'orientation permettent de détecter si l'appareil est en mode paysage ou portrait, et d'appliquer des styles adaptés à chaque orientation." },
  { time: "05:25", text: "Pour combiner plusieurs conditions, utilisez 'and' pour un ET logique, et la virgule pour un OU logique. Par exemple : @media (orientation: landscape) and (max-width: 600px)" },
  { time: "06:31", text: "Les sélecteurs les plus utiles sont max-width pour cibler les petits écrans, min-width pour les grands écrans, orientation pour la rotation de l'appareil, et print pour l'impression." },
  { time: "06:57", text: "En conclusion, les media queries sont la fondation du responsive design. Maîtrisez-les pour créer des sites web qui s'adaptent parfaitement à tous les appareils : mobiles, tablettes et ordinateurs." }
];

  const multimediaChapters = [
  { time: "00:00", title: "Introduction au multimédia", duration: "0:44" },
  { time: "00:44", title: "Définition du multimédia (texte, audio, vidéo, animation)", duration: "1:08" },
  { time: "01:52", title: "Formats de fichiers supportés (MP3, MP4)", duration: "4:21" },
  { time: "06:13", title: "Utilisation de la balise <video>", duration: "0:40" },
  { time: "06:53", title: "Utilisation de la balise <audio>", duration: "2:02" },
  { time: "08:55", title: "Plug-ins et méthodes héritées (<object>, <embed>)", duration: "1:59" },
  { time: "10:54", title: "Conclusion et bonnes pratiques", duration: "0:08" }
];

const multimediaVideoPoints = [
  { time: "0:00", title: "Introduction", description: "Le multimédia combine texte, audio, vidéo et animation pour créer des expériences web interactives." },
  { time: "0:44", title: "Définition", description: "Les navigateurs offrent une interactivité native avec ces éléments grâce aux balises HTML5." },
  { time: "1:52", title: "Formats supportés", description: "Les formats les plus courants sont MP3 pour l'audio et MP4 pour la vidéo, largement supportés sur toutes les plateformes." },
  { time: "6:13", title: "Balise <video>", description: "Embedder des vidéos avec attributs src, width, height, controls. L'attribut controls ajoute play/pause/volume." },
  { time: "6:53", title: "Balise <audio>", description: "Fonctionne similairement à <video> pour les fichiers audio. L'attribut controls ajoute les contrôles de lecture." },
  { time: "8:55", title: "Plug-ins hérités", description: "Avant HTML5 : <object> et <embed> avec Flash. Ces méthodes sont moins courantes aujourd'hui grâce au support natif." },
  { time: "10:54", title: "Conclusion", description: "Pratiquez l'utilisation des balises multimédia pour rendre vos pages plus engageantes. Toujours inclure les contrôles." }
];

const multimediaTranscript = [
  { time: "00:00", text: "Bienvenue dans ce cours sur le multimédia en HTML. Aujourd'hui, nous allons apprendre à intégrer et utiliser du contenu multimédia dans vos pages web." },
  { time: "00:44", text: "Le multimédia combine texte, audio, vidéo et animation. Les navigateurs offrent une interactivité native avec ces éléments grâce aux balises HTML5." },
  { time: "01:52", text: "Les formats de fichiers supportés incluent MP3 pour l'audio et MP4 pour la vidéo. Ces formats sont largement utilisés à travers toutes les plateformes web." },
  { time: "06:13", text: "La balise <video> permet d'embedder des vidéos avec des attributs comme src, width, height. L'attribut controls ajoute les contrôles de lecture (play, pause, volume)." },
  { time: "06:53", text: "La balise <audio> fonctionne de manière similaire pour les fichiers audio. L'attribut controls ajoute les boutons play, pause et le contrôle du volume." },
  { time: "08:55", text: "Avant HTML5, on utilisait les balises <object> et <embed> pour intégrer du contenu externe via des plug-ins. Ces méthodes sont moins courantes aujourd'hui grâce au support natif d'HTML5." },
  { time: "10:54", text: "En conclusion, pratiquez l'utilisation des balises multimédia pour rendre vos pages plus engageantes. N'oubliez pas d'ajouter l'attribut controls pour que les utilisateurs puissent contrôler la lecture." }
];

  const headChapters = [
  { time: "00:00", title: "Introduction - Qu'est-ce que la balise <head> ?", duration: "0:15" },
  { time: "00:15", title: "Objectif : Contenir les métadonnées", duration: "0:15" },
  { time: "00:30", title: "Les éléments essentiels : title, meta, link", duration: "0:15" },
  { time: "00:45", title: "Pourquoi le <head> est crucial pour le SEO", duration: "0:15" },
  { time: "01:00", title: "Bonnes pratiques et démonstration pratique", duration: "0:15" },
  { time: "01:15", title: "Récapitulatif", duration: "0:17" }
];

const headVideoPoints = [
  { time: "0:00", title: "Introduction", description: "La balise <head> contient des métadonnées sur la page web, pas de contenu visible." },
  { time: "0:15", title: "Métadonnées", description: "Le <head> inclut des informations comme le titre, la description, l'encodage des caractères, et les liens vers des ressources externes." },
  { time: "0:30", title: "Éléments essentiels", description: "Balises principales : <title>, <meta>, <link>, <script>. La balise <title> définit le titre dans l'onglet du navigateur." },
  { time: "0:45", title: "SEO", description: "L'utilisation correcte du <head> améliore le référencement SEO, l'accessibilité et la fonctionnalité globale d'une page web." },
  { time: "1:00", title: "Bonnes pratiques", description: "Incluez toujours UTF-8, la balise viewport pour le responsive, et les métadonnées pour les réseaux sociaux (Open Graph)." },
  { time: "1:15", title: "Récapitulatif", description: "Configuration correcte des métadonnées et des ressources d'une page HTML en utilisant l'élément <head>." }
];

const headTranscript = [
  { time: "00:00", text: "Bienvenue dans ce cours sur la balise <head> en HTML. Aujourd'hui, nous allons explorer cette section essentielle d'une page web qui contient des métadonnées, c'est-à-dire des informations sur la page qui ne sont pas visibles directement par l'utilisateur." },
  { time: "00:15", text: "Le <head> contient des métadonnées sur la page web, pas de contenu visible. Il inclut des éléments comme <title> pour le titre d'onglet, <meta> pour les descriptions et l'encodage des caractères, ainsi que des liens vers des ressources externes comme les feuilles de style CSS." },
  { time: "00:30", text: "Les éléments essentiels du <head> incluent la balise <title>, les balises <meta> pour la description et les mots-clés, les balises <link> pour les feuilles de style et les favicons, et les balises <script> pour le JavaScript." },
  { time: "00:45", text: "L'utilisation correcte du <head> améliore le référencement SEO, l'accessibilité et la fonctionnalité globale d'une page web. Les moteurs de recherche utilisent ces métadonnées pour comprendre et indexer votre contenu." },
  { time: "01:00", text: "Ce tutoriel montre des exemples pratiques de comment structurer un document HTML basique avec une section <head> bien formatée. Nous voyons comment ajouter le jeu de caractères UTF-8, la balise viewport pour le responsive, et les métadonnées pour les réseaux sociaux." },
  { time: "01:15", text: "En résumé, cette vidéo enseigne aux débutants comment configurer correctement les métadonnées et les ressources d'une page HTML en utilisant l'élément <head>. C'est un tutoriel concis mais complet sur les essentiels de la balise <head>." }
];

  const tableChapters = [
  { time: "00:00", title: "Introduction aux tableaux HTML", duration: "0:30" },
  { time: "00:30", title: "Objectif : Organiser des données structurées", duration: "0:30" },
  { time: "01:00", title: "Les balises de base : table, tr, td", duration: "0:30" },
  { time: "01:30", title: "Les en-têtes de colonnes avec <th>", duration: "0:30" },
  { time: "02:00", title: "Structure complète d'un tableau", duration: "0:29" }
];

const tableVideoPoints = [
  { time: "0:00", title: "Introduction", description: "Les tableaux HTML servent à organiser et afficher des informations structurées sur les pages web, comme des données organisées en lignes et colonnes." },
  { time: "0:30", title: "Objectif des tableaux", description: "Présenter des données structurées de manière claire et organisée." },
  { time: "0:45", title: "Balise <table>", description: "Conteneur principal qui définit le tableau." },
  { time: "1:00", title: "Balise <tr>", description: "Table Row - définit une ligne dans le tableau." },
  { time: "1:10", title: "Balise <td>", description: "Table Data - définit une cellule de données standard." },
  { time: "1:30", title: "Balise <th>", description: "Table Header - définit une cellule d'en-tête (généralement en gras et centrée)." },
  { time: "2:00", title: "Structure complète", description: "Combinaison de </table> (tableau), <tr> (lignes), <td>/<th> (cellules)." }
];

const tableTranscript = [
  { time: "00:00", text: "Bienvenue dans ce tutoriel sur les tableaux en HTML. Dans cette vidéo, vous allez apprendre à organiser et afficher des informations structurées sur vos pages web." },
  { time: "00:30", text: "Les tableaux sont utilisés pour organiser et afficher des informations structurées sur les pages web, comme des données organisées en lignes et colonnes." },
  { time: "01:00", text: "Le tableau se construit avec plusieurs balises : <td> pour créer le tableau, <tr> pour définir une ligne, et <td> pour une cellule de données." },
  { time: "01:30", text: "Pour les en-têtes, utilisez la balise <th> (table header) qui sera généralement affichée en gras et centrée. Elle remplace <td> dans les lignes d'en-tête." },
  { time: "02:00", text: "Ce tutoriel est conçu pour les débutants en HTML, montrant étape par étape comment créer un tableau simple et expliquant le fonctionnement de chaque balise." },
  { time: "02:29", text: "Ce tutoriel fait partie d'une série plus large visant à enseigner les fondamentaux du HTML. En résumé, c'est un tutoriel concis qui vous guide à travers les essentiels de la création et du formatage des tableaux en HTML." }
];

  
  const imageChapters = [
    { time: "00:00", title: "Introduction aux images HTML", duration: "2:30" },
    { time: "02:30", title: "La balise <img> et ses attributs (src, alt)", duration: "4:00" },
    { time: "06:30", title: "Dimensionnement des images", duration: "3:30" },
    { time: "10:00", title: "Images cliquables (liens)", duration: "3:00" },
    { time: "13:00", title: "Formats d'images (JPEG, PNG, GIF, WebP, SVG)", duration: "5:00" },
    { time: "18:00", title: "Images responsives et optimisation", duration: "4:00" },
    { time: "22:00", title: "Bonnes pratiques et accessibilité", duration: "3:00" }
  ];

  const cssChapters = [
  { time: "00:00", title: "Introduction : Flexbox vs Grid", duration: "0:51" },
  { time: "00:51", title: "Exemple 1 : Layout de Cartes", duration: "1:17" },
  { time: "02:08", title: "Exemple 2 : Aligner des Boutons en Bas", duration: "1:01" },
  { time: "03:09", title: "Exemple 3 : Layout Complet de Site avec Grid", duration: "1:11" },
  { time: "04:20", title: "Exemple 4 : Layout d'En-tête avec Flexbox", duration: "0:56" },
  { time: "05:16", title: "Exemple 5 : Menu Latéral Vertical avec Flexbox", duration: "0:44" }
];

const cssVideoPoints = [
  { time: "0:01", title: "Introduction", description: "Flexbox est unidimensionnel (1D), Grid est bidimensionnel (2D)." },
  { time: "0:51", title: "Exemple 1 : Layout de Cartes", description: "Flexbox nécessite du style sur l'enfant. Grid fonctionne uniquement avec les paramètres du parent." },
  { time: "2:08", title: "Exemple 2 : Aligner les Boutons", description: "Flexbox = solution avec `flex-grow`. Grid = définition simple `auto 1fr auto`." },
  { time: "3:09", title: "Exemple 3 : Layout de Site", description: "Grid excelle pour les layouts avec des lignes ET colonnes (header, nav, main, footer)." },
  { time: "4:20", title: "Exemple 4 : Layout d'En-tête", description: "Flexbox est parfait pour les layouts sur une seule ligne, avec `justify-content: space-between`." },
  { time: "5:16", title: "Exemple 5 : Menu Latéral", description: "Flexbox pour empiler des éléments avec `margin-top: auto`." }
];

const cssTranscript = [
  { time: "00:00", text: "Dans cette vidéo, vous allez comprendre la vraie différence entre Flexbox et Grid, et surtout, quand utiliser l'un ou l'autre." },
  { time: "00:51", text: "Pour un layout de cartes, Flexbox nécessite de styliser à la fois le parent et les enfants pour garder les cartes de taille égale. Grid, quant à lui, les rend automatiquement de largeur égale avec des réglages simples sur le parent." },
  { time: "02:08", text: "Pour aligner les boutons en bas d'une carte, avec Flexbox, on utilise `flex-grow`. Avec Grid, une simple définition de lignes `auto 1fr auto` suffit." },
  { time: "03:09", text: "Pour un layout complet de site web (header, nav, main, footer), Grid est excellent. Il combine parfaitement les lignes et les colonnes." },
  { time: "04:20", text: "Pour un en-tête avec logo et navigation, Flexbox est le meilleur choix pour un layout sur une seule ligne, avec `justify-content: space-between`." },
  { time: "05:16", text: "Pour les menus latéraux, Flexbox permet d'empiler facilement les éléments en colonne. La propriété `margin-top: auto` pousse un élément (comme 'Paramètres') en bas sans positionnement complexe." }
];

  
const formChapters = [
  { time: "00:00", title: "Introduction aux formulaires HTML", duration: "3:00" },
  { time: "03:00", title: "Structure de base d'un formulaire", duration: "4:00" },
  { time: "07:00", title: "Types de champs HTML5", duration: "5:00" },
  { time: "12:00", title: "Validation des formulaires", duration: "4:00" },
  { time: "16:00", title: "Attributs de formulaire avancés", duration: "4:00" },
  { time: "20:00", title: "Style CSS des formulaires", duration: "3:00" },
  { time: "23:00", title: "Sécurité et bonnes pratiques", duration: "4:00" },
  { time: "27:00", title: "Exercice pratique", duration: "8:00" }
];

  
  const imageVideoPoints = [
    { time: "0:30", title: "La balise <img>", description: "Balise auto-fermante avec attributs src et alt obligatoires" },
    { time: "2:30", title: "Attribut src", description: "Spécifie le chemin ou l'URL de l'image" },
    { time: "3:00", title: "Attribut alt", description: "Texte alternatif pour l'accessibilité et le SEO" },
    { time: "4:30", title: "Dimensions des images", description: "Utilisez width/height pour éviter les sauts de page" },
    { time: "6:30", title: "Images responsives", description: "max-width: 100% pour l'adaptation mobile" },
    { time: "8:00", title: "Images cliquables", description: "Entourez <img> avec <a> pour créer des liens" },
    { time: "10:00", title: "Formats d'images", description: "JPEG pour photos, PNG pour transparence, WebP pour optimisation" },
    { time: "13:00", title: "Optimisation", description: "Compressez vos images pour un chargement plus rapide" }
  ];

  
const formVideoPoints = [
  { time: "0:30", title: "Balise <form>", description: "Conteneur principal avec attributs action et method" },
  { time: "2:00", title: "Méthodes GET vs POST", description: "GET pour recherche, POST pour données sensibles" },
  { time: "4:00", title: "Champ email", description: "type='email' avec validation intégrée" },
  { time: "5:00", title: "Champ téléphone", description: "type='tel' avec pattern pour format" },
  { time: "6:00", title: "Champ nombre", description: "type='number' avec min, max, step" },
  { time: "7:00", title: "Champ date", description: "type='date', 'time', 'datetime-local'" },
  { time: "8:00", title: "Champ range", description: "Curseur pour sélection de valeur" },
  { time: "9:00", title: "Champ color", description: "Sélecteur de couleur" },
  { time: "10:00", title: "Listes déroulantes", description: "<select> et <datalist>" },
  { time: "12:00", title: "Attribut required", description: "Rend un champ obligatoire" },
  { time: "13:00", title: "Attribut pattern", description: "Expression régulière pour validation" },
  { time: "14:00", title: "Attribut placeholder", description: "Texte indicatif dans le champ" },
  { time: "15:00", title: "Groupes de champs", description: "<fieldset> et <legend>" }
];

  
  const imageTranscript = [
    { time: "00:00", text: "Bienvenue dans ce tutoriel vidéo sur les images en HTML. Les images sont essentielles pour enrichir le contenu visuel de vos pages web." },
    { time: "02:30", text: "La balise <img> est utilisée pour insérer des images. C'est une balise auto-fermante qui nécessite les attributs src et alt." },
    { time: "04:30", text: "L'attribut src spécifie la source de l'image. L'attribut alt fournit un texte alternatif pour l'accessibilité." },
    { time: "06:30", text: "Spécifiez toujours les dimensions de vos images avec width et height pour éviter le reflow de la page." },
    { time: "08:00", text: "Pour rendre une image cliquable, il suffit de l'entourer d'une balise <a> avec l'attribut href." },
    { time: "10:00", text: "JPEG est idéal pour les photos, PNG pour les logos avec transparence, WebP offre la meilleure compression." },
    { time: "13:00", text: "Optimisez vos images en les compressant et en utilisant des formats adaptés pour des temps de chargement rapides." }
  ];

  
const formTranscript = [
  { time: "00:00", text: "Bienvenue dans ce tutoriel sur les formulaires HTML avancés. Les formulaires sont essentiels pour collecter des données utilisateur." },
  { time: "03:00", text: "La balise <form> est le conteneur principal. L'attribut action spécifie où envoyer les données, method définit la méthode HTTP." },
  { time: "07:00", text: "Les nouveaux types d'input HTML5 incluent email, tel, number, date, range, et color. Ils apportent une validation intégrée." },
  { time: "12:00", text: "La validation HTML5 utilise required pour les champs obligatoires, pattern pour les regex, min et max pour les valeurs numériques." },
  { time: "16:00", text: "Les attributs avancés comme placeholder, autofocus, disabled, et readonly améliorent l'expérience utilisateur." },
  { time: "20:00", text: "Le style CSS des formulaires permet de créer des designs modernes et cohérents avec le reste du site." },
  { time: "23:00", text: "Pour la sécurité, validez toujours les données côté serveur et utilisez des tokens CSRF." },
  { time: "27:00", text: "Exercice pratique: Créez un formulaire d'inscription complet avec validation." }
];

  
  const generalChapters = [
    { time: "00:00", title: "Introduction", duration: "3:15" },
    { time: "03:15", title: "Structure de base", duration: "4:30" },
    { time: "07:45", title: "Attributs href et target", duration: "5:20" },
    { time: "13:05", title: "Liens internes", duration: "6:10" },
    { time: "19:15", title: "Liens externes", duration: "4:45" },
    { time: "24:00", title: "Pratique", duration: "6:00" }
  ];

  
  const generalTranscript = [
    { time: "00:00", text: "Bienvenue dans ce tutoriel vidéo sur les liens hypertextes en HTML." },
    { time: "03:15", text: "La balise <a> est le point de départ de tout lien. Elle nécessite l'attribut href." },
    { time: "07:45", text: "target='_blank' ouvre le lien dans un nouvel onglet." },
    { time: "13:05", text: "Les liens internes sont cruciaux pour la navigation d'un site." },
    { time: "19:15", text: "Pour les liens externes, utilisez rel='noopener noreferrer'." },
    { time: "24:00", text: "Passons maintenant à la pratique." }
  ];

  
  const generalVideoPoints = [
    { time: "0:35", title: "Les en-têtes HTML", description: "Utilisation des balises <h1> à <h6>" },
    { time: "3:40", title: "Paragraphes et sauts de ligne", description: "Différence entre <p> et <br>" },
    { time: "5:27", title: "Mise en forme du texte", description: "<strong> pour l'importance, <em> pour l'emphase" },
    { time: "8:20", title: "Les listes", description: "<ul> pour les listes non-ordonnées, <ol> pour les listes ordonnées" },
    { time: "12:10", title: "Caractères spéciaux", description: "Utilisation des entités HTML comme &lt;, &gt;" },
    { time: "16:01", title: "Autres balises utiles", description: "<pre>, <hr>, <sup>, <blockquote>" }
  ];

  const semanticChapters = [
  { time: "00:00", title: "Qu'est-ce que le HTML Sémantique ?", duration: "1:30" },
  { time: "01:30", title: "Pourquoi la sémantique est importante (SEO, Accessibilité)", duration: "1:30" },
  { time: "03:00", title: "Les balises structurelles : header, nav, main", duration: "1:30" },
  { time: "04:30", title: "Les balises de contenu : article, section", duration: "2:00" },
  { time: "06:30", title: "Les balises complémentaires : aside, footer", duration: "1:30" },
  { time: "08:00", title: "Les balises pour le contenu multimédia : figure, figcaption", duration: "1:30" },
  { time: "09:30", title: "Le problème du 'Div Soup'", duration: "1:30" },
  { time: "11:00", title: "Bonnes pratiques et récapitulatif", duration: "2:00" }
];

const semanticVideoPoints = [
  { time: "0:30", title: "Définition", description: "HTML sémantique = des balises qui décrivent la signification du contenu, pas son apparence." },
  { time: "1:00", title: "Accessibilité", description: "Les lecteurs d'écran utilisent les balises sémantiques pour naviguer dans la page." },
  { time: "1:30", title: "SEO", description: "Les moteurs de recherche comprennent mieux la structure et le contenu d'une page sémantique." },
  { time: "2:30", title: "<header>", description: "Contient l'en-tête, généralement le logo et le titre, peut être répété." },
  { time: "3:00", title: "<nav>", description: "Pour les blocs de liens de navigation majeurs." },
  { time: "3:30", title: "<main>", description: "Contenu principal unique. Un seul par page." },
  { time: "4:00", title: "<article>", description: "Contenu indépendant (blog post, article de presse, commentaire)." },
  { time: "4:30", title: "<section>", description: "Groupe un contenu thématique connexe (doit avoir un titre)." },
  { time: "5:00", title: "<aside>", description: "Contenu lié indirectement (sidebar, encarts publicitaires)." },
  { time: "5:30", title: "<footer>", description: "Pied de page, contient mentions légales, copyright." },
  { time: "6:00", title: "<figure> & <figcaption>", description: "Regroupe du contenu visuel et sa légende." },
  { time: "6:30", title: "<details> & <summary>", description: "Permet de créer un widget déroulant." },
  { time: "9:00", title: "Div Soup", description: "L'utilisation excessive de <div> rend le code illisible et non-maintenable." }
];

const semanticTranscript = [
  { time: "00:00", text: "Bienvenue dans ce tutoriel sur le HTML sémantique. Aujourd'hui, nous allons voir comment structurer une page web correctement." },
  { time: "01:30", text: "Le HTML sémantique est crucial pour l'accessibilité. Les lecteurs d'écran comme VoiceOver utilisent ces balises pour aider les utilisateurs malvoyants à naviguer." },
  { time: "03:00", text: "Commencez par identifier les grandes régions de votre page : l'en-tête avec <header>, la navigation avec <nav>, et le contenu principal avec <main>." },
  { time: "04:30", text: "Utilisez <article> pour du contenu autonome qui pourrait être distribué, comme un article de blog. Utilisez <section> pour découper votre contenu principal en thèmes." },
  { time: "06:30", text: "<aside> est parfait pour une barre latérale contenant des publicités ou des liens. <footer> conclut la page avec le copyright et les liens de contact." },
  { time: "08:00", text: "N'oubliez pas d'utiliser une balise <figure> pour une image ou un schéma important, et <figcaption> pour lui ajouter une légende." },
  { time: "09:30", text: "Évitez ce qu'on appelle le 'div soup', un code rempli de divs innombrables. C'est mauvais pour l'accessibilité, le SEO et la lisibilité." },
  { time: "11:00", text: "En résumé, privilégiez toujours la balise sémantique adaptée à votre contenu. C'est une bonne pratique qui rendra vos sites web meilleurs." }
];


const cssDefaultQuestions: Question[] = [
  {
    id: 1001,
    question: "Quelle est la différence fondamentale entre Flexbox et CSS Grid ?",
    options: { 
      A: "Flexbox est pour le mobile, Grid pour le desktop", 
      B: "Flexbox est unidimensionnel (1D), Grid est bidimensionnel (2D)", 
      C: "Flexbox est plus récent que Grid", 
      D: "Grid est uniquement pour les images" 
    },
    reponse_correcte: "B",
    points: 10,
    difficulte: "facile",
    explication: "Flexbox gère une seule dimension (ligne OU colonne), alors que Grid gère les deux dimensions (lignes ET colonnes)."
  },
  {
    id: 1002,
    question: "Selon la vidéo, quel système est le plus adapté pour créer un layout de cartes où les cartes ont la même hauteur ?",
    options: { 
      A: "Flexbox requiert du style sur l'enfant", 
      B: "Grid, car il n'a besoin que des paramètres du parent", 
      C: "Aucun des deux ne fonctionne", 
      D: "Il est impossible de faire des cartes de même hauteur" 
    },
    reponse_correcte: "A",
    points: 15,
    difficulte: "moyen",
    explication: "Pour un layout de cartes avec Flexbox, il est nécessaire d'utiliser des propriétés comme `align-items: stretch` sur le parent pour que les enfants aient la même hauteur, ce qui peut parfois nécessiter du style supplémentaire."
  },
  {
    id: 1003,
    question: "Quelle technique avec Flexbox permet d'aligner un élément (comme un bouton 'Paramètres') en bas d'un menu latéral ?",
    options: { 
      A: "`justify-content: flex-end`", 
      B: "`margin-top: auto`", 
      C: "`align-self: baseline`", 
      D: "`position: absolute`" 
    },
    reponse_correcte: "B",
    points: 15,
    difficulte: "difficile",
    explication: "En Flexbox, `margin-top: auto` sur l'élément pousse tout l'espace disponible au-dessus, le plaçant ainsi en bas du conteneur."
  },
  {
    id: 1004,
    question: "Si vous devez créer la structure principale d'une page web (En-tête, Navigation, Contenu principal, Pied de page), quel outil est préférable ?",
    options: { 
      A: "Flexbox, car il est plus simple pour les layouts", 
      B: "Grid, car il excelle avec les lignes ET les colonnes", 
      C: "Float, car c'est une méthode classique", 
      D: "Position absolute" 
    },
    reponse_correcte: "B",
    points: 10,
    difficulte: "moyen",
    explication: "CSS Grid est idéal pour les mises en pages globales à deux dimensions. Il permet de définir facilement des zones comme `header`, `nav`, `main` et `footer`."
  }];

const semanticDefaultQuestions: Question[] = [
  {
    id: 1001,
    question: "Quelle balise HTML5 est utilisée pour définir le contenu principal et unique d'une page ?",
    options: { A: "<header>", B: "<section>", C: "<main>", D: "<article>" },
    reponse_correcte: "C",
    points: 10,
    difficulte: "facile",
    explication: "La balise <main> représente le contenu principal du document, et il ne doit y en avoir qu'une par page."
  },
  {
    id: 1002,
    question: "Quel est l'avantage principal d'utiliser des balises sémantiques plutôt que des balises <div> ?",
    options: { A: "Un chargement plus rapide", B: "Une meilleure accessibilité et un meilleur référencement SEO", C: "Des couleurs par défaut plus jolies", D: "La compatibilité avec tous les navigateurs" },
    reponse_correcte: "B",
    points: 15,
    difficulte: "moyen",
    explication: "Les balises sémantiques aident les technologies d'assistance et les moteurs de recherche à comprendre la structure et le rôle du contenu."
  },
  {
    id: 1003,
    question: "Quelle est la bonne structure pour regrouper une image et sa légende ?",
    options: { A: "<div><img><span>", B: "<image><description>", C: "<figure><img><figcaption></figure>", D: "<media><img><legend>" },
    reponse_correcte: "C",
    points: 10,
    difficulte: "moyen",
    explication: "<figure> s'utilise pour du contenu multimédia (image, graphique) et <figcaption> pour lui associer une légende."
  }
];

  
  const imageQuestions: Question[] = [
    {
      id: 101,
      question: "Quels sont les deux attributs obligatoires de la balise <img> ?",
      options: { A: "src et width", B: "src et height", C: "src et alt", D: "alt et title" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "Les attributs src (source) et alt (texte alternatif) sont obligatoires pour une balise <img> valide."
    },
    {
      id: 102,
      question: "À quoi sert l'attribut 'alt' dans une balise <img> ?",
      options: { 
        A: "Définir la hauteur de l'image", 
        B: "Définir la largeur de l'image", 
        C: "Fournir un texte alternatif pour l'accessibilité", 
        D: "Définir le titre de l'image au survol" 
      },
      reponse_correcte: "C",
      points: 10,
      difficulte: "facile",
      explication: "L'attribut 'alt' décrit le contenu de l'image pour les lecteurs d'écran et s'affiche si l'image ne peut pas être chargée."
    },
    {
      id: 103,
      question: "Quel format d'image est recommandé pour les logos avec transparence ?",
      options: { A: "JPEG", B: "GIF", C: "PNG", D: "BMP" },
      reponse_correcte: "C",
      points: 10,
      difficulte: "moyen",
      explication: "Le format PNG supporte la transparence et est idéal pour les logos et les images nécessitant un fond transparent."
    },
    {
      id: 104,
      question: "Comment rendre une image cliquable ?",
      options: { 
        A: "<img src='image.jpg' href='https://example.com'>", 
        B: "<a href='https://example.com'><img src='image.jpg' alt='Description'></a>", 
        C: "<img src='image.jpg' link='https://example.com'>", 
        D: "<image src='image.jpg' url='https://example.com'>" 
      },
      reponse_correcte: "B",
      points: 15,
      difficulte: "moyen",
      explication: "Pour rendre une image cliquable, il faut l'entourer d'une balise <a> avec l'attribut href."
    },
    {
      id: 105,
      question: "Quelle propriété CSS permet de rendre une image responsive ?",
      options: { A: "width: 100%", B: "max-width: 100%; height: auto", C: "display: block", D: "position: relative" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "moyen",
      explication: "max-width: 100% et height: auto permettent à l'image de s'adapter à son conteneur tout en conservant ses proportions."
    }
  ];

  const saveMistakesToDB = async (userId: number, courseId: number, wrongQuestions: { question: string; questionId: number }[]) => {
  if (!userId || !courseId || wrongQuestions.length === 0) return;
  
  try {
    const mistakesToSave = wrongQuestions.map(q => ({
      cours_id: courseId,
      question_id: q.questionId,
      question_texte: q.question,
      reponse_utilisateur: userAnswers[q.questionId] || '',
      reponse_correcte: questions.find(qu => qu.id === q.questionId)?.reponse_correcte || '',
      mode_apprentissage: 'video',
      points_possibles: 10
    }));
    
    await mistakeService.saveBatchMistakes(mistakesToSave);
    console.log(' Erreurs sauvegardées en DB');
  } catch (error) {
    console.error(' Erreur sauvegarde DB:', error);
  }
};

const loadMistakesFromDB = async (userId: number, courseId: number) => {
  if (!userId || !courseId) return [];
  
  try {
    const mistakes = await mistakeService.getMyMistakes(courseId, 'video', 30);
    const mistakeTexts = mistakes.map((m: any) => m.question_texte);
    
    
    if (mistakeTexts.length !== mistakeQuestions.length) {
      setMistakeQuestions(mistakeTexts);
    }
    
    console.log(` ${mistakeTexts.length} erreurs chargées depuis la DB`);
    return mistakeTexts;
  } catch (error) {
    console.error(' Erreur chargement erreurs:', error);
    return [];
  }
};

const generatePersonalizedQuiz = async () => {
  if (!selectedCourse || !user?.id) {
    console.log(' Pas de cours sélectionné ou utilisateur non connecté');
    return;
  }
  
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
      
      await loadQuestionsForCourse(selectedCourse.id);
      return;
    }
    
    
    const fallbackQuestions = generateFallbackQuestionsFromMistakes(mistakes);
    
    if (fallbackQuestions.length > 0) {
      setQuestions(fallbackQuestions);
      const toast = document.createElement('div');
      toast.className = 'fixed bottom-4 right-4 bg-green-500 text-white px-4 py-2 rounded-lg shadow-lg z-50';
      toast.textContent = `🎯 Quiz personnalisé généré! Basé sur ${mistakes.length} erreur(s)`;
      document.body.appendChild(toast);
      setTimeout(() => toast.remove(), 3000);
      return;
    }
    
    await loadQuestionsForCourse(selectedCourse.id);
    
  } catch (error) {
    console.error(' Erreur génération quiz personnalisé:', error);
    await loadQuestionsForCourse(selectedCourse.id);
  } finally {
    setGeneratingQuiz(false);
  }
};

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
    },
    "Quelle est la différence entre Flexbox et CSS Grid ?": {
      id: 9993,
      question: "Quelle est la différence fondamentale entre Flexbox et CSS Grid ?",
      options: {
        A: "Flexbox est 1D, Grid est 2D",
        B: "Flexbox est pour mobile, Grid pour desktop",
        C: "Ils font la même chose",
        D: "Grid est plus rapide que Flexbox"
      },
      reponse_correcte: "A",
      points: 15,
      difficulte: "moyen",
      explication: "Flexbox gère une seule dimension (ligne OU colonne), Grid gère les deux dimensions (lignes ET colonnes)."
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
          A: "Révisez ce concept dans la leçon vidéo",
          B: "Consultez la documentation officielle",
          C: "Pratiquez avec des exercices supplémentaires",
          D: "Revoyez la vidéo explicative"
        },
        reponse_correcte: "A",
        points: 10,
        difficulte: "moyen",
        explication: `Pour maîtriser ce concept, révisez la section: ${mistake}`
      });
    }
  }
  
  return questions.slice(0, 5);
};

  
  const getChaptersForCourse = (courseId: number) => {
    if (courseId === 12) return imageChapters;
    if (courseId === 8) return formChapters;
    if (courseId === 9) return semanticChapters;
    if (courseId === 10) return cssChapters;
    if (courseId === 13) return tableChapters;
    if (courseId === 14) return headChapters;
    if (courseId === 15) return multimediaChapters;
    if (courseId === 16) return cssMediaQueryChapters;
    if (courseId === 17) return cssSelectorsChapters;
    if (courseId === 18) return cssColorsChapters;
    if (courseId === 19) return cssBackgroundChapters;
    if (courseId === 20) return cssBorderChapters;
    if (courseId === 22) return cssMarginChapters;
    if (courseId === 23) return cssPaddingChapters;
    if (courseId === 24) return cssTextChapters;
    if (courseId === 25) return cssFontChapters;
    if (courseId === 26) return cssLinksChapters;
    if (courseId === 27) return cssListsChapters;
    if (courseId === 28) return cssTablesChapters;
    if (courseId === 29) return cssDisplayVisibilityChapters;
    if (courseId === 30) return cssPositioningChapters;
    if (courseId === 31) return cssOverflowChapters;
    if (courseId === 32) return cssFloatChapters;
    if (courseId === 33) return jsIntroductionChapters;
    if (courseId === 34) return jsVariablesChapters;
    if (courseId === 35) return jsDataTypesChapters;
    if (courseId === 36) return jsOperatorsChapters;
    if (courseId === 37) return jsConditionsChapters;
    if (courseId === 38) return jsLoopsChapters;
    if (courseId === 39) return jsStringMethodsChapters;
    if (courseId === 40) return jsNumbersChapters;
    if (courseId === 41) return jsFunctionsChapters;
    if (courseId === 42) return jsObjectsChapters;
    if (courseId === 43) return jsArraysChapters;
    if (courseId === 44) return jsSetsChapters;
    if (courseId === 45) return jsMapsChapters;
    if (courseId === 46) return jsMathChapters;
    if (courseId === 47) return jsRegexChapters;
    if (courseId === 48) return jsEventsChapters;
    return generalChapters;
  };

  
  const getVideoPointsForCourse = (courseId: number) => {
    if (courseId === 12) return imageVideoPoints;
    if (courseId === 8) return formVideoPoints;
    if (courseId === 9) return semanticVideoPoints;
    if (courseId === 10) return cssVideoPoints;
    if (courseId === 13) return tableVideoPoints;
    if (courseId === 14) return headVideoPoints;
    if (courseId === 15) return multimediaVideoPoints;
    if (courseId === 16) return cssMediaQueryVideoPoints;
    if (courseId === 17) return cssSelectorsVideoPoints;
    if (courseId === 18) return cssColorsVideoPoints;
    if (courseId === 19) return cssBackgroundVideoPoints;
    if (courseId === 20) return cssBorderVideoPoints;
    if (courseId === 22) return cssMarginVideoPoints;
    if (courseId === 23) return cssPaddingVideoPoints;
    if (courseId === 24) return cssTextVideoPoints;
    if (courseId === 25) return cssFontVideoPoints;
    if (courseId === 26) return cssLinksVideoPoints;
    if (courseId === 27) return cssListsVideoPoints;
    if (courseId === 28) return cssTablesVideoPoints;
    if (courseId === 29) return cssDisplayVisibilityVideoPoints;
    if (courseId === 30) return cssPositioningVideoPoints;
    if (courseId === 31) return cssOverflowVideoPoints;
    if (courseId === 32) return cssFloatVideoPoints;
    if (courseId === 33) return jsIntroductionVideoPoints;
    if (courseId === 34) return jsVariablesVideoPoints;
    if (courseId === 35) return jsDataTypesVideoPoints;
    if (courseId === 36) return jsOperatorsVideoPoints;
    if (courseId === 37) return jsConditionsVideoPoints;
    if (courseId === 38) return jsLoopsVideoPoints;
    if (courseId === 39) return jsStringMethodsVideoPoints;
    if (courseId === 40) return jsNumbersVideoPoints;
    if (courseId === 41) return jsFunctionsVideoPoints;
    if (courseId === 42) return jsObjectsVideoPoints;
    if (courseId === 43) return jsArraysVideoPoints;
    if (courseId === 44) return jsSetsVideoPoints;
    if (courseId === 45) return jsMapsVideoPoints;
    if (courseId === 46) return jsMathVideoPoints;
    if (courseId === 47) return jsRegexVideoPoints;
    if (courseId === 48) return jsEventsVideoPoints;
    return generalVideoPoints;
  };

  
  const getTranscriptForCourse = (courseId: number) => {
    if (courseId === 12) return imageTranscript;
    if (courseId === 8) return formTranscript;
    if (courseId === 9) return semanticTranscript;
    if (courseId === 10) return cssTranscript;
    if (courseId === 13) return tableTranscript;
    if (courseId === 14) return headTranscript;
    if (courseId === 15) return multimediaTranscript;
    if (courseId === 16) return cssMediaQueryTranscript;
    if (courseId === 17) return cssSelectorsTranscript;
    if (courseId === 18) return cssColorsTranscript;
    if (courseId === 19) return cssBackgroundTranscript;
    if (courseId === 20) return cssBorderTranscript;
    if (courseId === 22) return cssMarginTranscript;
    if (courseId === 23) return cssPaddingTranscript;
    if (courseId === 24) return cssTextTranscript;
    if (courseId === 25) return cssFontTranscript;
    if (courseId === 26) return cssLinksTranscript;
    if (courseId === 27) return cssListsTranscript;
    if (courseId === 28) return cssTablesTranscript;
    if (courseId === 29) return cssDisplayVisibilityTranscript;
    if (courseId === 30) return cssPositioningTranscript;
    if (courseId === 31) return cssOverflowTranscript;
    if (courseId === 32) return cssFloatTranscript;
    if (courseId === 33) return jsIntroductionTranscript;
    if (courseId === 34) return jsVariablesTranscript;
    if (courseId === 35) return jsDataTypesTranscript;
    if (courseId === 36) return jsOperatorsTranscript;
    if (courseId === 37) return jsConditionsTranscript;
    if (courseId === 38) return jsLoopsTranscript;
    if (courseId === 39) return jsStringMethodsTranscript;
    if (courseId === 40) return jsNumbersTranscript;
    if (courseId === 41) return jsFunctionsTranscript;
    if (courseId === 42) return jsObjectsTranscript;
    if (courseId === 43) return jsArraysTranscript;
    if (courseId === 44) return jsSetsTranscript;
    if (courseId === 45) return jsMapsTranscript;
    if (courseId === 46) return jsMathTranscript;
    if (courseId === 47) return jsRegexTranscript;
    if (courseId === 48) return jsEventsTranscript;
    return generalTranscript;
  };

  
  const defaultQuestions: Record<number, Question[]> = {
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
      explication: "Le flag 'g' signifie global et trouve toutes les occurrences."
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
      explication: "search() retourne l'index de la première correspondance."
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
      explication: "Math.round() arrondit à l'entier le plus proche."
    },
    {
      id: 4602,
      question: "Comment obtenir la valeur de Pi en JavaScript ?",
      options: { A: "Math.Pi", B: "Math.PI", C: "Math.pi", D: "Math.PI()" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "Math.PI donne la constante mathématique π."
    },
    {
      id: 4603,
      question: "Quelle méthode supprime la partie décimale d'un nombre ?",
      options: { A: "Math.round()", B: "Math.floor()", C: "Math.ceil()", D: "Math.trunc()" },
      reponse_correcte: "D",
      points: 10,
      difficulte: "facile",
      explication: "Math.trunc() supprime la partie décimale."
    },
    {
      id: 4604,
      question: "Comment générer un nombre aléatoire entre 0 et 1 ?",
      options: { A: "Math.random()", B: "Math.random(1)", C: "Math.rand()", D: "Math.randomBetween(0,1)" },
      reponse_correcte: "A",
      points: 10,
      difficulte: "facile",
      explication: "Math.random() retourne un nombre aléatoire entre 0 et 1."
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
      explication: "Math.max() retourne la plus grande valeur, donc 10."
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
      explication: "Math.floor() arrondit vers le bas, donc 4."
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
      explication: "Map permet d'utiliser n'importe quel type de données comme clé."
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
  ],

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
      question: "Quelle propriété permet de combiner les avantages de block et inline (permet largeur/hauteur mais pas de saut de ligne) ?",
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
  ]
  ,
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
        explication: "<strong> a une signification sémantique."
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
        explication: "Les serveurs web sont configurés pour servir automatiquement 'index.html'."
      },
      {
        id: 5,
        question: "Comment créer un lien qui ouvre une page externe dans un nouvel onglet ?",
        options: {
          A: "<a href='https://example.com' target='_new'>Exemple</a>",
          B: "<a href='https://example.com' newtab>Exemple</a>",
          C: "<a href='https://example.com' target='_blank'>Exemple</a>",
          D: "<a href='https://example.com' open='new'>Exemple</a>"
        },
        reponse_correcte: "C",
        points: 15,
        difficulte: "moyen",
        explication: "L'attribut target='_blank' ouvre le lien dans un nouvel onglet."
      },
      {
        id: 6,
        question: "Vous avez la structure : site/index.html et site/produits/liste.html. Quel chemin utiliser depuis liste.html pour revenir à index.html ?",
        options: {
          A: "<a href='../index.html'>Accueil</a>",
          B: "<a href='./index.html'>Accueil</a>",
          C: "<a href='/index.html'>Accueil</a>",
          D: "<a href='index.html'>Accueil</a>"
        },
        reponse_correcte: "A",
        points: 15,
        difficulte: "moyen",
        explication: "Le chemin '../' remonte d'un niveau dans l'arborescence."
      }
    ],
    12: imageQuestions,
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
      explication: "L'attribut 'controls' affiche les contrôles de lecture natifs du navigateur (play, pause, volume, progression)."
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
      explication: "Il est recommandé d'éviter l'autoplay car cela peut être intrusif pour l'utilisateur. La plupart des navigateurs bloquent également l'autoplay avec son."
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
      explication: "HTML5 signifie HyperText Markup Language version 5, la dernière version majeure qui a introduit les balises <video> et <audio> natives."
    },
    {
      id: 1510,
      question: "Quel attribut permet de lancer automatiquement une vidéo dès le chargement de la page ?",
      options: { A: "start", B: "autoplay", C: "auto", D: "play" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "L'attribut 'autoplay' démarre la vidéo automatiquement dès que la page est chargée. Attention à l'expérience utilisateur."
    }
  ],
    8: [  
    {
      id: 101,
      question: "Quelle méthode HTTP est recommandée pour envoyer des données sensibles ?",
      options: { A: "GET", B: "POST", C: "PUT", D: "DELETE" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "POST est recommandé pour les données sensibles car les données sont dans le corps de la requête."
    },
    {
      id: 102,
      question: "Quel attribut rend un champ de formulaire obligatoire ?",
      options: { A: "mandatory", B: "required", C: "obligatory", D: "force" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "L'attribut 'required' rend un champ obligatoire dans HTML5."
    },
    {
      id: 103,
      question: "Quel type d'input HTML5 est utilisé pour les emails ?",
      options: { A: "type='text'", B: "type='email'", C: "type='mail'", D: "type='contact'" },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "type='email' active la validation automatique du format email."
    },
    {
      id: 104,
      question: "Quel attribut définit une expression régulière pour valider un champ ?",
      options: { A: "regex", B: "validate", C: "pattern", D: "format" },
      reponse_correcte: "C",
      points: 15,
      difficulte: "moyen",
      explication: "L'attribut 'pattern' permet de définir une expression régulière pour valider le champ."
    }
  ],
  9: semanticDefaultQuestions,
  10: cssDefaultQuestions,
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
    },
    {
      id: 1305,
      question: "Que signifie l'abréviation <th> en HTML ?",
      options: { 
        A: "Table Height", 
        B: "Table Header", 
        C: "Table Hyperlink", 
        D: "Table Holder" 
      },
      reponse_correcte: "B",
      points: 10,
      difficulte: "facile",
      explication: "<th> signifie 'Table Header' - c'est une cellule d'en-tête de tableau."
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
      explication: "Cette balise définit l'encodage des caractères en UTF-8, permettant d'afficher correctement tous les caractères (accents, symboles, emojis, etc.)."
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
      explication: "La balise <link rel='icon' type='image/x-icon' href='favicon.ico'> permet d'ajouter une icône personnalisée dans l'onglet du navigateur."
    },
    {
      id: 1407,
      question: "Quelle balise meta est essentielle pour le responsive design sur mobile ?",
      options: { 
        A: "<meta name='responsive'>", 
        B: "<meta name='viewport' content='width=device-width, initial-scale=1.0'>", 
        C: "<meta name='mobile'>", 
        D: "<meta name='scale'>" 
      },
      reponse_correcte: "B",
      points: 15,
      difficulte: "moyen",
      explication: "La balise viewport contrôle comment la page s'affiche sur les appareils mobiles. 'width=device-width, initial-scale=1.0' rend la page responsive."
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

  useEffect(() => {
    loadCourses();
    const savedProgress = localStorage.getItem('video_progress');
    if (savedProgress) setVideoProgress(parseInt(savedProgress));
    const savedNotes = localStorage.getItem('video_notes');
    if (savedNotes) setNotes(savedNotes);
  }, []);

  useEffect(() => {
    if (selectedCourse && selectedCourse.id) {
      loadQuestionsForCourse(selectedCourse.id);
    }
  }, [selectedCourse]);

  const loadCourses = async () => {
    try {
      setLoading(true);
      const allCourses = await courseService.getAllCourses();
      setCourses(allCourses);
      
      const videoCourses = allCourses.filter(c => c.id === 6 ||
         c.id === 11 || c.id === 12 || c.id === 8 || c.id === 9 ||
          c.id === 10 || c.id === 13 || c.id === 14 || c.id === 15 || c.id === 16 ||
           c.id === 17 || c.id === 18 || c.id===19 || c.id === 20 ||c.id===22 ||
            c.id===23 || c.id===24 || c.id===25 || c.id===26 
            || c.id===27 || c.id===28 || c.id===29 || c.id===30 
            || c.id===31 || c.id===32 || c.id===33 || c.id===34 ||
             c.id===35 || c.id===36 || c.id===37 || c.id===38 || c.id===39
              || c.id===40 || c.id===41 || 
              c.id===42 || c.id===43 || c.id===44 || c.id===45 || c.id===46 || c.id===47 || c.id===48);
      if (videoCourses.length > 0) {
        setSelectedCourse(videoCourses[0]);
      } else if (allCourses.length > 0) {
        setSelectedCourse(allCourses[0]);
      }
    } catch (error) {
      console.error('Erreur chargement cours:', error);
      setError('Impossible de charger les cours');
    } finally {
      setLoading(false);
    }
  };

 const loadQuestionsForCourse = async (courseId: number) => {
  try {
    setLoadingQuestions(true);
    const response = await api.get(`/courses/${courseId}/questions?mode=video`);
    const questionsData = response.data;
    
    console.log('📋 Questions reçues du backend pour cours', courseId, ':', questionsData);
    
    if (questionsData && questionsData.length > 0) {
      const filteredQuestions = questionsData.filter((q: any) => 
        q.mode_specifique === 'video' || q.mode_specifique === null || !q.mode_specifique
      );
      
      if (filteredQuestions.length > 0) {
        const formattedQuestions = filteredQuestions.map((q: any) => ({
          id: q.id,
          question: q.question,
          options: q.options || {},
          reponse_correcte: q.reponse_correcte,
          points: q.points || 10,
          difficulte: q.difficulte || 'moyen',
          explication: q.explication
        }));
        setQuestions(formattedQuestions);
        
        
        if (user?.id) {
          await loadMistakesFromDB(user.id, courseId);
        }
        return;
      }
    }
    
    console.log(' Utilisation des questions par défaut pour le cours', courseId);
    const defaultQs = defaultQuestions[courseId] || defaultQuestions[11];
    setQuestions(defaultQs);
    
  } catch (error) {
    console.error(' Erreur chargement questions:', error);
    const defaultQs = defaultQuestions[selectedCourse?.id || 11] || defaultQuestions[11];
    setQuestions(defaultQs);
  } finally {
    setLoadingQuestions(false);
  }
};

  const handleCourseChange = async (courseId: number) => {
    const course = courses.find(c => c.id === courseId);
    if (course) {
      setSelectedCourse(course);
      setQuizSubmitted(false);
      setUserAnswers({});
      setQuizScore(0);
      setShowExplanation({});
      setQuizResultId(null);
      setVideoProgress(0);
      setExamResult(null);
      setExamAnswers({});
      setVideoProgress(0);
      setExamMode(false);
      setExamSubmitted(false);
       setShowRecommendations(false);
       window.scrollTo({ top: 0, behavior: 'smooth' });
      await loadQuestionsForCourse(courseId);
    }
  };

  const handleProgressChange = (progress: number) => {
    setVideoProgress(progress);
    localStorage.setItem('video_progress', progress.toString());
  };

  const handleAnswerSelect = (questionId: number, answer: string) => {
    setUserAnswers(prev => ({ ...prev, [questionId]: answer }));
  };

  const toggleExplanation = (questionId: number) => {
    setShowExplanation(prev => ({ ...prev, [questionId]: !prev[questionId] }));
  };

  const saveNotes = () => {
    localStorage.setItem('video_notes', notes);
    alert('Notes sauvegardées !');
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
      console.log(' Erreur enregistrée:', q.question);
    }
    
    responses.push({
      question_id: q.id,
      reponse_utilisateur: userAnswer || '',
      est_correcte: isCorrect,
      temps_reponse: 45
    });
  }

  console.log(' Total des erreurs:', wrongQuestionsList.length);

  
  if (wrongQuestionsList.length > 0 && user?.id && selectedCourse?.id) {
    await saveMistakesToDB(user.id, selectedCourse.id, wrongQuestionsList);
    await loadMistakesFromDB(user.id, selectedCourse.id);
    
    
    const wrongQuestionTexts = wrongQuestionsList.map(w => w.question);
    await analyzeMistakesAndRecommend(wrongQuestionTexts);
  }

  const percentage = (totalScore / maxScore) * 100;
  const isSuccess = percentage >= 70;
  const timeSpent = Math.max(Math.floor(videoProgress / 2), 1);
  const completionRate = videoProgress;

  const resultData = {
    utilisateur_id: user.id,
    cours_id: Number(selectedCourse.id),
    mode: 'video',
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
      successMessage += `\n\n🤖 Tuteur IA: Analyse de vos erreurs en cours...\nLes recommandations apparaîtront sous le quiz.`;
    }
    alert(successMessage);
  } catch (error: any) {
    console.error(' Erreur:', error);
    alert(`Erreur: ${error.response?.data?.detail || 'Erreur inconnue'}`);
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
        
        
        const cleanOptions: Record<string, string> = {};
        const optionKeys = ['A', 'B', 'C', 'D'];
        
        
        if (questionText.includes("surligner")) {
          options = { A: "<mark>", B: "<highlight>", C: "<strong>", D: "<em>" };
        } else if (questionText.includes("pliable") || questionText.includes("dépliable")) {
          options = { A: "<details> et <summary>", B: "<collapse> et <expand>", 
                      C: "<fold> et <unfold>", D: "<hide> et <show>" };
        } else if (questionText.includes("sémantique")) {
          options = { A: "Meilleur SEO et accessibilité", B: "Chargement plus rapide",
                      C: "Design plus joli", D: "Compatibilité avec plus de navigateurs" };
        } else if (questionText.includes("modifier le contenu texte") || questionText.includes("innerHTML")) {
          options = { A: "element.value = nouveauTexte", B: "element.innerHTML = nouveauTexte",
                      C: "element.text = nouveauTexte", D: "element.content = nouveauTexte" };
        } else if (questionText.includes("titre principal")) {
          options = { A: "<title>", B: "<h1>", C: "<head>", D: "<header>" };
        } else if (questionText.includes("ligne dans un tableau")) {
          options = { A: "<tr>", B: "<td>", C: "<th>", D: "<thead>" };
        } else if (questionText.includes("cellule d'en-tête")) {
          options = { A: "<td>", B: "<tr>", C: "<th>", D: "<thead>" };
        } else if (questionText.includes("taille du texte") || questionText.includes("font-size")) {
          options = { A: "text-size", B: "font-size", C: "size", D: "text-scale" };
        } else if (questionText.includes("sélecteur") && questionText.includes("paragraphes")) {
          options = { A: "p", B: "#paragraph", C: ".paragraph", D: "<p>" };
        } else if (questionText.includes("méthode HTTP") && questionText.includes("formulaire")) {
          options = { A: "GET", B: "POST", C: "PUT", D: "DELETE" };
        } else if (questionText.includes("barrer le texte") || questionText.includes("line-through")) {
          options = { A: "underline", B: "overline", C: "line-through", D: "none" };
        } else {
          
          for (let i = 0; i < optionKeys.length; i++) {
            const key = optionKeys[i];
            const value = options[key] || `Option ${key}`;
            let cleanValue = String(value);
            cleanValue = cleanValue.replace(/^['"]+/, '').replace(/['"]+$/, '');
            cleanValue = cleanValue.trim();
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
        }
        
        
        for (let i = 0; i < optionKeys.length; i++) {
          const key = optionKeys[i];
          const value = options[key as keyof typeof options];
          let cleanValue = String(value);
          cleanValue = cleanValue.replace(/^['"]+/, '').replace(/['"]+$/, '');
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
    await loadRegularQuiz();
  } finally {
    setGeneratingQuiz(false);
  }
};

const loadRegularQuiz = async () => {
  if (!selectedCourse) return;
  
  try {
    setLoadingQuestions(true);
    setQuizGenerationMode('default');
    
    const response = await api.get(`/courses/${selectedCourse.id}/questions?mode=video`);
    const questionsData = response.data;
    
    if (questionsData && questionsData.length > 0) {
      const filteredQuestions = questionsData.filter((q: any) => 
        q.mode_specifique === 'video' || q.mode_specifique === null || !q.mode_specifique
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
      const defaultQs = getDefaultQuestionsForVideo();
      setQuestions(defaultQs);
    }
  } catch (error) {
    console.error('Erreur chargement quiz:', error);
    const defaultQs = getDefaultQuestionsForVideo();
    setQuestions(defaultQs);
  } finally {
    setLoadingQuestions(false);
  }
};

  const resetQuiz = () => {
    setUserAnswers({});
    setQuizSubmitted(false);
    setQuizScore(0);
    setQuizResultId(null);
    setShowExplanation({});
  };

  useEffect(() => {
  if (selectedCourse && selectedCourse.id && user?.id) {
    loadMistakesFromDB(user.id, selectedCourse.id);
  }
}, [selectedCourse, user?.id]);

const updateLearningContext = useCallback(() => {
  if (setLearningContextValue) {
    setLearningContextValue({
      generatePersonalizedQuiz: generatePersonalizedQuiz,
      showTutorRecommendations: () => {
        if (mistakeQuestions.length > 0) {
          analyzeMistakesAndRecommend(mistakeQuestions);
        } else {
          alert('Aucune erreur enregistrée pour ce cours');
        }
      },
      showMistakeStats: showMistakeStats,
      generateBertQuiz: generateBertQuiz,
      generateExam: generateFinalExam,
      cancelExam: cancelExam,
      isExamMode: examMode,
      hasMistakes: mistakeQuestions.length > 0,
      isGeneratingQuiz: generatingQuiz,
      isGeneratingExam: generatingExam,
      selectedCourseId: selectedCourse?.id
    });
  }
}, [
  selectedCourse?.id,  
  mistakeQuestions.length,  
  examMode,
  generatingQuiz,
  generatingExam,
  setLearningContextValue
]);

useEffect(() => {
  updateLearningContext();
}, [updateLearningContext]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="text-4xl mb-4">🎬</div>
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

  const currentVideoInfo = selectedCourse ? videoMapping[selectedCourse.id] : videoMapping[11];
  const videoId = currentVideoInfo?.videoId || "gJ_G-gxQRRk";
  const embedUrl = `https://www.youtube.com/embed/${videoId}?rel=0&showinfo=0&modestbranding=1`;
  
  const currentChapters = getChaptersForCourse(selectedCourse?.id || 11);
  const currentVideoPoints = getVideoPointsForCourse(selectedCourse?.id || 11);
  const currentTranscript = getTranscriptForCourse(selectedCourse?.id || 11);

 return (
  <div className="min-h-screen bg-gray-100">
    <div className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
      <div className="space-y-8">
        
        {/* En-tête */}
        <div className="bg-gradient-to-r from-red-500 to-red-700 rounded-2xl p-6 text-white">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div>
              <h1 className="text-3xl font-bold mb-2">
                {examMode ? '📝 Examen Final' : '🎬 Apprentissage par Vidéo'}
              </h1>
              <p className="opacity-90">
                {examMode 
                  ? `Évaluez vos connaissances sur ${selectedCourse?.titre}`
                  : 'Apprenez HTML à travers des tutoriels vidéo interactifs'}
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
          <h3 className="text-sm font-semibold text-gray-500 mb-3">📚 Sélectionner un cours vidéo</h3>
          
          
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
                    ? `${cat.bgColor} ${cat.color} ring-2 ring-offset-1 ring-${cat.color.replace('text-', '')}`
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
                  onClick={() => handleCourseChange(course.id)}
                  className={`p-2 rounded-lg text-center transition-all duration-200 ${
                    isSelected 
                      ? 'bg-red-100 border-2 border-red-500 text-red-700' 
                      : 'bg-gray-50 hover:bg-gray-100 text-gray-700 border-2 border-transparent'
                  }`}
                >
                  <div className="text-2xl">{icon}</div>
                  <div className={`text-xs font-medium truncate mt-1 ${isSelected ? 'text-red-700' : categoryColor}`}>
                    {course.titre}
                  </div>
                  {isSelected && (
                    <div className="text-[10px] text-red-500 mt-0.5">▶ En cours</div>
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


        
        {selectedCourse && (
          <div className="bg-white rounded-xl shadow-md p-6">
            <h2 className="text-xl font-bold text-gray-800">{currentVideoInfo?.title || selectedCourse.titre}</h2>
            <p className="text-gray-600 mt-1">{currentVideoInfo?.description || selectedCourse.description || 'Apprenez les bases du HTML'}</p>
            <div className="flex flex-wrap gap-4 mt-2">
              <span className="text-sm text-gray-500">📊 Niveau: {selectedCourse.difficulte || 'Débutant'}</span>
              <span className="text-sm text-gray-500">⏱️ Durée: {currentVideoInfo?.duration || '25'} min</span>
            </div>
          </div>
        )}

        
        <div className="bg-white rounded-xl shadow-lg p-4 sm:p-6 md:p-8">
          <h3 className="text-lg sm:text-xl font-bold mb-4">🎬 Lecteur Vidéo - {currentVideoInfo?.title}</h3>
          
          <div className="aspect-video bg-black rounded-lg overflow-hidden">
            <iframe
              src={embedUrl}
              title="YouTube video player"
              frameBorder="0"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
              className="w-full h-full"
            />
          </div>

         
          <div className="mt-4 grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-600">⚡ Vitesse:</span>
              <select
                value={playbackSpeed}
                onChange={(e) => setPlaybackSpeed(parseFloat(e.target.value))}
                className="px-3 py-1 border rounded-lg text-sm flex-1"
              >
                <option value="0.5">0.5x</option>
                <option value="0.75">0.75x</option>
                <option value="1.0">1.0x</option>
                <option value="1.25">1.25x</option>
                <option value="1.5">1.5x</option>
                <option value="2.0">2.0x</option>
              </select>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-600">🎬 Qualité:</span>
              <select
                value={quality}
                onChange={(e) => setQuality(e.target.value)}
                className="px-3 py-1 border rounded-lg text-sm flex-1"
              >
                <option value="360p">360p</option>
                <option value="480p">480p</option>
                <option value="720p">720p</option>
                <option value="1080p">1080p</option>
              </select>
            </div>
            <div className="text-sm text-gray-600 text-right flex items-center justify-end">
              Progression: {Math.floor(videoProgress)}%
            </div>
          </div>
        </div>

        
        <div className="bg-white rounded-xl shadow-md p-4 sm:p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-base sm:text-lg font-semibold">📊 Progression vidéo</h3>
            <span className="text-sm text-gray-500">{videoProgress}%</span>
          </div>
          <input
            type="range"
            min="0"
            max="100"
            value={videoProgress}
            onChange={(e) => handleProgressChange(parseInt(e.target.value))}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
          />
          <button
            onClick={() => handleProgressChange(100)}
            className="mt-4 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition text-sm w-full sm:w-auto"
          >
            ✅ Marquer comme terminé
          </button>
        </div>

        
        <div className="bg-white rounded-xl shadow-md p-4 sm:p-6">
          <h3 className="text-lg sm:text-xl font-bold mb-4">📋 Chapitres</h3>
          <div className="space-y-2 max-h-[400px] overflow-y-auto">
            {currentChapters.map((chapter, idx) => (
              <div key={idx} className="flex flex-col sm:flex-row items-start sm:items-center p-3 rounded-lg bg-gray-50 gap-2 sm:gap-0">
                <div className="min-w-[60px] font-bold text-red-600 text-sm sm:text-base">{chapter.time}</div>
                <div className="flex-1 ml-0 sm:ml-4 text-sm sm:text-base">{chapter.title}</div>
                <div className="text-xs sm:text-sm text-gray-500">{chapter.duration}</div>
              </div>
            ))}
          </div>
        </div>

       
        <div className="bg-white rounded-xl shadow-md p-4 sm:p-6">
          <h3 className="text-lg sm:text-xl font-bold mb-4">📝 Points clés</h3>
          <div className="space-y-3">
            {currentVideoPoints.map((point, idx) => (
              <div key={idx} className="border-b border-gray-100 pb-3 last:border-0">
                <div className="font-semibold text-gray-800 text-sm sm:text-base">⏱️ {point.time} - {point.title}</div>
                <p className="text-gray-600 text-xs sm:text-sm mt-1">{point.description}</p>
              </div>
            ))}
          </div>
        </div>

       
        <div className="bg-white rounded-xl shadow-md p-4 sm:p-6">
          <h3 className="text-lg sm:text-xl font-bold mb-4">📝 Transcription</h3>
          <div className="bg-gray-50 rounded-lg p-4 max-h-[400px] overflow-y-auto">
            {currentTranscript.map((segment, idx) => (
              <div key={idx} className="p-3 border-b border-gray-200 last:border-0">
                <div className="flex flex-col sm:flex-row items-start gap-2 sm:gap-3">
                  <span className="min-w-[60px] font-medium text-red-600 text-sm">{segment.time}</span>
                  <p className="flex-1 text-gray-700 text-sm sm:text-base">{segment.text}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        
        <div className="bg-white rounded-xl shadow-md p-4 sm:p-6">
          <h3 className="text-lg sm:text-xl font-bold mb-4">📓 Notes personnelles</h3>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Prenez des notes pendant le visionnage..."
            className="w-full h-32 p-3 border rounded-lg resize-none focus:ring-2 focus:ring-red-500 text-sm"
          />
          <button
            onClick={saveNotes}
            className="mt-2 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition text-sm w-full sm:w-auto"
          >
            💾 Sauvegarder les notes
          </button>
        </div>

        
        {showRecommendations && (
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
                    onClick={() => navigateToRecommendedCourse(rec.cours_id)}
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

        
        {!examMode ? (
         
          <div className="bg-gradient-to-r from-purple-500 to-purple-700 rounded-xl p-4 sm:p-6 md:p-8 text-white">
            <div className="flex flex-wrap justify-between items-center gap-2 mb-4">
              <h3 className="text-xl sm:text-2xl font-bold">🎯 Quiz de compréhension</h3>
              {quizGenerationMode === 'personalized' && (
                <span className="text-xs bg-green-500 px-3 py-1 rounded-full">Personnalisé</span>
              )}
            </div>
            <p className="mb-6 text-sm sm:text-base">Testez vos connaissances sur {selectedCourse?.titre}</p>

            {mistakeQuestions.length > 0 && !quizSubmitted && (
              <div className="mb-4 p-2 bg-yellow-500/30 rounded-lg text-center">
                <span className="text-sm">📝 {mistakeQuestions.length} erreur(s) enregistrée(s) pour ce cours</span>
              </div>
            )}

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
                  {Object.keys(userAnswers).length !== questions.length && (
                    <p className="text-sm text-purple-200 mt-2 text-center">
                      ⚠️ Veuillez répondre à toutes les questions ({Object.keys(userAnswers).length}/{questions.length})
                    </p>
                  )}
                  {!isAuthenticated && (
                    <p className="text-sm text-yellow-200 mt-2 text-center">
                      ⚠️ Connectez-vous pour enregistrer vos résultats
                    </p>
                  )}
                </>
              ) : (
                <div className="bg-white/10 rounded-lg p-6 text-center">
                  <div className="text-5xl mb-4">🎉</div>
                  <h4 className="text-xl sm:text-2xl font-bold mb-2">Résultats du quiz</h4>
                  <p className="text-2xl sm:text-3xl font-bold mb-2">{quizScore.toFixed(1)}%</p>
                  <p className="mb-4 text-sm sm:text-base">
                    {quizScore >= 70 ? '✅ Félicitations !' : '⚠️ Revoyez la leçon et réessayez.'}
                  </p>
                  {quizResultId && (
                    <p className="text-sm mb-4">Résultat enregistré (ID: {quizResultId})</p>
                  )}
                  <div className="flex flex-wrap gap-2 justify-center">
                    <button
                      onClick={resetQuiz}
                      className="px-4 sm:px-6 py-2 bg-white text-purple-600 rounded-lg hover:bg-gray-100 text-sm sm:text-base"
                    >
                      🔄 Recommencer le quiz
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
                <p>📝 Aucune question disponible pour ce cours.</p>
                <button
                  onClick={generatePersonalizedQuiz}
                  disabled={generatingQuiz}
                  className="mt-4 px-6 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 text-sm sm:text-base"
                >
                  {generatingQuiz ? '⏳...' : '🎯 Générer quiz personnalisé'}
                </button>
              </div>
            )}
          </div>
        ) : (
         
          <div className="bg-gradient-to-r from-indigo-500 to-indigo-700 rounded-xl p-4 sm:p-6 md:p-8 text-white">
            <div className="flex flex-wrap justify-between items-center gap-2 mb-4">
              <h3 className="text-xl sm:text-2xl font-bold">📝 Examen Final</h3>
              <button
                onClick={cancelExam}
                className="px-3 py-1 bg-white/20 rounded-lg hover:bg-white/30 transition text-sm"
              >
                ✕ Retour au quiz
              </button>
            </div>
            <p className="mb-2 text-sm sm:text-base">Cours: {selectedCourse?.titre}</p>
            <p className="text-sm mb-6">Score minimum requis: 70%</p>

            {generatingExam ? (
  <div className="text-center py-12">
    <div className="text-4xl mb-4">⏳</div>
    <p>Génération de votre examen...</p>
  </div>
) : examSubmitted && examResult ? (
  <div className="space-y-6">
   
    <div className={`rounded-lg p-6 text-center ${
      examResult.passed 
        ? 'bg-green-500/30' 
        : 'bg-red-500/30'
    }`}>
      <div className="text-6xl mb-4">{examResult.passed ? '🎓' : '📚'}</div>
      <h4 className="text-xl sm:text-2xl font-bold mb-2">Résultat de l'examen</h4>
      <p className="text-4xl sm:text-5xl font-bold mb-2">{examResult.percentage.toFixed(1)}%</p>
      <p className="mb-4 text-sm sm:text-base">
        {examResult.passed 
          ? '✅ Félicitations ! Vous avez réussi l\'examen.' 
          : '⚠️ Vous n\'avez pas atteint le seuil de réussite (70%).'}
      </p>
      <p className="text-sm">Score: {examResult.score} / {examResult.total} points</p>
    </div>

   
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
      <div className="bg-white/10 rounded-lg p-3 text-center">
        <div className="text-2xl font-bold text-green-400">
          {examResult.answers.filter((a: any) => a.isCorrect).length}
        </div>
        <div className="text-xs text-white/70">✅ Réponses correctes</div>
      </div>
      <div className="bg-white/10 rounded-lg p-3 text-center">
        <div className="text-2xl font-bold text-red-400">
          {examResult.answers.filter((a: any) => !a.isCorrect).length}
        </div>
        <div className="text-xs text-white/70">❌ Réponses incorrectes</div>
      </div>
      <div className="bg-white/10 rounded-lg p-3 text-center">
        <div className="text-2xl font-bold text-purple-400">
          {examResult.answers.length}
        </div>
        <div className="text-xs text-white/70">📝 Total questions</div>
      </div>
    </div>

    
    {examResult.answers.filter((a: any) => !a.isCorrect).length > 0 && (
      <div className="bg-yellow-500/20 rounded-lg p-4">
        <h4 className="font-bold mb-3 text-sm sm:text-base">
          📊 Analyse des erreurs ({examResult.answers.filter((a: any) => !a.isCorrect).length})
        </h4>
        <div className="space-y-2 max-h-60 overflow-y-auto">
          {examResult.answers.filter((a: any) => !a.isCorrect).map((answer: any, idx: number) => (
            <div key={idx} className="bg-white/10 rounded p-2 text-xs sm:text-sm">
              <p className="font-semibold">❌ {answer.questionText}</p>
              <div className="grid grid-cols-2 gap-2 mt-1">
                <div>
                  <span className="text-red-300">Votre réponse:</span>
                  <p className="font-mono">{answer.selectedAnswer || 'Non répondue'}</p>
                </div>
                <div>
                  <span className="text-green-300">Bonne réponse:</span>
                  <p className="font-mono">{answer.correctAnswer}</p>
                </div>
              </div>
              {answer.explanation && (
                <p className="text-xs text-blue-200 mt-1">💡 {answer.explanation}</p>
              )}
            </div>
          ))}
        </div>
      </div>
    )}

    
    <div className="flex flex-col sm:flex-row gap-3">
      <button
        onClick={cancelExam}
        className="flex-1 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition text-sm sm:text-base"
      >
        🔄 Retour aux quiz
      </button>
      <button
        onClick={() => {
          setExamSubmitted(false);
          setExamResult(null);
          generateFinalExam();
        }}
        className="flex-1 px-4 py-2 bg-white text-indigo-600 rounded-lg font-semibold hover:bg-gray-100 transition text-sm sm:text-base"
      >
        🔁 Recommencer l'examen
      </button>
    </div>

   
    {examResult.passed && (
      <div className="mt-4 p-4 bg-gradient-to-r from-yellow-400/30 to-amber-400/30 rounded-xl border-2 border-yellow-400/50">
        <p className="text-center text-sm text-white/90 mb-3">
          🎉 Félicitations ! Vous avez réussi l'examen. Vous pouvez maintenant générer votre certificat de formation complète.
        </p>
        <button
          onClick={() => generateCertificate(examResult, selectedCourse?.titre || 'Cours')}
          className="w-full px-6 py-4 bg-gradient-to-r from-yellow-400 via-yellow-500 to-yellow-600 text-white rounded-lg font-bold hover:from-yellow-500 hover:via-yellow-600 hover:to-yellow-700 transition-all duration-300 shadow-lg hover:shadow-xl flex items-center justify-center gap-3 text-lg"
        >
          <span className="text-3xl animate-bounce">🎓</span>
          Générer mon certificat global
          <span className="text-sm opacity-80">📄</span>
        </button>
        <p className="text-xs text-white/60 text-center mt-2">
          Ce certificat atteste de la réussite de l'ensemble de la formation
        </p>
      </div>
    )}
  </div>
) : (
  
  <>
    <p className="text-sm mb-4">L'examen contient {examQuestions.length} questions.</p>
    <div className="max-h-[500px] overflow-y-auto space-y-4">
      {examQuestions.map((q, idx) => (
        <div key={q.id} className="bg-white/10 rounded-lg p-4">
          <p className="font-semibold mb-3 text-sm sm:text-base">
            Question {idx + 1} ({q.points} points - {q.difficulte})
          </p>
          <p className="mb-3 text-sm sm:text-base">{q.question}</p>
          <div className="space-y-2">
            {Object.entries(q.options).map(([key, value]) => (
              <label key={key} className="flex items-start gap-3 cursor-pointer text-sm sm:text-base">
                <input
                  type="radio"
                  name={`exam_question_${q.id}`}
                  value={key}
                  checked={examAnswers[q.id] === key}
                  onChange={() => setExamAnswers(prev => ({ ...prev, [q.id]: key }))}
                  className="w-4 h-4 mt-1 flex-shrink-0"
                />
                <span className="break-words">{key}: {value}</span>
              </label>
            ))}
          </div>
        </div>
      ))}
    </div>
    <button
      onClick={submitExam}
      disabled={Object.keys(examAnswers).length !== examQuestions.length}
      className="w-full mt-6 px-6 py-3 bg-white text-indigo-600 rounded-lg font-semibold hover:bg-gray-100 transition disabled:opacity-50 text-sm sm:text-base"
    >
      📤 Soumettre l'examen
    </button>
    {Object.keys(examAnswers).length !== examQuestions.length && (
      <p className="text-xs sm:text-sm text-yellow-200 mt-2 text-center">
        ⚠️ {Object.keys(examAnswers).length}/{examQuestions.length} questions répondues
      </p>
    )}
  </>
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
    onClick={() => {
      if (selectedCourse) {
        navigate(`/learning/text/${selectedCourse.id}`);
      } else {
        navigate('/learning/text');
      }
    }}
    className="px-3 sm:px-4 py-2 bg-gray-100 rounded-lg hover:bg-gray-200 transition text-xs sm:text-sm"
  >
    📖 Texte
  </button>
  <button
    onClick={() => navigate('/')}
    className="px-3 sm:px-4 py-2 bg-gray-100 rounded-lg hover:bg-gray-200 transition text-xs sm:text-sm"
  >
    🏠 Accueil
  </button>
</div>
      </div>
    </div>
  </div>
);
};

export default VideoLearningPage;
