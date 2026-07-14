
/* eslint-disable react-refresh/only-export-components */
import { createContext, useContext, ReactNode } from 'react';

export type LearningContextType = {
  generatePersonalizedQuiz: () => void;
  showTutorRecommendations: () => void;
  showMistakeStats: () => void;
  generateBertQuiz: () => void;
  generateExam: () => void;
  cancelExam: () => void;
  isExamMode: boolean;
  hasMistakes: boolean;
  isGeneratingQuiz: boolean;
  isGeneratingExam: boolean;
  selectedCourseId?: number;
};


const defaultContextValue: LearningContextType = {
  generatePersonalizedQuiz: () => console.warn('generatePersonalizedQuiz not implemented'),
  showTutorRecommendations: () => console.warn('showTutorRecommendations not implemented'),
  showMistakeStats: () => console.warn('showMistakeStats not implemented'),
  generateBertQuiz: () => console.warn('generateBertQuiz not implemented'),
  generateExam: () => console.warn('generateExam not implemented'),
  cancelExam: () => console.warn('cancelExam not implemented'),
  isExamMode: false,
  hasMistakes: false,
  isGeneratingQuiz: false,
  isGeneratingExam: false,
  selectedCourseId: undefined
};

const LearningContext = createContext<LearningContextType>(defaultContextValue);

export const LearningProvider = ({ children, value }: { 
  children: ReactNode; 
  value: LearningContextType 
}) => {
  return (
    <LearningContext.Provider value={value}>
      {children}
    </LearningContext.Provider>
  );
};

export const useLearningContext = (): LearningContextType => {
  return useContext(LearningContext);
};

export default LearningContext;