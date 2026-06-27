
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from ml.recommender import LearningRecommender
import logging

logging.basicConfig(level=logging.INFO)

def main():
    print("=" * 60)
    print("ENTRAÎNEMENT DU MODÈLE DE RECOMMANDATION")
    print("=" * 60)
    
    
    recommender = LearningRecommender()
    
    print(f"\n✅ Modèle entraîné et sauvegardé")
    print(f"📁 Modèle: {recommender.model_path}")
    
    
    test_metrics = {
        'text': {'avg_score': 85, 'avg_time': 30, 'sessions': 5, 'avg_completion': 90, 'success_rate': 0.9},
        'audio': {'avg_score': 70, 'avg_time': 25, 'sessions': 3, 'avg_completion': 80, 'success_rate': 0.7},
        'video': {'avg_score': 75, 'avg_time': 28, 'sessions': 4, 'avg_completion': 85, 'success_rate': 0.8}
    }
    
    test_preferences = {
        'score_texte': 85,
        'score_audio': 70,
        'score_video': 75,
        'confiance': 80
    }
    
    print("\n🔍 Test avec utilisateur exemple:")
    try:
        recommendation = recommender.predict_best_mode(test_metrics, test_preferences)
        print(f"Mode recommandé: {recommendation['recommended_mode']}")
        print(f"Confiance: {recommendation['confidence']:.1%}")
        print(f"Probabilités: {recommendation['probabilities_dict']}")
        print(f"\n📊 Détails:")
        print(f"Titre: {recommendation['recommended_title']}")
        print(f"Description: {recommendation['description']}")
        print(f"\nPoints forts:")
        for strength in recommendation['strengths']:
            print(f"  • {strength}")
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("POUR UTILISER DANS L'API:")
    print("=" * 60)
    print("1. Démarrez le serveur FastAPI")
    print("2. Accédez à: http://localhost:8001/recommend/learning-mode")
    print("3. Header: Authorization: Bearer <votre_token>")

if __name__ == "__main__":
    main()