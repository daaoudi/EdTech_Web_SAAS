/* eslint-disable @typescript-eslint/no-explicit-any */

import api from './api';

export interface VoiceSearchResult {
  id: number;
  titre: string;
  description: string;
  difficulte: string;
  tags: string[];
  duree: number;
  score: number;
}

export interface VoiceSearchResponse {
  transcript: string;
  confidence: number;
  intent: {
    original_query: string;
    processed_query: string;
    topics: string[];
    difficulty: string | null;
    actions: string[];
    keywords: string[];
    course_ids: number[];
    confidence: number;
  };
  results: VoiceSearchResult[];
  suggestions: string[];
}

class VoiceSearchService {
  private mediaRecorder: MediaRecorder | null = null;
  private audioChunks: Blob[] = [];
  private isRecording: boolean = false;

  async startRecording(): Promise<void> {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      this.mediaRecorder = new MediaRecorder(stream);
      this.audioChunks = [];

      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          this.audioChunks.push(event.data);
        }
      };

      this.mediaRecorder.start(1000);
      this.isRecording = true;
      console.log('🎤 Enregistrement démarré');
    } catch (error) {
      console.error('Erreur microphone:', error);
      throw new Error('Impossible d\'accéder au microphone');
    }
  }

  async stopRecordingAndSearch(): Promise<VoiceSearchResponse> {
    return new Promise((resolve, reject) => {
      if (!this.mediaRecorder) {
        reject(new Error('Aucun enregistrement en cours'));
        return;
      }

      this.mediaRecorder.onstop = async () => {
        console.log('🎤 Enregistrement arrêté, traitement...');
        
        const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
        this.isRecording = false;

        
        if (this.mediaRecorder?.stream) {
          this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
        }

        try {
          const formData = new FormData();
          formData.append('audio', audioBlob, 'recording.webm');

          console.log('📤 Envoi au serveur...');
          const response = await api.post<VoiceSearchResponse>('/voice/search', formData, {
            headers: { 
              'Content-Type': 'multipart/form-data'
            },
            timeout: 60000 
          });

          console.log('✅ Réponse reçue:', response.data);
          resolve(response.data);
        } catch (error: any) {
          console.error('❌ Erreur détaillée:', error);
          console.error('❌ Response:', error.response?.data);
          reject(error);
        }
      };

      this.mediaRecorder.stop();
    });
  }

  cancelRecording(): void {
    if (this.mediaRecorder && this.isRecording) {
      this.mediaRecorder.stop();
      this.audioChunks = [];
      this.isRecording = false;
    }
  }

  isSupported(): boolean {
    return !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia);
  }
}

export const voiceSearchService = new VoiceSearchService();