import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os
import json
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
from typing import Dict, Any, Optional, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LearningRecommender:
    def __init__(self, model_path="models/learning_recommender.pkl", db_config=None):
        self.model_path = model_path
        self.scaler_path = model_path.replace('.pkl', '_scaler.pkl')
        self.encoder_path = model_path.replace('.pkl', '_encoder.pkl')
        self.model = None
        self.scaler = None
        self.label_encoder = None
        self.db_config = db_config or {
            'host': 'localhost',
            'database': 'plateforme_elearning',
            'user': 'postgres',
            'password': 'root',
            'port': 5432
        }
        self.load_or_create_model()
    
    def get_db_connection(self):
        
        try:
            conn = psycopg2.connect(
                host=self.db_config['host'],
                database=self.db_config['database'],
                user=self.db_config['user'],
                password=self.db_config['password'],
                port=self.db_config['port'],
                cursor_factory=RealDictCursor
            )
            return conn
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            return None
    
    def load_or_create_model(self):
        
        if os.path.exists(self.model_path):
            try:
                self.model = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
                self.label_encoder = joblib.load(self.encoder_path)
                logger.info("✅ Model loaded successfully")
            except Exception as e:
                logger.error(f"Error loading model: {e}")
                self.train_with_real_data()
        else:
            logger.info("No existing model found. Training with real data...")
            self.train_with_real_data()
    
    def _create_default_model(self):
        
       
        self.model = RandomForestClassifier(n_estimators=10, random_state=42)
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.label_encoder.fit(['text', 'audio', 'video'])
        logger.info("✅ Default model created")
    
    def fetch_user_learning_data(self):
        
        conn = self.get_db_connection()
        if not conn:
            return None
        
        try:
            cur = conn.cursor()
            
            
            query = """
            WITH user_scores AS (
                SELECT 
                    utilisateur_id,
                    mode,
                    AVG(score_quiz) as avg_score,
                    AVG(temps_passe) as avg_time,
                    COUNT(*) as sessions,
                    AVG(taux_completion) as avg_completion,
                    SUM(CASE WHEN est_reussi THEN 1 ELSE 0 END)::float / COUNT(*) as success_rate,
                    MAX(date_completion) as last_activity
                FROM resultats_apprentissage
                WHERE score_quiz IS NOT NULL
                GROUP BY utilisateur_id, mode
            ),
            user_preferences AS (
                SELECT 
                    utilisateur_id,
                    score_texte,
                    score_audio,
                    score_video,
                    confiance,
                    date_calcul
                FROM preferences_apprentissage
                ORDER BY date_calcul DESC
            )
            SELECT 
                us.utilisateur_id,
                us.mode,
                us.avg_score,
                us.avg_time,
                us.sessions,
                us.avg_completion,
                us.success_rate,
                us.last_activity,
                up.score_texte,
                up.score_audio,
                up.score_video,
                up.confiance,
                EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - up.date_calcul)) / 86400 as days_since_pref
            FROM user_scores us
            LEFT JOIN user_preferences up ON us.utilisateur_id = up.utilisateur_id
            WHERE us.sessions >= 1  -- Au moins 1 session pour avoir des données fiables
            ORDER BY us.utilisateur_id, us.mode
            """
            
            cur.execute(query)
            results = cur.fetchall()
            
            
            user_data = {}
            for row in results:
                user_id = row['utilisateur_id']
                if user_id not in user_data:
                    user_data[user_id] = {
                        'metrics': {
                            'text': {'avg_score': 0, 'avg_time': 0, 'sessions': 0, 'avg_completion': 0, 'success_rate': 0},
                            'audio': {'avg_score': 0, 'avg_time': 0, 'sessions': 0, 'avg_completion': 0, 'success_rate': 0},
                            'video': {'avg_score': 0, 'avg_time': 0, 'sessions': 0, 'avg_completion': 0, 'success_rate': 0}
                        },
                        'preferences': {
                            'score_texte': row['score_texte'] or 0,
                            'score_audio': row['score_audio'] or 0,
                            'score_video': row['score_video'] or 0,
                            'confiance': row['confiance'] or 0
                        },
                        'actual_mode': None
                    }
                
                
                user_data[user_id]['metrics'][row['mode']] = {
                    'avg_score': row['avg_score'] or 0,
                    'avg_time': row['avg_time'] or 0,
                    'sessions': row['sessions'] or 0,
                    'avg_completion': row['avg_completion'] or 0,
                    'success_rate': row['success_rate'] or 0
                }
            
            
            for user_id, data in user_data.items():
                scores = {
                    'text': data['metrics']['text']['avg_score'] * data['metrics']['text']['success_rate'],
                    'audio': data['metrics']['audio']['avg_score'] * data['metrics']['audio']['success_rate'],
                    'video': data['metrics']['video']['avg_score'] * data['metrics']['video']['success_rate']
                }
                
                
                sessions = {
                    'text': data['metrics']['text']['sessions'],
                    'audio': data['metrics']['audio']['sessions'],
                    'video': data['metrics']['video']['sessions']
                }
                
                
                weighted_scores = {}
                for mode in ['text', 'audio', 'video']:
                    score_weight = 0.7
                    session_weight = 0.3
                    max_sessions = max(sessions.values()) if max(sessions.values()) > 0 else 1
                    weighted_scores[mode] = (
                        score_weight * scores[mode] + 
                        session_weight * (sessions[mode] / max_sessions * 100)
                    )
                
                data['actual_mode'] = max(weighted_scores, key=weighted_scores.get)
            
            cur.close()
            conn.close()
            
            logger.info(f"✅ Fetched data for {len(user_data)} users")
            return list(user_data.values())
            
        except Exception as e:
            logger.error(f"Error fetching user data: {e}")
            return None
    
    def prepare_features(self, user_metrics, user_preferences=None):
        
        features = [
            user_metrics.get('text', {}).get('avg_score', 0),
            user_metrics.get('audio', {}).get('avg_score', 0),
            user_metrics.get('video', {}).get('avg_score', 0),
            user_metrics.get('text', {}).get('avg_time', 0),
            user_metrics.get('audio', {}).get('avg_time', 0),
            user_metrics.get('video', {}).get('avg_time', 0),
            user_metrics.get('text', {}).get('sessions', 0),
            user_metrics.get('audio', {}).get('sessions', 0),
            user_metrics.get('video', {}).get('sessions', 0),
            user_metrics.get('text', {}).get('avg_completion', 0),
            user_metrics.get('audio', {}).get('avg_completion', 0),
            user_metrics.get('video', {}).get('avg_completion', 0),
            user_metrics.get('text', {}).get('success_rate', 0),
            user_metrics.get('audio', {}).get('success_rate', 0),
            user_metrics.get('video', {}).get('success_rate', 0)
        ]
        
        
        if user_preferences:
            features.extend([
                user_preferences.get('score_texte', 0),
                user_preferences.get('score_audio', 0),
                user_preferences.get('score_video', 0),
                user_preferences.get('confiance', 0)
            ])
        else:
            features.extend([0, 0, 0, 0])
        
        return np.array(features).reshape(1, -1)
    
    def train_with_real_data(self):
        
        user_data = self.fetch_user_learning_data()
        
        if not user_data or len(user_data) < 3:
            logger.warning("Not enough real data. Using synthetic data for initial training.")
            self.train_initial_model()
            return
        
        
        X = []
        y = []
        
        for data in user_data:
            features = self.prepare_features(data['metrics'], data.get('preferences'))[0]
            X.append(features)
            y.append(data['actual_mode'])
        
        X = np.array(X)
        
        
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        
        self.label_encoder = LabelEncoder()
        y_encoded = self.label_encoder.fit_transform(y)
        
        
        if len(X) > 1:
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y_encoded, test_size=0.2, random_state=42
            )
        else:
            X_train, y_train = X_scaled, y_encoded
            X_test, y_test = X_scaled, y_encoded
        
        
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        self.model.fit(X_train, y_train)
        
        
        if len(X_test) > 0:
            y_pred = self.model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            logger.info(f"✅ Model trained with accuracy: {accuracy:.2f}")
        
        
        self.save_model()
    
    def train_initial_model(self):
        
        np.random.seed(42)
        n_samples = 1000  
        
        
        X = np.random.rand(n_samples, 19) * 100  
        
        
        y = []
        for features in X:
            text_score, audio_score, video_score = features[0], features[1], features[2]
            text_sessions, audio_sessions, video_sessions = features[6], features[7], features[8]
            text_success, audio_success, video_success = features[12], features[13], features[14]
            
            
            text_weighted = text_score * 0.6 + text_success * 100 * 0.3 + text_sessions * 0.1
            audio_weighted = audio_score * 0.6 + audio_success * 100 * 0.3 + audio_sessions * 0.1
            video_weighted = video_score * 0.6 + video_success * 100 * 0.3 + video_sessions * 0.1
            
            
            text_weighted += np.random.normal(0, 5)
            audio_weighted += np.random.normal(0, 5)
            video_weighted += np.random.normal(0, 5)
            
            
            scores = {
                'text': text_weighted,
                'audio': audio_weighted,
                'video': video_weighted
            }
            
            y.append(max(scores, key=scores.get))
        
        
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        
        self.label_encoder = LabelEncoder()
        y_encoded = self.label_encoder.fit_transform(y)
        
        
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        self.model.fit(X_scaled, y_encoded)
        
        logger.info("✅ Initial model trained with synthetic data")
        self.save_model()
    
    def save_model(self):
        
        try:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            joblib.dump(self.model, self.model_path)
            joblib.dump(self.scaler, self.scaler_path)
            joblib.dump(self.label_encoder, self.encoder_path)
            logger.info("✅ Model saved successfully")
        except Exception as e:
            logger.error(f"Error saving model: {e}")


    def _generate_details(self, metrics: Dict, recommended_mode: str) -> List[str]:
        
        details = []
        
        for mode, data in metrics.items():
            if data.get('sessions', 0) > 0:
                avg_score = data.get('avg_score', 0)
                symbol = "✅" if mode == recommended_mode else "📊"
                details.append(
                    f"{symbol} Mode {mode}: {data['sessions']} sessions, "
                    f"score moyen {avg_score:.0f}%"
                )
        
        if not any(m.get('sessions', 0) > 0 for m in metrics.values()):
            details.append("Aucune donnée d'apprentissage disponible")
            details.append("Basé sur les statistiques des nouveaux apprenants")
        
        return details
    
    def _get_strengths(self, mode: str) -> List[str]:
        
        strengths = {
            'text': [
                "Lecture à votre propre rythme",
                "Possibilité de prendre des notes détaillées",
                "Accès facile aux références"
            ],
            'audio': [
                "Apprentissage en multitâche",
                "Idéal pour les déplacements",
                "Réduction de la fatigue oculaire"
            ],
            'video': [
                "Exemples visuels concrets",
                "Démonstrations pas à pas",
                "Meilleure rétention visuelle"
            ]
        }
        return strengths.get(mode, ["Contenu adapté à vos besoins"])
    
    def _get_next_steps(self, mode: str) -> List[str]:
        
        steps = {
            'text': [
                "Commencez par lire l'introduction du cours",
                "Pratiquez avec les exercices associés",
                "Passez le quiz de validation"
            ],
            'audio': [
                "Écoutez la leçon audio d'introduction",
                "Prenez des notes audio si possible",
                "Testez vos connaissances avec le quiz"
            ],
            'video': [
                "Regardez la vidéo d'introduction",
                "Suivez les démonstrations pas à pas",
                "Validez votre compréhension avec le quiz"
            ]
        }
        return steps.get(mode, ["Commencez votre apprentissage"])


    def _build_recommendation(self, mode: str, confidence: float, 
                              scores: Dict[str, float], metrics: Dict) -> Dict:
        
        
        titles = {
            'text': '📖 Mode Texte - Apprentissage par lecture',
            'audio': '🎧 Mode Audio - Apprentissage par écoute',
            'video': '🎬 Mode Vidéo - Apprentissage visuel'
        }
        
        descriptions = {
            'text': 'Recommandé pour les apprenants qui préfèrent la lecture détaillée et la prise de notes.',
            'audio': 'Idéal pour les apprenants auditifs et les moments où vous ne pouvez pas regarder un écran.',
            'video': 'Parfait pour les apprenants visuels qui préfèrent voir les concepts en action.'
        }
        
        confidence_level = (
            'Élevée' if confidence > 0.7 else
            'Moyenne' if confidence > 0.4 else 'Faible'
        )
        
        confidence_colors = {
            'Élevée': '#10B981', 
            'Moyenne': '#F59E0B',  
            'Faible': '#6B7280'    
        }
        
        return {
            'recommended_mode': mode,
            'recommended_title': titles.get(mode, f"Mode {mode}"),
            'confidence': confidence,
            'confidence_text': confidence_level,
            'confidence_color': confidence_colors.get(confidence_level, '#6B7280'),
            'probabilities_dict': scores,
            'description': descriptions.get(mode, ""),
            'details': self._generate_details(metrics, mode),
            'strengths': self._get_strengths(mode),
            'next_steps': self._get_next_steps(mode),
            'metrics': metrics
        }
    
    def _build_recommendation_from_data(self, mode: str, confidence: float, 
                                         scores: Dict[str, float], metrics: Dict) -> Dict:
        
        
        
        mode_to_learner = {
            'text': 'lecture',
            'audio': 'auditif',
            'video': 'visuel'
        }
        
        learner_type = mode_to_learner.get(mode, 'mixte')
        
        
        messages = {
            'text': f"📖 Vous excellez dans le mode texte (score {metrics.get('text', {}).get('avg_score', 0):.1f}%) ! Continuez avec les cours écrits pour maximiser votre apprentissage.",
            'audio': f"🎧 Vous excellez dans le mode audio (score {metrics.get('audio', {}).get('avg_score', 0):.1f}%) ! Continuez avec les cours en audio pour maximiser votre apprentissage.",
            'video': f"🎬 Vous excellez dans le mode vidéo (score {metrics.get('video', {}).get('avg_score', 0):.1f}%) ! Continuez avec les cours en vidéo pour maximiser votre apprentissage."
        }
        
        titles = {
            'text': '📖 Mode Texte - Lecture',
            'audio': '🎧 Mode Audio - Écoute',
            'video': '🎬 Mode Vidéo - Visuel'
        }
        
        return {
            'recommended_mode': mode,
            'learner_type': learner_type,
            'recommended_title': titles.get(mode, f"Mode {mode}"),
            'confidence': confidence,
            'confidence_text': 'Élevée' if confidence > 0.7 else 'Moyenne' if confidence > 0.4 else 'Faible',
            'message': messages.get(mode, "Continuez sur votre lancée !"),
            'scores': {k: round(v * 100, 1) for k, v in scores.items()},
            'metrics': {
                'text': round(metrics.get('text', {}).get('avg_score', 0), 1),
                'audio': round(metrics.get('audio', {}).get('avg_score', 0), 1),
                'video': round(metrics.get('video', {}).get('avg_score', 0), 1)
            }
        }
    
    def predict_best_mode(self, metrics: Dict[str, Dict], user_profile: Optional[Dict] = None) -> Dict[str, Any]:
        
        
        
        
        scores = {}
        
        
        real_scores = {
            'text': metrics.get('text', {}).get('avg_score', 0),
            'audio': metrics.get('audio', {}).get('avg_score', 0),
            'video': metrics.get('video', {}).get('avg_score', 0)
        }
        
        
        for mode, data in metrics.items():
            if data.get('sessions', 0) == 0:
                scores[mode] = 0.3
            else:
                
                score = (
                    data.get('avg_score', 0) / 100 * 0.7 +
                    data.get('success_rate', 0) * 0.2 +
                    data.get('avg_completion', 0) / 100 * 0.1
                )
                scores[mode] = min(score, 1.0)
        
        
        
        best_real_score = max(real_scores.values())
        
        
        best_modes = [mode for mode, score in real_scores.items() if score == best_real_score]
        
        
        if len(best_modes) > 1:
            sessions = {mode: metrics.get(mode, {}).get('sessions', 0) for mode in best_modes}
            best_mode = max(sessions, key=sessions.get)
        else:
            best_mode = best_modes[0]
        
        best_score = real_scores[best_mode]
        
        logger.info(f"Scores réels: texte={real_scores['text']:.1f}%, audio={real_scores['audio']:.1f}%, video={real_scores['video']:.1f}%")
        logger.info(f"Meilleur mode détecté: {best_mode} avec score {best_score:.1f}%")
        
        
        mode_names = {'text': 'texte', 'audio': 'audio', 'video': 'vidéo'}
        mode_emoji = {'text': '📖', 'audio': '🎧', 'video': '🎬'}
        mode_to_learner = {'text': 'lecture', 'audio': 'auditif', 'video': 'visuel'}
        
        learner_type = mode_to_learner.get(best_mode, 'mixte')
        
        
        message = f"{mode_emoji[best_mode]} Vous excellez dans le mode {mode_names[best_mode]} (score {best_score:.1f}%) ! Continuez avec les cours en {mode_names[best_mode]} pour maximiser votre apprentissage."
        
        
        other_modes = [m for m in ['text', 'audio', 'video'] if m != best_mode and real_scores[m] >= 95]
        if other_modes:
            other_names = [mode_names[m] for m in other_modes]
            message += f" Le mode {', '.join(other_names)} est également excellent pour vous."
        
        
        confidence = best_score / 100
        
        return {
            'recommended_mode': best_mode,
            'learner_type': learner_type,
            'recommended_title': f"{mode_emoji[best_mode]} Mode {mode_names[best_mode].capitalize()}",
            'confidence': confidence,
            'confidence_text': 'Élevée' if confidence > 0.7 else 'Moyenne' if confidence > 0.4 else 'Faible',
            'message': message,
            'scores': {k: round(v * 100, 1) for k, v in scores.items()},
            'metrics': {
                'text': round(real_scores['text'], 1),
                'audio': round(real_scores['audio'], 1),
                'video': round(real_scores['video'], 1)
            }
        }

    def _adjust_by_profile(self, scores: Dict, profile: Dict) -> Dict:
        
        type_apprenant = profile.get('type_apprenant', 'mixte')
        
        
        type_mapping = {
            'visuel': 'video',
            'auditif': 'audio',
            'lecture': 'texte',
            'mixte': None
        }
        
        preferred_mode = type_mapping.get(type_apprenant)
        if preferred_mode and preferred_mode in scores:
            scores[preferred_mode] *= 1.2
        
        return scores
    
    def generate_recommendation(self, predicted_mode, prob_dict, user_metrics, user_preferences):
        
        
        
        mode_metrics = {}
        for mode in ['text', 'audio', 'video']:
            mode_metrics[mode] = {
                'score': float(user_metrics.get(mode, {}).get('avg_score', 0)),
                'sessions': int(user_metrics.get(mode, {}).get('sessions', 0)),
                'success_rate': float(user_metrics.get(mode, {}).get('success_rate', 0) * 100),
                'completion': float(user_metrics.get(mode, {}).get('avg_completion', 0))
            }
        
        
        reasons = {
            'text': {
                'title': '📖 Apprentissage par la Lecture',
                'description': 'Vous apprenez mieux en lisant et en écrivant.',
                'details': [
                    f"Score moyen: {mode_metrics['text']['score']:.1f}%",
                    f"Taux de réussite: {mode_metrics['text']['success_rate']:.1f}%",
                    f"{mode_metrics['text']['sessions']} sessions complétées"
                ],
                'strengths': [
                    "Lecture et compréhension écrite",
                    "Prise de notes efficace",
                    "Analyse de code commenté"
                ],
                'next_steps': [
                    "Pratiquez avec des exercices écrits",
                    "Documentez vos apprentissages",
                    "Créez des fiches de révision"
                ]
            },
            'audio': {
                'title': '🎧 Apprentissage Auditif',
                'description': 'Vous retenez mieux les informations en écoutant.',
                'details': [
                    f"Score moyen: {mode_metrics['audio']['score']:.1f}%",
                    f"Taux de réussite: {mode_metrics['audio']['success_rate']:.1f}%",
                    f"{mode_metrics['audio']['sessions']} sessions complétées"
                ],
                'strengths': [
                    "Compréhension orale",
                    "Mémorisation par répétition",
                    "Apprentissage en mobilité"
                ],
                'next_steps': [
                    "Écoutez des podcasts techniques",
                    "Expliquez les concepts à voix haute",
                    "Utilisez des outils de synthèse vocale"
                ]
            },
            'video': {
                'title': '🎬 Apprentissage Visuel',
                'description': 'Les démonstrations visuelles vous aident à comprendre.',
                'details': [
                    f"Score moyen: {mode_metrics['video']['score']:.1f}%",
                    f"Taux de réussite: {mode_metrics['video']['success_rate']:.1f}%",
                    f"{mode_metrics['video']['sessions']} sessions complétées"
                ],
                'strengths': [
                    "Compréhension des concepts visuels",
                    "Apprentissage par l'exemple",
                    "Visualisation des résultats"
                ],
                'next_steps': [
                    "Regardez des tutoriels vidéo",
                    "Observez des démonstrations en direct",
                    "Créez des mind maps visuels"
                ]
            }
        }
        
        
        mixed_reason = {
            'title': '🔄 Apprentissage Mixte',
            'description': 'Vous bénéficiez d\'une approche combinant plusieurs modes.',
            'details': [
                f"Texte: {mode_metrics['text']['score']:.1f}%",
                f"Audio: {mode_metrics['audio']['score']:.1f}%",
                f"Vidéo: {mode_metrics['video']['score']:.1f}%"
            ],
            'strengths': [
                "Flexibilité d'apprentissage",
                "Adaptabilité à différents contenus",
                "Renforcement par la variété"
            ],
            'next_steps': [
                "Alternez entre les modes selon le contenu",
                "Utilisez le texte pour la théorie",
                "Privilégiez la vidéo pour les démonstrations",
                "Complétez avec l'audio pour les révisions"
            ]
        }
        
        recommendation = reasons.get(predicted_mode, mixed_reason)
        
        
        confidence_level = prob_dict.get(predicted_mode, 0.5)
        
        if confidence_level > 0.8:
            confidence_text = "Très élevée"
            confidence_color = "#10B981"
        elif confidence_level > 0.6:
            confidence_text = "Élevée"
            confidence_color = "#3B82F6"
        elif confidence_level > 0.4:
            confidence_text = "Moyenne"
            confidence_color = "#F59E0B"
        else:
            confidence_text = "Faible"
            confidence_color = "#EF4444"
        
        return {
            'recommended_mode': predicted_mode,
            'recommended_title': recommendation['title'],
            'confidence': float(confidence_level),
            'confidence_text': confidence_text,
            'confidence_color': confidence_color,
            'probabilities_dict': prob_dict,
            'description': recommendation['description'],
            'details': recommendation['details'],
            'strengths': recommendation['strengths'],
            'next_steps': recommendation['next_steps'],
            'metrics': mode_metrics,
            'timestamp': datetime.now().isoformat()
        }
    
    def update_model_with_new_data(self):
        
        user_data = self.fetch_user_learning_data()
        
        if not user_data or len(user_data) < 3:
            logger.warning("Not enough new data for update")
            return False
        
        
        X_new = []
        y_new = []
        
        for data in user_data:
            features = self.prepare_features(data['metrics'], data.get('preferences'))[0]
            X_new.append(features)
            y_new.append(data['actual_mode'])
        
        X_new = np.array(X_new)
        X_new_scaled = self.scaler.transform(X_new)
        y_new_encoded = self.label_encoder.transform(y_new)
        
        
        if hasattr(self.model, 'estimators_'):
            
            n_original = 100  
            X_original = np.random.rand(n_original, 19) * 100
            y_original = np.random.choice(['text', 'audio', 'video'], n_original)
            
            X_combined = np.vstack([X_original, X_new])
            y_combined = np.concatenate([y_original, y_new])
            
            X_combined_scaled = self.scaler.fit_transform(X_combined)
            y_combined_encoded = self.label_encoder.transform(y_combined)
            
            self.model.fit(X_combined_scaled, y_combined_encoded)
        
        self.save_model()
        logger.info("✅ Model updated with new data")
        return True


recommender = LearningRecommender()