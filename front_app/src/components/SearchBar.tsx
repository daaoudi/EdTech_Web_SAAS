/* eslint-disable @typescript-eslint/no-explicit-any */
import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { voiceSearchService } from '../services/voiceSearchService';
import type { VoiceSearchResult } from '../services/voiceSearchService';
import api from '../services/api';

interface SearchBarProps {
  onSearch?: (results: VoiceSearchResult[]) => void;
  placeholder?: string;
}

interface VoiceSearchHistory {
  id: number;
  query: string;
  confidence: number;
  results_count: number;
  response_time_ms: number;
  success: boolean;
  date: string;
}

const SearchBar = ({ onSearch, placeholder = "Rechercher un cours..." }: SearchBarProps) => {
  const [query, setQuery] = useState<string>('');
  const [isRecording, setIsRecording] = useState<boolean>(false);
  const [isSearching, setIsSearching] = useState<boolean>(false);
  const [results, setResults] = useState<VoiceSearchResult[]>([]);
  const [showResults, setShowResults] = useState<boolean>(false);
  const [recordingTime, setRecordingTime] = useState<number>(0);
  const [isSpeechSupported, setIsSpeechSupported] = useState<boolean>(true);
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [showHistory, setShowHistory] = useState<boolean>(false);
  const [history, setHistory] = useState<VoiceSearchHistory[]>([]);
  const [loadingHistory, setLoadingHistory] = useState<boolean>(false);
  const searchRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();

  useEffect(() => {
    setIsSpeechSupported(voiceSearchService.isSupported());
    loadHistory();
  }, []);

  useEffect(() => {
    let interval: ReturnType<typeof setInterval>;
    if (isRecording) {
      interval = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
    } else {
      setRecordingTime(0);
    }
    return () => clearInterval(interval);
  }, [isRecording]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setShowResults(false);
        setShowHistory(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const loadHistory = async () => {
    try {
      setLoadingHistory(true);
      const response = await api.get('/voice/history', { params: { limit: 10 } });
      setHistory(response.data);
    } catch (error) {
      console.error('Erreur chargement historique:', error);
    } finally {
      setLoadingHistory(false);
    }
  };

  const handleSearch = async (searchQuery: string): Promise<void> => {
    if (!searchQuery.trim()) {
      setResults([]);
      setShowResults(false);
      onSearch?.([]);
      return;
    }

    setIsSearching(true);
    setShowHistory(false);
    try {
      const response = await fetch(`http://127.0.0.1:8001/courses/search?q=${encodeURIComponent(searchQuery)}&limit=20`);
      const searchResults = await response.json();
      setResults(searchResults);
      setShowResults(true);
      onSearch?.(searchResults);
    } catch (error) {
      console.error('Erreur de recherche:', error);
    } finally {
      setIsSearching(false);
    }
  };

  const handleStartRecording = async (): Promise<void> => {
    if (!voiceSearchService.isSupported()) {
      alert('La reconnaissance vocale n\'est pas supportée. Utilisez Chrome ou Edge.');
      return;
    }
    try {
      await voiceSearchService.startRecording();
      setIsRecording(true);
      setIsProcessing(false);
      setShowHistory(false);
    } catch (error) {
      console.error('Erreur démarrage:', error);
      alert('Impossible d\'accéder au microphone.');
    }
  };

  const handleStopRecording = async (): Promise<void> => {
    if (!isRecording) return;
    
    setIsProcessing(true);
    try {
      console.log('🎤 Arrêt de l\'enregistrement...');
      const result = await voiceSearchService.stopRecordingAndSearch();
      
      console.log('🎤 Résultat reçu:', result);
      
      if (result && result.transcript) {
        setQuery(result.transcript);
        
        if (result.results && result.results.length > 0) {
          setResults(result.results);
          setShowResults(true);
          if (onSearch) {
            onSearch(result.results);
          }
        } else {
          await handleSearch(result.transcript);
        }
        
        console.log(`🎤 Transcription: "${result.transcript}" (confiance: ${Math.round(result.confidence * 100)}%)`);
        
        
        await loadHistory();
      } else {
        console.warn('Aucune transcription reçue');
        alert('Je n\'ai pas compris. Veuillez réessayer.');
      }
      
    } catch (error: any) {
      console.error('❌ Erreur détaillée:', error);
      console.error('❌ Message:', error.message);
      console.error('❌ Response:', error.response?.data);
      
      let errorMessage = 'Erreur lors de la reconnaissance vocale. ';
      if (error.response?.data?.detail) {
        errorMessage += error.response.data.detail;
      } else if (error.message) {
        errorMessage += error.message;
      } else {
        errorMessage += 'Veuillez réessayer.';
      }
      
      alert(errorMessage);
    } finally {
      setIsRecording(false);
      setIsProcessing(false);
    }
  };

  const handleCancelRecording = (): void => {
    voiceSearchService.cancelRecording();
    setIsRecording(false);
    setIsProcessing(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>): void => {
    if (e.key === 'Enter') handleSearch(query);
  };

  const handleResultClick = (courseId: number): void => {
    setShowResults(false);
    setShowHistory(false);
    navigate(`/course/${courseId}`);
  };

  const handleHistoryClick = (historyQuery: string): void => {
    setQuery(historyQuery);
    handleSearch(historyQuery);
    setShowHistory(false);
  };

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'À l\'instant';
    if (diffMins < 60) return `Il y a ${diffMins} min`;
    if (diffHours < 24) return `Il y a ${diffHours} h`;
    return `Il y a ${diffDays} j`;
  };

  const getDifficultyColor = (difficulte: string): string => {
    const colors: Record<string, string> = {
      débutant: 'bg-green-100 text-green-700',
      intermediaire: 'bg-yellow-100 text-yellow-700',
      avancé: 'bg-red-100 text-red-700'
    };
    return colors[difficulte] || 'bg-gray-100 text-gray-700';
  };

  return (
    <div ref={searchRef} className="relative w-full max-w-2xl">
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>

        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => {
            if (!query && history.length > 0) {
              setShowHistory(true);
            }
          }}
          placeholder={placeholder}
          className="w-full pl-10 pr-24 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          disabled={isProcessing}
        />

        <div className="absolute inset-y-0 right-0 flex items-center gap-1 pr-2">
          {isRecording && (
            <div className="flex items-center gap-2 mr-2">
              <div className="flex items-center gap-1">
                <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse" />
                <span className="text-xs text-red-500 font-medium">{formatTime(recordingTime)}</span>
              </div>
              <button onClick={handleCancelRecording} className="text-gray-400 hover:text-gray-600 transition-colors" title="Annuler">
                <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          )}

          {isProcessing && (
            <div className="mr-2">
              <div className="w-5 h-5 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
            </div>
          )}

          {!isSpeechSupported ? (
            <div className="p-2 text-gray-400" title="Non supporté">
              <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
              </svg>
            </div>
          ) : (
            <button
              onClick={isRecording ? handleStopRecording : handleStartRecording}
              className={`p-2 rounded-full transition-colors ${isRecording ? 'bg-red-500 text-white animate-pulse' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}
              title={isRecording ? "Arrêter" : "Recherche vocale"}
              disabled={isProcessing}
            >
              <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
              </svg>
            </button>
          )}
        </div>
      </div>

      
      {showHistory && !isSearching && history.length > 0 && (
        <div className="absolute top-full left-0 right-0 mt-2 bg-white rounded-xl shadow-lg border border-gray-200 z-50 max-h-80 overflow-y-auto">
          <div className="p-3 border-b border-gray-100 bg-gray-50 sticky top-0 flex justify-between items-center">
            <p className="text-sm font-medium text-gray-700">📜 Historique des recherches vocales</p>
            <button 
              onClick={() => setShowHistory(false)}
              className="text-xs text-gray-400 hover:text-gray-600"
            >
              ✖ Fermer
            </button>
          </div>
          {loadingHistory ? (
            <div className="p-4 text-center text-gray-500">
              <div className="inline-block animate-spin rounded-full h-5 w-5 border-b-2 border-primary-500" />
              <p className="mt-1 text-sm">Chargement...</p>
            </div>
          ) : (
            history.map((item) => (
              <div
                key={item.id}
                onClick={() => handleHistoryClick(item.query)}
                className="p-3 hover:bg-gray-50 cursor-pointer transition-colors border-b border-gray-100 last:border-0"
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="text-lg">🎤</span>
                      <p className="text-sm font-medium text-gray-800">{item.query}</p>
                    </div>
                    <div className="flex items-center gap-3 mt-1 text-xs text-gray-500">
                      <span className="flex items-center gap-1">
                        📊 Confiance: {Math.round(item.confidence * 100)}%
                      </span>
                      <span className="flex items-center gap-1">
                        📚 {item.results_count} résultat(s)
                      </span>
                      <span className="flex items-center gap-1">
                        🕐 {formatDate(item.date)}
                      </span>
                    </div>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleHistoryClick(item.query);
                    }}
                    className="text-primary-500 text-sm hover:underline"
                  >
                    Rechercher
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      
      {showResults && (results.length > 0 || isSearching) && (
        <div className="absolute top-full left-0 right-0 mt-2 bg-white rounded-xl shadow-lg border border-gray-200 z-50 max-h-96 overflow-y-auto">
          {isSearching ? (
            <div className="p-4 text-center text-gray-500">
              <div className="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-primary-500" />
              <p className="mt-2">Recherche en cours...</p>
            </div>
          ) : results.length > 0 ? (
            <>
              <div className="p-3 border-b border-gray-100 bg-gray-50 sticky top-0 flex justify-between items-center">
                <p className="text-sm text-gray-500">{results.length} résultat(s)</p>
                <button 
                  onClick={() => setShowResults(false)}
                  className="text-xs text-gray-400 hover:text-gray-600"
                >
                  ✖ Fermer
                </button>
              </div>
              {results.map((result) => (
                <div key={result.id} onClick={() => handleResultClick(result.id)} className="p-4 hover:bg-gray-50 cursor-pointer transition-colors border-b border-gray-100 last:border-0">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <h4 className="font-semibold text-gray-800">{result.titre}</h4>
                      <p className="text-sm text-gray-600 mt-1 line-clamp-2">{result.description}</p>
                      <div className="flex flex-wrap gap-2 mt-2">
                        <span className={`text-xs px-2 py-1 rounded-full ${getDifficultyColor(result.difficulte)}`}>
                          {result.difficulte === 'débutant' && '🟢 Débutant'}
                          {result.difficulte === 'intermediaire' && '🟡 Intermédiaire'}
                          {result.difficulte === 'avancé' && '🔴 Avancé'}
                          {!result.difficulte && '📘 Non spécifié'}
                        </span>
                        {result.tags && result.tags.slice(0, 3).map((tag, idx) => (
                          <span key={idx} className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full">{tag}</span>
                        ))}
                      </div>
                    </div>
                    {result.score > 0 && (
                      <div className="ml-4 text-right">
                        <div className="text-sm font-semibold text-primary-600">{Math.round(result.score)}% match</div>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </>
          ) : query && (
            <div className="p-4 text-center text-gray-500">
              <p>Aucun résultat pour "{query}"</p>
              <p className="text-sm mt-1">Essayez d'autres mots-clés</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default SearchBar;