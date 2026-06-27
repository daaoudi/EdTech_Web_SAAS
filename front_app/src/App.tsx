import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import HomePage from './pages/HomePage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import CoursesPage from './pages/CoursesPage'
import CourseDetailPage from './pages/CourseDetailPage'
import TextLearningPage from './pages/TextLearningPage'
import AudioLearningPage from './pages/AudioLearningPage'
import VideoLearningPage from './pages/VideoLearningPage'
import ProgressPage from './pages/ProgressPage'
import QuizPage from './pages/QuizPage'
import ProfilePage from './pages/ProfilePage'
import RecommendationPage from './pages/RecommendationPage'
import PrivateRoute from './components/PrivateRoute'
import LevelTestPage from './pages/LevelTestPage'
import RiskMonitorPage from './pages/RiskMonitorPage';
import ProtectedRoute from './components/ProtectedRoute';
import AdminPage from './pages/AdminPage';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<HomePage />} />
        <Route path="login" element={<LoginPage />} />
        <Route path="register" element={<RegisterPage />} />
        
        <Route path="courses" element={
          <PrivateRoute>
            <CoursesPage />
          </PrivateRoute>
        } />
        
        <Route path="course/:id" element={
          <PrivateRoute>
            <CourseDetailPage />
          </PrivateRoute>
        } />
        
        <Route path="learning/text" element={
          <PrivateRoute>
            <TextLearningPage />
          </PrivateRoute>
        } />
        
        <Route path="learning/audio" element={
          <PrivateRoute>
            <AudioLearningPage />
          </PrivateRoute>
        } />
        
        <Route path="learning/video" element={
          <PrivateRoute>
            <VideoLearningPage />
          </PrivateRoute>
        } />
        
        <Route path="progress" element={
          <PrivateRoute>
            <ProgressPage />
          </PrivateRoute>
        } />
        
        <Route path="quiz" element={
          <PrivateRoute>
            <QuizPage />
          </PrivateRoute>
        } />
        
        <Route path="profile" element={
          <PrivateRoute>
            <ProfilePage />
          </PrivateRoute>
        } />
        
        <Route path="recommendation" element={
          <PrivateRoute>
            <RecommendationPage />
          </PrivateRoute>
        } />
        
        <Route path="level-test" element={
          <PrivateRoute>
            <LevelTestPage />
          </PrivateRoute>
        } />
        
       
        <Route 
          path="admin/risk-monitor" 
          element={
            <ProtectedRoute requiredRole="admin">
              <RiskMonitorPage />
            </ProtectedRoute>
          } 
        />
        
        <Route 
          path="admin" 
          element={
            <ProtectedRoute requiredRole="admin">
              <AdminPage />
            </ProtectedRoute>
          } 
        />
      </Route>
    </Routes>
  )
}

export default App