from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
import logging
from ml.recommender import recommender
from auth import get_current_user
from models.user import UserInDB
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import datetime 
router = APIRouter(prefix="/recommend", tags=["recommendations"])
logger = logging.getLogger(__name__)

def get_db_connection():
    
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'plateforme_elearning'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'root'),
            port=os.getenv('DB_PORT', 5432),
            cursor_factory=RealDictCursor
        )
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return None

def get_user_metrics(user_id: int):
    
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cur = conn.cursor()
        
        
        query = """
        SELECT 
            mode,
            AVG(score_quiz) as avg_score,
            AVG(temps_passe) as avg_time,
            COUNT(*) as sessions,
            AVG(taux_completion) as avg_completion,
            SUM(CASE WHEN est_reussi THEN 1 ELSE 0 END)::float / COUNT(*) as success_rate,
            MAX(date_completion) as last_activity
        FROM resultats_apprentissage
        WHERE utilisateur_id = %s
        GROUP BY mode
        """
        
        cur.execute(query, (user_id,))
        results = cur.fetchall()
        
        
        pref_query = """
        SELECT score_texte, score_audio, score_video, confiance
        FROM preferences_apprentissage
        WHERE utilisateur_id = %s
        ORDER BY date_calcul DESC
        LIMIT 1
        """
        
        cur.execute(pref_query, (user_id,))
        preferences = cur.fetchone()
        
        cur.close()
        conn.close()
        
        
        metrics = {
            'text': {'avg_score': 0, 'avg_time': 0, 'sessions': 0, 'avg_completion': 0, 'success_rate': 0},
            'audio': {'avg_score': 0, 'avg_time': 0, 'sessions': 0, 'avg_completion': 0, 'success_rate': 0},
            'video': {'avg_score': 0, 'avg_time': 0, 'sessions': 0, 'avg_completion': 0, 'success_rate': 0}
        }
        
        for row in results:
            mode = row['mode']
            if mode in metrics:
                metrics[mode] = {
                    'avg_score': row['avg_score'] or 0,
                    'avg_time': row['avg_time'] or 0,
                    'sessions': row['sessions'] or 0,
                    'avg_completion': row['avg_completion'] or 0,
                    'success_rate': row['success_rate'] or 0
                }
        
        return metrics, preferences
        
    except Exception as e:
        logger.error(f"Error getting user metrics: {e}")
        return None, None

@router.get("/learning-mode")
async def recommend_learning_mode(
    current_user: UserInDB = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Recommend the best learning mode for the current user
    based on their learning history and preferences
    """
    try:
        
        metrics, preferences = get_user_metrics(current_user.id)
        
        if not metrics:
            
            return {
                'recommended_mode': 'video',  
                'recommended_title': '🎬 Commencez avec la Vidéo',
                'confidence': 0.5,
                'confidence_text': 'Moyenne',
                'confidence_color': '#F59E0B',
                'probabilities_dict': {'text': 0.3, 'audio': 0.3, 'video': 0.4},
                'description': 'Pour débuter, nous recommandons le mode vidéo qui offre une introduction visuelle complète.',
                'details': [
                    "Aucune donnée d'apprentissage disponible",
                    "Basé sur les statistiques des nouveaux apprenants"
                ],
                'strengths': [
                    "Découverte progressive des concepts",
                    "Exemples visuels concrets",
                    "Démonstrations pas à pas"
                ],
                'next_steps': [
                    "Commencez par regarder une vidéo d'introduction",
                    "Pratiquez avec les exercices associés",
                    "Passez le quiz de validation"
                ],
                'metrics': {},
                'timestamp': datetime.now().isoformat()
            }
        
        
        recommendation = recommender.predict_best_mode(metrics, preferences)
        
        return recommendation
        
    except Exception as e:
        logger.error(f"Error in recommendation: {e}")
        raise HTTPException(status_code=500, detail="Error generating recommendation")

@router.get("/learning-mode/{user_id}")
async def recommend_for_user(
    user_id: int,
    current_user: UserInDB = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Recommend learning mode for a specific user (admin only)
    """
    
    if current_user.role_name != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        metrics, preferences = get_user_metrics(user_id)
        
        if not metrics:
            return {
                'recommended_mode': 'video',
                'message': 'No learning data available for this user',
                'recommendation': 'Start with video mode'
            }
        
        recommendation = recommender.predict_best_mode(metrics, preferences)
        recommendation['user_id'] = user_id
        
        return recommendation
        
    except Exception as e:
        logger.error(f"Error in recommendation for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Error generating recommendation")

@router.post("/update-model")
async def update_recommendation_model(
    current_user: UserInDB = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Update the ML model with new data (admin only)
    """
    if current_user.role_name != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        success = recommender.update_model_with_new_data()
        
        if success:
            return {
                'status': 'success',
                'message': 'Model updated successfully'
            }
        else:
            return {
                'status': 'partial',
                'message': 'Not enough new data for update'
            }
            
    except Exception as e:
        logger.error(f"Error updating model: {e}")
        raise HTTPException(status_code=500, detail="Error updating model")

@router.get("/model-info")
async def get_model_info(
    current_user: UserInDB = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get information about the recommendation model (admin only)
    """
    if current_user.role_name != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        if recommender.model:
            feature_names = [
                'text_score', 'audio_score', 'video_score',
                'text_time', 'audio_time', 'video_time',
                'text_sessions', 'audio_sessions', 'video_sessions',
                'text_completion', 'audio_completion', 'video_completion',
                'text_success_rate', 'audio_success_rate', 'video_success_rate',
                'pref_text_score', 'pref_audio_score', 'pref_video_score', 'pref_confidence'
            ]
            
            importance = pd.DataFrame({
                'feature': feature_names[:len(recommender.model.feature_importances_)],
                'importance': recommender.model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            return {
                'model_type': type(recommender.model).__name__,
                'n_estimators': recommender.model.n_estimators if hasattr(recommender.model, 'n_estimators') else None,
                'max_depth': recommender.model.max_depth,
                'classes': recommender.label_encoder.classes_.tolist(),
                'feature_importance': importance.to_dict('records'),
                'model_path': recommender.model_path
            }
        else:
            return {'message': 'Model not loaded'}
            
    except Exception as e:
        logger.error(f"Error getting model info: {e}")
        raise HTTPException(status_code=500, detail="Error getting model information")