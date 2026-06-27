import { useState } from 'react';

const QuizPage = () => {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState<number[]>([]);
  const [showResults, setShowResults] = useState(false);

  const questions = [
    {
      question: "Que signifie l'acronyme HTML ?",
      options: [
        "Hyper Text Markup Language",
        "High Tech Modern Language",
        "Hyper Transfer Markup Language",
        "Home Tool Markup Language"
      ],
      correct: 0
    },
    {
      question: "Quelle balise est utilisée pour créer un lien hypertexte ?",
      options: ["<link>", "<a>", "<href>", "<url>"],
      correct: 1
    },
    {
      question: "Quelle balise est utilisée pour insérer une image ?",
      options: ["<pic>", "<image>", "<img>", "<src>"],
      correct: 2
    },
    {
      question: "Quelle balise définit le titre d'une page HTML ?",
      options: ["<head>", "<title>", "<heading>", "<header>"],
      correct: 1
    },
    {
      question: "Quel attribut spécifie l'URL d'un lien ?",
      options: ["src", "link", "href", "url"],
      correct: 2
    }
  ];

  const handleAnswer = (answerIndex: number) => {
    const newAnswers = [...answers];
    newAnswers[currentQuestion] = answerIndex;
    setAnswers(newAnswers);
    
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    } else {
      setShowResults(true);
    }
  };

  const calculateScore = () => {
    let correct = 0;
    answers.forEach((answer, idx) => {
      if (answer === questions[idx].correct) correct++;
    });
    return (correct / questions.length) * 100;
  };

  const resetQuiz = () => {
    setCurrentQuestion(0);
    setAnswers([]);
    setShowResults(false);
  };

  if (showResults) {
    const score = calculateScore();
    return (
      <div className="max-w-2xl mx-auto space-y-8">
        <div className="bg-white rounded-xl shadow-lg p-8 text-center">
          <h1 className="text-3xl font-bold text-primary-800 mb-6">🎯 Résultats du Quiz</h1>
          
          <div className="text-6xl font-bold mb-4 text-primary-600">{score.toFixed(0)}%</div>
          
          <div className="w-full bg-gray-200 h-4 rounded-full mb-6">
            <div 
              className="bg-primary-500 h-4 rounded-full transition-all"
              style={{ width: `${score}%` }}
            />
          </div>
          
          <p className="text-gray-600 mb-6">
            Vous avez répondu correctement à {answers.filter((a, i) => a === questions[i].correct).length} 
            questions sur {questions.length}
          </p>
          
          {score >= 80 && (
            <div className="bg-green-100 border-l-4 border-green-500 p-4 rounded mb-6">
              <p className="text-green-700">🎉 Excellent travail ! Continuez comme ça !</p>
            </div>
          )}
          
          {score >= 50 && score < 80 && (
            <div className="bg-yellow-100 border-l-4 border-yellow-500 p-4 rounded mb-6">
              <p className="text-yellow-700">📚 Bon travail ! Revoyez les cours pour améliorer votre score.</p>
            </div>
          )}
          
          {score < 50 && (
            <div className="bg-red-100 border-l-4 border-red-500 p-4 rounded mb-6">
              <p className="text-red-700">💪 Continuez vos efforts ! Revoir les cours vous aidera à progresser.</p>
            </div>
          )}
          
          <button
            onClick={resetQuiz}
            className="px-6 py-3 bg-primary-500 text-white rounded-lg hover:bg-primary-600"
          >
            🔄 Recommencer le quiz
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-primary-800">🎯 Quiz HTML</h1>
        <div className="text-gray-600">
          Question {currentQuestion + 1} sur {questions.length}
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-lg p-8">
        <h2 className="text-2xl font-bold mb-8 text-gray-800">
          {questions[currentQuestion].question}
        </h2>
        
        <div className="space-y-4">
          {questions[currentQuestion].options.map((option, idx) => (
            <button
              key={idx}
              onClick={() => handleAnswer(idx)}
              className="w-full text-left p-4 border rounded-lg hover:bg-blue-50 hover:border-blue-500 transition group"
            >
              <div className="flex items-center">
                <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center mr-4 group-hover:bg-blue-500 group-hover:text-white">
                  {String.fromCharCode(65 + idx)}
                </div>
                <span className="text-gray-700">{option}</span>
              </div>
            </button>
          ))}
        </div>
      </div>

      <div className="bg-gray-100 rounded-lg p-4">
        <div className="flex justify-between text-sm text-gray-600">
          <span>Progression du quiz</span>
          <span>{((currentQuestion + 1) / questions.length * 100).toFixed(0)}%</span>
        </div>
        <div className="w-full bg-gray-300 h-2 rounded-full mt-2">
          <div 
            className="bg-primary-500 h-2 rounded-full transition-all"
            style={{ width: `${((currentQuestion + 1) / questions.length * 100)}%` }}
          />
        </div>
      </div>
    </div>
  );
};

export default QuizPage;