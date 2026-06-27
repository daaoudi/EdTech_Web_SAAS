
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

def inserer_questions_html5_semantique():
    
    
    COURS_ID = 9
    
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
            "question": "Quelle est la balise HTML5 pour l'en-tête d'une page ou d'une section ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "<head>",
                "B": "<header>",
                "C": "<h1>",
                "D": "<top>"
            },
            "reponse_correcte": "B",
            "explication": "La balise <header> représente l'en-tête d'une page ou d'une section.",
            "mode_specifique": "texte"
        },
        {
            "question": "Quelle balise HTML5 contient le contenu principal unique d'une page ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "<main>",
                "B": "<body>",
                "C": "<content>",
                "D": "<center>"
            },
            "reponse_correcte": "A",
            "explication": "<main> contient le contenu principal unique d'une page (un seul par page).",
            "mode_specifique": "video"
        },
        {
            "question": "Quelle balise HTML5 est utilisée pour la navigation principale ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "<menu>",
                "B": "<navigation>",
                "C": "<nav>",
                "D": "<navbar>"
            },
            "reponse_correcte": "C",
            "explication": "<nav> est utilisée pour regrouper les liens de navigation principaux.",
            "mode_specifique": "audio"
        },
        {
            "question": "Quelle balise HTML5 représente un contenu autonome (article, blog post, commentaire) ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "moyen",
            "options": {
                "A": "<div>",
                "B": "<section>",
                "C": "<content>",
                "D": "<article>"
            },
            "reponse_correcte": "D",
            "explication": "<article> représente un contenu autonome, réutilisable indépendamment.",
            "mode_specifique": "texte"
        },
        {
            "question": "Quelle balise HTML5 regroupe du contenu thématiquement lié ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "moyen",
            "options": {
                "A": "<group>",
                "B": "<section>",
                "C": "<part>",
                "D": "<block>"
            },
            "reponse_correcte": "B",
            "explication": "<section> regroupe du contenu thématiquement lié et doit avoir un titre.",
            "mode_specifique": "video"
        },
        {
            "question": "Quelle balise HTML5 contient du contenu complémentaire (sidebar) ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "moyen",
            "options": {
                "A": "<sidebar>",
                "B": "<side>",
                "C": "<aside>",
                "D": "<extra>"
            },
            "reponse_correcte": "C",
            "explication": "<aside> contient du contenu complémentaire (barre latérale, notes, etc.).",
            "mode_specifique": "audio"
        },
        {
            "question": "Quelle balise HTML5 représente le pied de page ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "<bottom>",
                "B": "<footer>",
                "C": "<foot>",
                "D": "<end>"
            },
            "reponse_correcte": "B",
            "explication": "<footer> représente le pied de page d'une page ou d'une section.",
            "mode_specifique": "texte"
        },
        {
            "question": "Quel est l'avantage principal des balises sémantiques HTML5 ?",
            "type_question": "choix_multiple",
            "points": 15,
            "difficulte": "difficile",
            "options": {
                "A": "Meilleure performance",
                "B": "Accessibilité et SEO améliorés",
                "C": "Compatibilité navigateur",
                "D": "Styles intégrés"
            },
            "reponse_correcte": "B",
            "explication": "Les balises sémantiques améliorent l'accessibilité (lecteurs d'écran) et le SEO.",
            "mode_specifique": "video"
        },
        {
            "question": "Combien de fois peut-on utiliser la balise <main> dans une page HTML ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "moyen",
            "options": {
                "A": "Autant qu'on veut",
                "B": "Une seule fois",
                "C": "Deux fois maximum",
                "D": "Une fois par section"
            },
            "reponse_correcte": "B",
            "explication": "Il ne doit y avoir qu'un seul <main> par page, contenant le contenu principal unique.",
            "mode_specifique": "audio"
        },
        {
            "question": "Quelle balise HTML5 est utilisée pour la date et l'heure ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "moyen",
            "options": {
                "A": "<date>",
                "B": "<time>",
                "C": "<calendar>",
                "D": "<datetime>"
            },
            "reponse_correcte": "B",
            "explication": "<time> représente une date, une heure ou une durée.",
            "mode_specifique": "texte"
        },
        {
            "question": "Quelle balise HTML5 est utilisée pour les figures/illustrations ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "moyen",
            "options": {
                "A": "<image>",
                "B": "<illustration>",
                "C": "<figure>",
                "D": "<media>"
            },
            "reponse_correcte": "C",
            "explication": "<figure> regroupe des illustrations avec <figcaption> pour la légende.",
            "mode_specifique": "video"
        },
        {
            "question": "Quel élément doit contenir la balise <section> ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "moyen",
            "options": {
                "A": "Un titre (h1-h6)",
                "B": "Un paragraphe",
                "C": "Une image",
                "D": "Un lien"
            },
            "reponse_correcte": "A",
            "explication": "Une <section> doit toujours avoir un titre pour être sémantiquement correcte.",
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
            WHERE q.cours_id = 9
            ORDER BY q.id
        """)
        
        questions = cur.fetchall()
        
        if questions:
            print("\n📋 QUESTIONS EXISTANTES POUR LE COURS HTML5 SÉMANTIQUE")
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
    print("🎓 QUESTIONS POUR COURS: HTML5 SÉMANTIQUE - STRUCTURES MODERNES")
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
        inserer_questions_html5_semantique()
    elif choix == "3":
        lister_questions_existantes()
        inserer_questions_html5_semantique()
    elif choix == "4":
        print("\n👋 Au revoir !")
        return False
    else:
        print("❌ Choix invalide.")
    
    return True

if __name__ == "__main__":
    print("\n" + "🌟" * 30)
    print("🔧 INSERTION DES QUESTIONS HTML5 SÉMANTIQUE")
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