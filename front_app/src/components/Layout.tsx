
import { useState } from 'react';
import { Outlet } from 'react-router-dom';
import Header from './Header';
import Sidebar from './Sidebar';
import { useAuth } from '../contexts/AuthContext';
import { LearningProvider, LearningContextType } from '../contexts/LearningContext';

const Layout = () => {
  const { isAuthenticated, loading } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  
  const [learningContextValue, setLearningContextValue] = useState<LearningContextType>({
    generatePersonalizedQuiz: () => {},
    showTutorRecommendations: () => {},
    showMistakeStats: () => {},
    generateBertQuiz: () => {},
    generateExam: () => {},
    cancelExam: () => {},
    isExamMode: false,
    hasMistakes: false,
    isGeneratingQuiz: false,
    isGeneratingExam: false,
    selectedCourseId: undefined
  });

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="text-4xl mb-4">🎓</div>
          <div className="text-xl text-gray-600">Chargement de votre espace...</div>
        </div>
      </div>
    );
  }

  return (
    <LearningProvider value={learningContextValue}>
      <div className="min-h-screen bg-gray-50 flex flex-col">
        <Header />
        <div className="flex flex-1">
          {isAuthenticated && (
            <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />
          )}
          <main className="flex-1 p-4 sm:p-6 lg:p-8 min-w-0">
            <Outlet context={{ setLearningContextValue }} />
          </main>
        </div>
        {isAuthenticated && !sidebarOpen && (
          <button
            onClick={() => setSidebarOpen(true)}
            className="lg:hidden fixed bottom-6 right-6 z-30 w-14 h-14 bg-primary-500 text-white rounded-full shadow-xl flex items-center justify-center hover:bg-primary-600 transition-all hover:scale-110 active:scale-95"
            aria-label="Ouvrir le tableau de bord"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        )}
      </div>
    </LearningProvider>
  );
};

export default Layout;