/* eslint-disable @typescript-eslint/no-explicit-any */
/* eslint-disable react-hooks/exhaustive-deps */
import { useState, useEffect, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';
import { useNavigate } from 'react-router-dom';

interface Question {
  id: number;
  question: string;
  options: Record<string, string>;
  reponse_correcte: string;
  points: number;
  category: 'html' | 'css' | 'javascript';
  difficulte: 'debutant' | 'intermediaire' | 'avance';
  explication?: string;
}

interface CategoryScore {
  html: { score: number; maxScore: number; level: string };
  css: { score: number; maxScore: number; level: string };
  javascript: { score: number; maxScore: number; level: string };
}

const testQuestions: Question[] = [
  {
    id: 1,
    question: "Quelle balise HTML est utilisée pour créer un paragraphe ?",
    options: { A: "<h1>", B: "<p>", C: "<div>", D: "<span>" },
    reponse_correcte: "B",
    points: 10,
    category: "html",
    difficulte: "debutant"
  },
  {
    id: 2,
    question: "Quelle balise HTML est utilisée pour créer un lien hypertexte ?",
    options: { A: "<link>", B: "<a>", C: "<href>", D: "<url>" },
    reponse_correcte: "B",
    points: 10,
    category: "html",
    difficulte: "debutant"
  },
  {
    id: 3,
    question: "Quelle balise HTML5 est utilisée pour le contenu principal unique d'une page ?",
    options: { A: "<header>", B: "<main>", C: "<section>", D: "<article>" },
    reponse_correcte: "B",
    points: 10,
    category: "html",
    difficulte: "intermediaire"
  },
  {
    id: 4,
    question: "Quelle est la différence entre <article> et <section> ?",
    options: {
      A: "Aucune différence",
      B: "<article> contenu autonome, <section> groupes thématiques",
      C: "<section> plus récent",
      D: "<article> sans titre"
    },
    reponse_correcte: "B",
    points: 10,
    category: "html",
    difficulte: "intermediaire"
  },
  {
    id: 5,
    question: "Quelle propriété CSS change la couleur du texte ?",
    options: { A: "background-color", B: "color", C: "text-color", D: "font-color" },
    reponse_correcte: "B",
    points: 10,
    category: "css",
    difficulte: "debutant"
  },
  {
    id: 6,
    question: "Quelle propriété CSS permet d'activer Flexbox ?",
    options: { A: "display: flex", B: "display: block", C: "display: grid", D: "flex: true" },
    reponse_correcte: "A",
    points: 10,
    category: "css",
    difficulte: "debutant"
  },
  {
    id: 7,
    question: "Quelle est la différence entre Flexbox et CSS Grid ?",
    options: {
      A: "Flexbox est 1D, Grid est 2D",
      B: "Grid est plus récent",
      C: "Flexbox mobile uniquement",
      D: "Grid colonnes uniquement"
    },
    reponse_correcte: "A",
    points: 10,
    category: "css",
    difficulte: "intermediaire"
  },
  {
    id: 8,
    question: "Que signifie 'fr' dans CSS Grid ?",
    options: { A: "Fraction", B: "Frame", C: "Flexible Ratio", D: "Free space" },
    reponse_correcte: "A",
    points: 10,
    category: "css",
    difficulte: "intermediaire"
  },
  {
    id: 9,
    question: "Quelle propriété CSS permet de créer une animation ?",
    options: { A: "transition", B: "animation", C: "transform", D: "keyframes" },
    reponse_correcte: "B",
    points: 10,
    category: "css",
    difficulte: "avance"
  },
  {
    id: 10,
    question: "Comment déclarer a variable en JavaScript ?",
    options: { A: "var x = 5;", B: "let x = 5;", C: "const x = 5;", D: "Toutes ces réponses" },
    reponse_correcte: "D",
    points: 10,
    category: "javascript",
    difficulte: "debutant"
  },
  {
    id: 11,
    question: "Quelle fonction affiche un message dans une boîte de dialogue ?",
    options: { A: "console.log()", B: "alert()", C: "prompt()", D: "confirm()" },
    reponse_correcte: "B",
    points: 10,
    category: "javascript",
    difficulte: "debutant"
  },
  {
    id: 12,
    question: "Quelle méthode sélectionne un élément par son ID ?",
    options: {
      A: "getElementByClass()",
      B: "getElementById()",
      C: "querySelectorAll()",
      D: "getElementsByTagName()"
    },
    reponse_correcte: "B",
    points: 10,
    category: "javascript",
    difficulte: "intermediaire"
  },
  {
    id: 13,
    question: "Que signifie DOM en JavaScript ?",
    options: {
      A: "Document Object Model",
      B: "Data Object Management",
      C: "Document Orientation Model",
      D: "Digital Object Model"
    },
    reponse_correcte: "A",
    points: 10,
    category: "javascript",
    difficulte: "intermediaire"
  }
];

const LevelTestPage = () => {
  const { isAuthenticated, user, refreshUser } = useAuth(); 
  const navigate = useNavigate();

  const [questions] = useState<Question[]>(testQuestions);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [userAnswers, setUserAnswers] = useState<Record<number, string>>({});
  const [testStarted, setTestStarted] = useState(false);
  const [testCompleted, setTestCompleted] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<{
    overallLevel: string;
    scores: CategoryScore;
    recommendations: string[];
  } | null>(null);
  const [timeRemaining, setTimeRemaining] = useState(1800);

  const submitRef = useRef<(() => Promise<void>) | null>(null);

  useEffect(() => {
    submitRef.current = async () => {
      if (submitting) return;
      setSubmitting(true);

      const categoryScores: CategoryScore = {
        html: { score: 0, maxScore: 0, level: 'débutant' },
        css: { score: 0, maxScore: 0, level: 'débutant' },
        javascript: { score: 0, maxScore: 0, level: 'débutant' }
      };

      let totalScore = 0;
      let totalMaxScore = 0;

      for (const q of questions) {
        const pts = q.points;
        totalMaxScore += pts;
        categoryScores[q.category].maxScore += pts;
        if (userAnswers[q.id] === q.reponse_correcte) {
          totalScore += pts;
          categoryScores[q.category].score += pts;
        }
      }

      const calc = (s: number, m: number): string => {
        if (m === 0) return 'débutant';
        const p = (s / m) * 100;
        if (p >= 80) return 'avancé';
        if (p >= 50) return 'intermédiaire';
        return 'débutant';
      };

      categoryScores.html.level = calc(categoryScores.html.score, categoryScores.html.maxScore);
      categoryScores.css.level = calc(categoryScores.css.score, categoryScores.css.maxScore);
      categoryScores.javascript.level = calc(categoryScores.javascript.score, categoryScores.javascript.maxScore);

      const pct = (totalScore / totalMaxScore) * 100;
      let overallLevel = 'débutant';
      if (pct >= 70) overallLevel = 'avancé';
      else if (pct >= 40) overallLevel = 'intermédiaire';

      const recs: string[] = [];
      if (categoryScores.html.level === 'débutant') recs.push('Revoyez les bases du HTML');
      else if (categoryScores.html.level === 'intermédiaire') recs.push('Approfondissez HTML (HTML5, accessibilité)');
      else recs.push('Excellent niveau HTML ! Passez aux frameworks');
      if (categoryScores.css.level === 'débutant') recs.push('Apprenez les bases du CSS');
      else if (categoryScores.css.level === 'intermédiaire') recs.push('Maîtrisez Flexbox, Grid et animations');
      else recs.push('Excellent CSS ! Explorez Sass ou Tailwind');
      if (categoryScores.javascript.level === 'débutant') recs.push('Commencez par les bases de JavaScript');
      else if (categoryScores.javascript.level === 'intermédiaire') recs.push('Approfondissez JS (DOM, Promises, async/await)');
      else recs.push('Excellent JS ! Lancez-vous dans React ou Vue');

      setResult({ overallLevel, scores: categoryScores, recommendations: recs });
      setTestCompleted(true);

      if (isAuthenticated && user) {
        try {
          
          await api.put('/users/me', { niveau_global: overallLevel });
          
          
          await refreshUser();
          
          console.log('✅ Niveau mis à jour et utilisateur rafraîchi');
        } catch (error: any) {
          console.error('Erreur mise à jour niveau:', error.response?.data || error.message);
        }
      }

      setSubmitting(false);
    };
  }, [questions, userAnswers, isAuthenticated, user, refreshUser, submitting]);

  useEffect(() => {
    if (!testStarted || testCompleted) return;

    const timer = setInterval(() => {
      setTimeRemaining(prev => {
        if (prev <= 1) {
          clearInterval(timer);
          submitRef.current?.();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [testStarted, testCompleted]);

  const handleSubmitTest = () => {
    submitRef.current?.();
  };

  const formatTime = (seconds: number) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}:${s.toString().padStart(2, '0')}`;
  };

  const handleStartTest = () => {
    setTestStarted(true);
    setUserAnswers({});
    setCurrentQuestionIndex(0);
    setTimeRemaining(1800);
    setResult(null);
    setTestCompleted(false);
    setSubmitting(false);
  };

  const handleAnswerSelect = (answer: string) => {
    setUserAnswers(prev => ({ ...prev, [questions[currentQuestionIndex].id]: answer }));
  };

  const handleNextQuestion = () => {
    if (currentQuestionIndex < questions.length - 1) setCurrentQuestionIndex(prev => prev + 1);
  };

  const handlePrevQuestion = () => {
    if (currentQuestionIndex > 0) setCurrentQuestionIndex(prev => prev - 1);
  };

  const getLevelBadge = (level: string) => {
    switch (level) {
      case 'débutant': return <span className="px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs font-semibold">🟢 Débutant</span>;
      case 'intermédiaire': return <span className="px-2 py-1 bg-yellow-100 text-yellow-700 rounded-full text-xs font-semibold">🟡 Intermédiaire</span>;
      case 'avancé': return <span className="px-2 py-1 bg-red-100 text-red-700 rounded-full text-xs font-semibold">🔴 Avancé</span>;
      default: return <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded-full text-xs font-semibold">Non défini</span>;
    }
  };

  
  if (!testStarted) {
    return (
      <div className="max-w-3xl mx-auto space-y-8 animate-fade-in">
        <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl p-8 text-white text-center">
          <h1 className="text-3xl font-bold mb-4">📋 Test de Niveau</h1>
          <p className="text-lg opacity-90">Évaluez vos connaissances en HTML, CSS et JavaScript</p>
        </div>
        <div className="bg-white rounded-xl shadow-lg p-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">📝 Instructions</h2>
          <ul className="space-y-3 text-gray-600">
            <li className="flex items-start gap-3"><span className="text-blue-500 font-bold">•</span><span>{questions.length} questions réparties en 3 catégories</span></li>
            <li className="flex items-start gap-3"><span className="text-blue-500 font-bold">•</span><span>Temps imparti : 30 minutes</span></li>
            <li className="flex items-start gap-3"><span className="text-blue-500 font-bold">•</span><span>Chaque question a une seule bonne réponse</span></li>
            <li className="flex items-start gap-3"><span className="text-blue-500 font-bold">•</span><span>Votre niveau sera enregistré dans votre profil</span></li>
          </ul>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-xl shadow-md p-6 text-center border-t-4 border-orange-500">
            <div className="text-4xl mb-3">📄</div>
            <h3 className="text-xl font-bold text-gray-800">HTML</h3>
            <p className="text-gray-500 text-sm mt-2">Structure et sémantique</p>
            <p className="text-gray-400 text-xs mt-2">{questions.filter(q => q.category === 'html').length} questions</p>
          </div>
          <div className="bg-white rounded-xl shadow-md p-6 text-center border-t-4 border-blue-500">
            <div className="text-4xl mb-3">🎨</div>
            <h3 className="text-xl font-bold text-gray-800">CSS</h3>
            <p className="text-gray-500 text-sm mt-2">Style et mise en page</p>
            <p className="text-gray-400 text-xs mt-2">{questions.filter(q => q.category === 'css').length} questions</p>
          </div>
          <div className="bg-white rounded-xl shadow-md p-6 text-center border-t-4 border-yellow-500">
            <div className="text-4xl mb-3">⚡</div>
            <h3 className="text-xl font-bold text-gray-800">JavaScript</h3>
            <p className="text-gray-500 text-sm mt-2">Interactivité et logique</p>
            <p className="text-gray-400 text-xs mt-2">{questions.filter(q => q.category === 'javascript').length} questions</p>
          </div>
        </div>
        <button onClick={handleStartTest} className="w-full py-4 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl font-semibold text-lg hover:opacity-90 transition">
          🚀 Commencer le test
        </button>
      </div>
    );
  }

  
  if (testCompleted && result) {
    return (
      <div className="max-w-3xl mx-auto space-y-8 animate-fade-in">
        <div className="bg-gradient-to-r from-green-500 to-teal-500 rounded-2xl p-8 text-white text-center">
          <div className="text-6xl mb-4">🎉</div>
          <h1 className="text-3xl font-bold mb-2">Test Terminé !</h1>
          <p className="text-lg opacity-90">Voici vos résultats détaillés</p>
        </div>
        <div className="bg-white rounded-xl shadow-lg p-8 text-center">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">📊 Niveau Global</h2>
          <div className="text-6xl font-bold mb-4">
            {result.overallLevel === 'débutant' && '🟢'}
            {result.overallLevel === 'intermédiaire' && '🟡'}
            {result.overallLevel === 'avancé' && '🔴'}
          </div>
          <div className="text-3xl font-bold capitalize mb-2">{result.overallLevel}</div>
          <p className="text-gray-600">
            {result.overallLevel === 'débutant' && 'Vous êtes au début de votre apprentissage. Continuez !'}
            {result.overallLevel === 'intermédiaire' && 'Vous avez de bonnes bases. Continuez à vous perfectionner !'}
            {result.overallLevel === 'avancé' && 'Excellent niveau ! Vous maîtrisez les fondamentaux.'}
          </p>
        </div>
        <div className="bg-white rounded-xl shadow-lg p-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">📈 Résultats par Catégorie</h2>
          <div className="space-y-6">
            {(['html', 'css', 'javascript'] as const).map((cat, idx) => {
              const s = result.scores[cat];
              const colors = ['bg-orange-500', 'bg-blue-500', 'bg-yellow-500'];
              const icons = ['📄', '🎨', '⚡'];
              const names = ['HTML', 'CSS', 'JavaScript'];
              return (
                <div key={cat} className={idx < 2 ? 'border-b pb-4' : ''}>
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-lg font-semibold">{icons[idx]} {names[idx]}</span>
                    {getLevelBadge(s.level)}
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div className={`${colors[idx]} h-2 rounded-full transition-all`} style={{ width: `${s.maxScore > 0 ? (s.score / s.maxScore) * 100 : 0}%` }} />
                  </div>
                  <p className="text-sm text-gray-500 mt-1">Score: {s.score}/{s.maxScore} points</p>
                </div>
              );
            })}
          </div>
        </div>
        <div className="bg-blue-50 rounded-xl shadow-md p-8 border-l-4 border-blue-500">
          <h2 className="text-xl font-bold text-blue-800 mb-4">💡 Recommandations</h2>
          <ul className="space-y-2">
            {result.recommendations.map((rec, i) => (
              <li key={i} className="flex items-start gap-2 text-blue-700"><span>•</span><span>{rec}</span></li>
            ))}
          </ul>
        </div>
        <div className="flex gap-4">
          <button onClick={() => navigate('/courses')} className="flex-1 px-6 py-3 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition">📚 Voir les cours</button>
          <button onClick={handleStartTest} className="flex-1 px-6 py-3 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition">🔄 Recommencer</button>
        </div>
      </div>
    );
  }

  
  const currentQuestion = questions[currentQuestionIndex];
  const answeredCount = Object.keys(userAnswers).length;
  const progress = (answeredCount / questions.length) * 100;

  return (
    <div className="max-w-3xl mx-auto space-y-6 animate-fade-in">
      <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl p-6 text-white">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold">📋 Test de Niveau</h1>
          <div className="text-right">
            <div className="text-sm opacity-90">Temps restant</div>
            <div className="text-2xl font-mono font-bold">{formatTime(timeRemaining)}</div>
          </div>
        </div>
        <div className="mt-4">
          <div className="flex justify-between text-sm mb-1">
            <span>Progression</span>
            <span>{answeredCount}/{questions.length}</span>
          </div>
          <div className="w-full bg-white/30 rounded-full h-2">
            <div className="bg-white h-2 rounded-full transition-all" style={{ width: `${progress}%` }} />
          </div>
        </div>
      </div>

      <div className="flex justify-between items-center text-sm text-gray-500">
        <span>Question {currentQuestionIndex + 1} sur {questions.length}</span>
        <span className="px-2 py-1 bg-gray-100 rounded-full text-xs">
          {currentQuestion.category === 'html' && '📄 HTML'}
          {currentQuestion.category === 'css' && '🎨 CSS'}
          {currentQuestion.category === 'javascript' && '⚡ JavaScript'}
        </span>
      </div>

      <div className="bg-white rounded-xl shadow-lg p-8">
        <h3 className="text-xl font-semibold text-gray-800 mb-6">{currentQuestion.question}</h3>
        <div className="space-y-3">
          {Object.entries(currentQuestion.options).map(([key, value]) => (
            <label
              key={key}
              className={`flex items-center p-4 border rounded-lg cursor-pointer transition ${
                userAnswers[currentQuestion.id] === key ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:bg-gray-50'
              }`}
            >
              <input
                type="radio"
                name={`q_${currentQuestion.id}`}
                value={key}
                checked={userAnswers[currentQuestion.id] === key}
                onChange={() => handleAnswerSelect(key)}
                className="w-4 h-4 text-blue-600 mr-3"
              />
              <span className="text-gray-700">{key}: {value}</span>
            </label>
          ))}
        </div>
      </div>

      <div className="flex justify-between gap-4">
        <button
          onClick={handlePrevQuestion}
          disabled={currentQuestionIndex === 0}
          className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg disabled:opacity-50 hover:bg-gray-300 transition"
        >
          ← Précédent
        </button>
        {currentQuestionIndex < questions.length - 1 ? (
          <button onClick={handleNextQuestion} className="px-6 py-3 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition">
            Suivant →
          </button>
        ) : (
          <button
            onClick={handleSubmitTest}
            disabled={submitting || answeredCount !== questions.length}
            className="px-6 py-3 bg-green-500 text-white rounded-lg hover:bg-green-600 transition disabled:opacity-50"
          >
            {submitting ? 'Soumission...' : '📤 Terminer le test'}
          </button>
        )}
      </div>

      {answeredCount !== questions.length && currentQuestionIndex === questions.length - 1 && (
        <p className="text-center text-sm text-orange-600">
          ⚠️ Veuillez répondre à toutes les questions ({questions.length - answeredCount} restantes)
        </p>
      )}
    </div>
  );
};

export default LevelTestPage;