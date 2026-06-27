
import psycopg2
import json

def get_connection():
    
    try:
        return psycopg2.connect(
            host="localhost",
            database="plateforme_elearning",
            user="postgres",
            password="root",
            port="5432"
        )
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return None

def get_admin_user():
    
    try:
        conn = get_connection()
        if not conn:
            return None
        
        cur = conn.cursor()
        
        
        cur.execute("""
            SELECT u.id 
            FROM utilisateurs u
            JOIN roles r ON u.role_id = r.id
            WHERE r.nom_role = 'admin' AND u.est_actif = true
            LIMIT 1
        """)
        
        admin = cur.fetchone()
        
        if admin:
            admin_id = admin[0]
            print(f"✅ Admin trouvé (ID: {admin_id})")
            cur.close()
            conn.close()
            return admin_id
        
        cur.close()
        conn.close()
        print("❌ Aucun admin trouvé")
        return None
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None

def inserer_questions_css():
    
    
    COURS_ID = 10
    
    admin_id = get_admin_user()
    if not admin_id:
        print("❌ Impossible de trouver un utilisateur")
        return False
    
    conn = get_connection()
    if not conn:
        return False
    
    cur = conn.cursor()
    
    
    cur.execute("SELECT id, titre FROM cours_html WHERE id = %s", (COURS_ID,))
    cours = cur.fetchone()
    
    if not cours:
        print(f"❌ Cours non trouvé (ID: {COURS_ID})")
        cur.close()
        conn.close()
        return False
    
    cours_id = cours[0]
    cours_titre = cours[1]
    print(f"\n📚 Cours trouvé: {cours_titre} (ID: {cours_id})")
    
    
    questions = [
        {
            "question": "Quelle propriété CSS permet d'activer Flexbox sur un conteneur ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {"A": "display: flex", "B": "display: block", "C": "display: grid", "D": "display: inline"},
            "reponse_correcte": "A",
            "explication": "display: flex active le mode Flexbox sur un conteneur.",
            "mode_specifique": "texte"
        },
        {
            "question": "Quelle propriété CSS permet d'aligner les éléments horizontalement en Flexbox ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {"A": "align-items", "B": "justify-content", "C": "flex-direction", "D": "align-content"},
            "reponse_correcte": "B",
            "explication": "justify-content contrôle l'alignement horizontal en Flexbox.",
            "mode_specifique": "video"
        },
        {
            "question": "Que signifie 'fr' dans CSS Grid ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "moyen",
            "options": {"A": "Fraction", "B": "Frame", "C": "Flexible Ratio", "D": "Free space"},
            "reponse_correcte": "A",
            "explication": "fr signifie 'fraction' en CSS Grid.",
            "mode_specifique": "audio"
        },
        {
            "question": "Quelle propriété CSS Grid définit le nombre et la taille des colonnes ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "moyen",
            "options": {"A": "grid-template-rows", "B": "grid-template-columns", "C": "grid-gap", "D": "grid-auto-flow"},
            "reponse_correcte": "B",
            "explication": "grid-template-columns définit les colonnes d'une grille.",
            "mode_specifique": "texte"
        },
        {
            "question": "Comment centrer un élément horizontalement et verticalement avec Flexbox ?",
            "type_question": "choix_multiple",
            "points": 15,
            "difficulte": "difficile",
            "options": {"A": "justify-content: center; align-items: center", "B": "text-align: center", "C": "margin: auto", "D": "position: absolute"},
            "reponse_correcte": "A",
            "explication": "justify-content: center centre horizontalement, align-items: center centre verticalement.",
            "mode_specifique": "video"
        },
        {
            "question": "Quelle propriété Flexbox contrôle l'ordre d'affichage des éléments ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "moyen",
            "options": {"A": "order", "B": "flex-order", "C": "sort", "D": "sequence"},
            "reponse_correcte": "A",
            "explication": "La propriété 'order' permet de réordonner les éléments flexibles.",
            "mode_specifique": "audio"
        },
        {
            "question": "Quelle propriété CSS Grid permet de fusionner des cellules horizontalement ?",
            "type_question": "choix_multiple",
            "points": 15,
            "difficulte": "difficile",
            "options": {"A": "grid-column", "B": "grid-span", "C": "colspan", "D": "grid-merge"},
            "reponse_correcte": "A",
            "explication": "grid-column permet de fusionner des cellules horizontalement.",
            "mode_specifique": "texte"
        },
        {
            "question": "Quelle est la différence principale entre Flexbox et CSS Grid ?",
            "type_question": "choix_multiple",
            "points": 15,
            "difficulte": "difficile",
            "options": {"A": "Flexbox est 1D, Grid est 2D", "B": "Flexbox est plus récent", "C": "Grid ne fonctionne que sur mobile", "D": "Aucune différence"},
            "reponse_correcte": "A",
            "explication": "Flexbox gère une seule dimension, Grid gère les deux dimensions.",
            "mode_specifique": "video"
        },
        {
            "question": "Comment créer un espacement entre les éléments d'une grille CSS ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {"A": "gap", "B": "margin", "C": "padding", "D": "spacing"},
            "reponse_correcte": "A",
            "explication": "La propriété 'gap' définit l'espacement entre les éléments d'une grille.",
            "mode_specifique": "audio"
        },
        {
            "question": "Quelle propriété Flexbox fait passer les éléments à la ligne suivante ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "moyen",
            "options": {"A": "flex-wrap: wrap", "B": "flex-direction: column", "C": "flex-flow: row", "D": "flex-line: break"},
            "reponse_correcte": "A",
            "explication": "flex-wrap: wrap permet le passage à la ligne.",
            "mode_specifique": "texte"
        },
        {
            "question": "Comment définir un media query pour mobile (max-width: 768px) ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "moyen",
            "options": {"A": "@media (max-width: 768px)", "B": "@media screen (max-width: 768px)", "C": "@media (min-width: 768px)", "D": "@media mobile"},
            "reponse_correcte": "A",
            "explication": "@media (max-width: 768px) cible les écrans mobiles.",
            "mode_specifique": "video"
        },
        {
            "question": "Quelle propriété Flexbox permet d'étirer un élément pour remplir l'espace disponible ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "moyen",
            "options": {"A": "flex-grow", "B": "flex-shrink", "C": "flex-basis", "D": "flex-fill"},
            "reponse_correcte": "A",
            "explication": "flex-grow permet à un élément de prendre l'espace disponible.",
            "mode_specifique": "audio"
        }
    ]
    
    print(f"\n📝 Insertion de {len(questions)} questions...")
    
    questions_creees = 0
    questions_existantes = 0
    
    for q in questions:
        
        cur.execute("""
            SELECT id FROM questions_quiz 
            WHERE cours_id = %s AND question = %s
        """, (cours_id, q["question"]))
        
        existing = cur.fetchone()
        
        if existing:
            questions_existantes += 1
            print(f"  ⚠️ Question déjà existante: {q['question'][:50]}...")
            continue
        
        try:
            
            cur.execute("""
                INSERT INTO questions_quiz 
                (cours_id, question, type_question, points, difficulte, 
                 options, reponse_correcte, explication, mode_specifique, 
                 created_by, date_creation)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            """, (
                cours_id,
                q["question"],
                q["type_question"],
                q["points"],
                q["difficulte"],
                json.dumps(q["options"]),
                q["reponse_correcte"],
                q["explication"],
                q["mode_specifique"],
                admin_id
            ))
            
            questions_creees += 1
            print(f"  ✅ Question créée: {q['question'][:50]}...")
            
        except Exception as e:
            print(f"  ❌ Erreur: {e}")
    
    conn.commit()
    cur.close()
    conn.close()
    
    print(f"\n📊 RÉSUMÉ:")
    print(f"   • Cours: {cours_titre} (ID: {cours_id})")
    print(f"   • Questions créées: {questions_creees}")
    print(f"   • Questions existantes: {questions_existantes}")
    
    return True

def lister_questions_existantes():
    
    try:
        conn = get_connection()
        if not conn:
            return
        
        cur = conn.cursor()
        
        cur.execute("""
            SELECT q.id, q.question, q.difficulte, q.mode_specifique, q.points
            FROM questions_quiz q
            WHERE q.cours_id = 10
            ORDER BY q.id
        """)
        
        questions = cur.fetchall()
        
        if questions:
            print("\n📋 QUESTIONS EXISTANTES POUR LE COURS CSS")
            print("=" * 80)
            for q in questions:
                print(f"ID: {q[0]} | Mode: {q[3] or 'tous'} | Points: {q[4]} | Diff: {q[2]}")
                print(f"   Question: {q[1][:70]}...")
                print()
        else:
            print("\n📋 Aucune question existante pour ce cours")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

def menu():
    
    print("\n" + "=" * 60)
    print("🎓 QUESTIONS POUR COURS: CSS - MISE EN PAGE AVANCÉE")
    print("=" * 60)
    print("\nQue souhaitez-vous faire ?")
    print("1. Lister les questions existantes")
    print("2. Insérer les questions")
    print("3. Tout faire (lister + insérer)")
    print("4. Quitter")
    
    choix = input("\nVotre choix (1-4) : ").strip()
    
    if choix == "1":
        lister_questions_existantes()
    elif choix == "2":
        inserer_questions_css()
    elif choix == "3":
        lister_questions_existantes()
        inserer_questions_css()
    elif choix == "4":
        print("\n👋 Au revoir !")
        return False
    else:
        print("❌ Choix invalide.")
    
    return True

if __name__ == "__main__":
    print("\n" + "🌟" * 30)
    print("🔧 INSERTION DES QUESTIONS CSS - MISE EN PAGE")
    print("🌟" * 30)
    
    
    conn = get_connection()
    if not conn:
        print("❌ Impossible de se connecter à la base de données")
        exit(1)
    
    conn.close()
    print("✅ Connexion à la base de données établie")
    
    while menu():
        input("\nAppuyez sur Entrée pour continuer...")
    
    print("\n" + "🎉" * 30)
    print("SCRIPT TERMINÉ")
    print("🎉" * 30)