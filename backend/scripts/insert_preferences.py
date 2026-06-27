import psycopg2
import json
from datetime import datetime
from psycopg2.extras import RealDictCursor

def get_connection():
    """Établir la connexion à PostgreSQL"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="plateforme_elearning",
            user="postgres",
            password="root",
            port="5432"
        )
        
        conn.cursor_factory = RealDictCursor
        return conn
    except Exception as e:
        print(f"❌ Erreur de connexion à la base de données: {e}")
        return None

def calculer_preferences_utilisateur(utilisateur_id):
    """Calculer les préférences d'apprentissage pour un utilisateur"""
    try:
        conn = get_connection()
        if not conn:
            return None
        
        cur = conn.cursor()
        
        
        cur.execute("""
            SELECT 
                mode,
                COUNT(*) as nb_cours,
                COALESCE(AVG(score_quiz), 0) as score_moyen,
                COALESCE(SUM(temps_passe), 0) as temps_total,
                COALESCE(SUM(CASE WHEN est_reussi THEN 1 ELSE 0 END), 0) as reussis
            FROM resultats_apprentissage 
            WHERE utilisateur_id = %s
            GROUP BY mode
            ORDER BY mode
        """, (utilisateur_id,))
        
        stats_par_mode = cur.fetchall()
        
        
        scores = {'texte': 0, 'audio': 0, 'video': 0}
        temps_par_mode = {'texte': 0, 'audio': 0, 'video': 0}
        
        for row in stats_par_mode:
            mode = row['mode']
            if mode in scores:
                scores[mode] = round(float(row['score_moyen']), 2)
                temps_par_mode[mode] = int(row['temps_total'])
        
        
        cur.execute("""
            SELECT 
                COUNT(DISTINCT mode) as modes_differents,
                COUNT(*) as total_cours
            FROM resultats_apprentissage 
            WHERE utilisateur_id = %s
        """, (utilisateur_id,))
        
        stats = cur.fetchone()
        modes_differents = stats['modes_differents'] if stats else 0
        total_cours = stats['total_cours'] if stats else 0
        
        
        if total_cours == 0:
            confiance = 40  
        elif modes_differents == 3:
            confiance = 90  
        elif modes_differents == 2:
            confiance = 75  
        else:
            confiance = 60  
        
        
        score_moyen_global = sum(scores.values()) / 3
        if score_moyen_global > 80:
            confiance = min(95, confiance + 10)
        
        
        historique = {
            "date_calcul": datetime.now().isoformat(),
            "utilisateur_id": utilisateur_id,
            "scores_par_mode": {},
            "statistiques_globales": {},
            "recommandations": [],
            "type_apprenant_detecte": ""
        }
        
        
        for mode in ['texte', 'audio', 'video']:
            historique["scores_par_mode"][mode] = {
                "score": scores[mode],
                "temps_total": temps_par_mode[mode]
            }
        
        
        cur.execute("""
            SELECT 
                COUNT(*) as total_cours,
                COALESCE(AVG(score_quiz), 0) as score_moyen_global,
                COALESCE(SUM(temps_passe), 0) as temps_total_global,
                COALESCE(SUM(CASE WHEN est_reussi THEN 1 ELSE 0 END), 0) as reussis_global
            FROM resultats_apprentissage 
            WHERE utilisateur_id = %s
        """, (utilisateur_id,))
        
        row = cur.fetchone()
        total_cours = row['total_cours'] if row else 0
        score_moyen_global = row['score_moyen_global'] if row else 0
        temps_total_global = row['temps_total_global'] if row else 0
        reussis_global = row['reussis_global'] if row else 0
        
        historique["statistiques_globales"] = {
            "total_cours": total_cours or 0,
            "score_moyen_global": round(float(score_moyen_global or 0), 2),
            "temps_total": temps_total_global or 0,
            "cours_reussis": reussis_global or 0,
            "taux_reussite": round((reussis_global / total_cours * 100) if total_cours > 0 else 0, 2)
        }
        
        
        meilleur_mode = max(scores, key=scores.get)
        scores_items = list(scores.items())
        scores_tries = sorted(scores_items, key=lambda x: x[1], reverse=True)
        
        if all(score > 80 for score in scores.values()):
            type_apprenant = "polyvalent"
            historique["recommandations"] = [
                "Vous excellez dans tous les formats d'apprentissage",
                "Continuez à varier les modes pour maintenir votre polyvalence",
                "Vous pouvez vous concentrer sur le format que vous préférez le plus"
            ]
        elif len(scores_tries) > 1 and scores[meilleur_mode] > scores[scores_tries[1][0]] + 10:
            
            type_apprenant = f"préfère le mode {meilleur_mode}"
            historique["recommandations"] = [
                f"Votre mode d'apprentissage préféré est le {meilleur_mode}",
                f"Continuez à explorer des cours en mode {meilleur_mode}",
                f"Essayez occasionnellement d'autres modes pour diversifier"
            ]
        else:
            type_apprenant = "équilibré"
            historique["recommandations"] = [
                "Vos performances sont équilibrées entre les différents modes",
                "Continuez à varier vos méthodes d'apprentissage",
                "Vous pouvez vous concentrer sur vos points forts"
            ]
        
        historique["type_apprenant_detecte"] = type_apprenant
        
        cur.close()
        conn.close()
        
        return {
            "utilisateur_id": utilisateur_id,
            "score_texte": scores['texte'],
            "score_audio": scores['audio'],
            "score_video": scores['video'],
            "confiance": confiance,
            "historique": json.dumps(historique, ensure_ascii=False)
        }
        
    except Exception as e:
        print(f"❌ Erreur lors du calcul des préférences: {e}")
        import traceback
        traceback.print_exc()
        return None

def inserer_preferences_apprentissage(preferences):
    
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="plateforme_elearning",
            user="postgres",
            password="root",
            port="5432"
        )
        
        cur = conn.cursor()
        
        
        cur.execute("""
            SELECT COUNT(*) FROM preferences_apprentissage 
            WHERE utilisateur_id = %s
        """, (preferences["utilisateur_id"],))
        
        existe_deja = cur.fetchone()[0] > 0
        
        if existe_deja:
            
            cur.execute("""
                UPDATE preferences_apprentissage 
                SET score_texte = %s,
                    score_audio = %s,
                    score_video = %s,
                    confiance = %s,
                    date_maj = CURRENT_TIMESTAMP,
                    historique = %s
                WHERE utilisateur_id = %s
            """, (
                preferences["score_texte"],
                preferences["score_audio"],
                preferences["score_video"],
                preferences["confiance"],
                preferences["historique"],
                preferences["utilisateur_id"]
            ))
            action = "mis à jour"
        else:
            
            cur.execute("""
                INSERT INTO preferences_apprentissage 
                (utilisateur_id, score_texte, score_audio, score_video, 
                 confiance, date_calcul, date_maj, historique)
                VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, %s)
            """, (
                preferences["utilisateur_id"],
                preferences["score_texte"],
                preferences["score_audio"],
                preferences["score_video"],
                preferences["confiance"],
                preferences["historique"]
            ))
            action = "inséré"
        
        conn.commit()
        cur.close()
        conn.close()
        
        print(f"✅ Préférences {action} avec succès pour l'utilisateur {preferences['utilisateur_id']}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'insertion des préférences: {e}")
        import traceback
        traceback.print_exc()
        return False

def afficher_preferences_utilisateur(utilisateur_id):
    
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="plateforme_elearning",
            user="postgres",
            password="root",
            port="5432"
        )
        
        cur = conn.cursor()
        
        cur.execute("""
            SELECT 
                id, utilisateur_id, score_texte, score_audio, score_video,
                confiance, date_calcul, date_maj, historique
            FROM preferences_apprentissage 
            WHERE utilisateur_id = %s
        """, (utilisateur_id,))
        
        preferences = cur.fetchone()
        cur.close()
        conn.close()
        
        if preferences:
            print("\n" + "="*60)
            print("📊 PRÉFÉRENCES D'APPRENTISSAGE")
            print("="*60)
            print(f"ID: {preferences[0]}")
            print(f"Utilisateur ID: {preferences[1]}")
            print(f"\nScores par mode:")
            print(f"  📖 Texte: {preferences[2]:.1f}%")
            print(f"  🔊 Audio: {preferences[3]:.1f}%")
            print(f"  🎬 Vidéo: {preferences[4]:.1f}%")
            print(f"\nConfiance: {preferences[5]}%")
            print(f"Date calcul: {preferences[6]}")
            print(f"Date MAJ: {preferences[7]}")
            
            
            historique = preferences[8]
            
            
            if isinstance(historique, str):
                try:
                    historique = json.loads(historique)
                except json.JSONDecodeError:
                    print(f"\n📝 Historique (texte): {historique[:200]}...")
                    return preferences
            
            
            if isinstance(historique, dict):
                print(f"\n📈 Historique:")
                print(f"  Type d'apprenant: {historique.get('type_apprenant_detecte', 'Non détecté')}")
                
                stats = historique.get('statistiques_globales', {})
                if stats:
                    print(f"\n  Statistiques globales:")
                    print(f"    Total cours: {stats.get('total_cours', 0)}")
                    print(f"    Score moyen: {stats.get('score_moyen_global', 0):.1f}%")
                    print(f"    Taux réussite: {stats.get('taux_reussite', 0):.1f}%")
                    print(f"    Temps total: {stats.get('temps_total', 0)}s")
                
                recommandations = historique.get('recommandations', [])
                if recommandations:
                    print(f"\n  Recommandations:")
                    for reco in recommandations[:3]:  
                        print(f"    • {reco}")
            
            print("\n" + "="*60)
        else:
            print(f"ℹ️ Aucune préférence trouvée pour l'utilisateur {utilisateur_id}")
        
        return preferences
        
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des préférences: {e}")
        return None

def afficher_preferences_toutes():
    
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="plateforme_elearning",
            user="postgres",
            password="root",
            port="5432"
        )
        
        cur = conn.cursor()
        
        cur.execute("""
            SELECT 
                id, utilisateur_id, score_texte, score_audio, score_video,
                confiance, date_calcul, date_maj
            FROM preferences_apprentissage 
            ORDER BY utilisateur_id
        """)
        
        all_preferences = cur.fetchall()
        cur.close()
        conn.close()
        
        if all_preferences:
            print("\n" + "="*80)
            print("📊 TOUTES LES PRÉFÉRENCES D'APPRENTISSAGE")
            print("="*80)
            print(f"{'ID':<4} {'User':<6} {'Texte':<7} {'Audio':<7} {'Vidéo':<7} {'Conf':<6} {'Date MAJ'}")
            print("-"*80)
            
            for pref in all_preferences:
                print(f"{pref[0]:<4} {pref[1]:<6} {pref[2]:<7.1f} {pref[3]:<7.1f} {pref[4]:<7.1f} {pref[5]:<6} {pref[7].strftime('%d/%m/%Y')}")
            
            print("="*80)
            print(f"Total: {len(all_preferences)} utilisateur(s) avec des préférences")
        else:
            print("ℹ️ Aucune préférence trouvée dans la base de données")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

def main():
    """Fonction principale"""
    print("🎯 CALCUL DES PRÉFÉRENCES D'APPRENTISSAGE")
    print("="*50)
    
    
    utilisateur_id = input("Entrez l'ID utilisateur (par défaut 4): ").strip()
    utilisateur_id = int(utilisateur_id) if utilisateur_id else 4
    
    
    calculer_tous = input("Calculer pour tous les utilisateurs? (o/N): ").strip().lower()
    
    if calculer_tous == 'o':
        
        try:
            conn = psycopg2.connect(
                host="localhost",
                database="plateforme_elearning",
                user="postgres",
                password="root",
                port="5432"
            )
            
            cur = conn.cursor()
            
            cur.execute("""
                SELECT DISTINCT utilisateur_id 
                FROM resultats_apprentissage 
                WHERE utilisateur_id IS NOT NULL
                ORDER BY utilisateur_id
            """)
            
            utilisateurs = cur.fetchall()
            cur.close()
            conn.close()
            
            print(f"\n🎯 Calcul des préférences pour {len(utilisateurs)} utilisateurs...")
            
            for (user_id,) in utilisateurs:
                print(f"\n📊 Utilisateur {user_id}:")
                preferences = calculer_preferences_utilisateur(user_id)
                if preferences:
                    success = inserer_preferences_apprentissage(preferences)
                    if success:
                        print(f"  ✅ Préférences calculées et enregistrées")
                        
                        print(f"    Scores: Texte={preferences['score_texte']:.1f}%, "
                              f"Audio={preferences['score_audio']:.1f}%, "
                              f"Vidéo={preferences['score_video']:.1f}%")
                        print(f"    Confiance: {preferences['confiance']}%")
                    else:
                        print(f"  ❌ Échec de l'insertion")
                else:
                    print(f"  ⚠️ Pas de données ou erreur de calcul")
            
            print("\n✅ Calcul terminé pour tous les utilisateurs!")
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
    
    else:
        
        print(f"\n🎯 Calcul des préférences pour l'utilisateur {utilisateur_id}...")
        
        
        preferences = calculer_preferences_utilisateur(utilisateur_id)
        
        if not preferences:
            print("❌ Impossible de calculer les préférences.")
            return
        
        
        print(f"\n📈 Résultats du calcul:")
        print(f"  Score texte: {preferences['score_texte']:.1f}%")
        print(f"  Score audio: {preferences['score_audio']:.1f}%")
        print(f"  Score vidéo: {preferences['score_video']:.1f}%")
        print(f"  Confiance: {preferences['confiance']}%")
        
        
        confirmer = input(f"\nInsérer ces préférences pour l'utilisateur {utilisateur_id}? (O/n): ").strip().lower()
        
        if confirmer != 'n':
            
            success = inserer_preferences_apprentissage(preferences)
            
            if success:
                
                print(f"\n✅ Préférences enregistrées avec succès!")
                afficher_preferences_utilisateur(utilisateur_id)
            else:
                print("❌ Erreur lors de l'enregistrement.")
        else:
            print("❌ Insertion annulée.")

def inserer_exemple_manuel():
    
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="plateforme_elearning",
            user="postgres",
            password="root",
            port="5432"
        )
        
        cur = conn.cursor()
        
        historique_json = json.dumps({
            "date_calcul": datetime.now().isoformat(),
            "utilisateur_id": 4,
            "scores_par_mode": {
                "texte": {"score": 100, "nb_cours": 1, "temps_total": 60},
                "audio": {"score": 100, "nb_cours": 1, "temps_total": 60},
                "video": {"score": 100, "nb_cours": 1, "temps_total": 90}
            },
            "statistiques_globales": {
                "total_cours": 3,
                "score_moyen_global": 100.0,
                "temps_total": 210,
                "cours_reussis": 3,
                "taux_reussite": 100.0
            },
            "type_apprenant_detecte": "polyvalent",
            "recommandations": [
                "Vous excellez dans tous les formats d'apprentissage",
                "Continuez à varier les modes pour maintenir votre polyvalence",
                "Vous pouvez vous concentrer sur le format que vous préférez le plus"
            ],
            "performance": "excellente",
            "mode_prefere": "tous",
            "niveau": "avance"
        }, ensure_ascii=False)
        
        cur.execute("""
            INSERT INTO preferences_apprentissage 
            (utilisateur_id, score_texte, score_audio, score_video, 
             confiance, date_calcul, date_maj, historique)
            VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, %s)
            ON CONFLICT (utilisateur_id) 
            DO UPDATE SET
                score_texte = EXCLUDED.score_texte,
                score_audio = EXCLUDED.score_audio,
                score_video = EXCLUDED.score_video,
                confiance = EXCLUDED.confiance,
                date_maj = EXCLUDED.date_maj,
                historique = EXCLUDED.historique
        """, (
            4,      
            100.0,  
            100.0,  
            100.0,  
            90,     
            historique_json
        ))
        
        conn.commit()
        cur.close()
        conn.close()
        
        print("✅ Exemple manuel inséré avec succès pour l'utilisateur 4")
        
        
        afficher_preferences_utilisateur(4)
        
    except Exception as e:
        print(f"❌ Erreur lors de l'insertion manuelle: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("="*60)
    print("SCRIPT D'INSERTION DES PRÉFÉRENCES D'APPRENTISSAGE")
    print("="*60)
    
    print("\nOptions disponibles:")
    print("1. Calculer automatiquement à partir des résultats")
    print("2. Insérer un exemple manuel pour l'utilisateur 4")
    print("3. Vérifier les préférences existantes")
    print("4. Lister toutes les préférences")
    print("5. Quitter")
    
    choix = input("\nVotre choix (1/2/3/4/5): ").strip()
    
    if choix == "1":
        main()
    elif choix == "2":
        inserer_exemple_manuel()
    elif choix == "3":
        user_id = input("ID utilisateur à vérifier (par défaut 4): ").strip()
        user_id = int(user_id) if user_id else 4
        afficher_preferences_utilisateur(user_id)
    elif choix == "4":
        afficher_preferences_toutes()
    elif choix == "5":
        print("👋 Au revoir!")
    else:
        print("❌ Choix invalide.")