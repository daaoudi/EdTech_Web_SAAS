
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
        
        
        cur.execute("SELECT id FROM utilisateurs WHERE est_actif = true LIMIT 1")
        user = cur.fetchone()
        
        if user:
            user_id = user[0]
            print(f"⚠️ Aucun admin trouvé. Utilisation ID: {user_id}")
            cur.close()
            conn.close()
            return user_id
        
        cur.close()
        conn.close()
        print("❌ Aucun utilisateur trouvé")
        return None
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None

def inserer_questions_formulaires():
    
    
    
    COURS_ID = 8
    SLUG_COURS = "formulaires-html-avances"
    
    admin_id = get_admin_user()
    if not admin_id:
        print("❌ Impossible de trouver un utilisateur")
        return False
    
    conn = get_connection()
    if not conn:
        return False
    
    cur = conn.cursor()
    
    
    cur.execute("SELECT id, titre FROM cours_html WHERE id = %s OR slug = %s", (COURS_ID, SLUG_COURS))
    cours = cur.fetchone()
    
    if not cours:
        print(f"❌ Cours non trouvé (ID: {COURS_ID} ou slug: {SLUG_COURS})")
        cur.close()
        conn.close()
        return False
    
    cours_id = cours[0]
    cours_titre = cours[1]
    print(f"\n📚 Cours trouvé: {cours_titre} (ID: {cours_id})")
    
    
    questions = [
        {
            "question": "Quelle est la méthode HTTP par défaut pour un formulaire HTML ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "GET",
                "B": "POST",
                "C": "PUT",
                "D": "DELETE"
            },
            "reponse_correcte": "A",
            "explication": "La méthode GET est la méthode par défaut pour les formulaires HTML. Elle envoie les données dans l'URL.",
            "mode_specifique": "texte"
        },
        {
            "question": "Quel attribut HTML5 permet de valider automatiquement un champ email ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "validate='email'",
                "B": "type='email'",
                "C": "format='email'",
                "D": "input='email'"
            },
            "reponse_correcte": "B",
            "explication": "L'attribut type='email' active la validation automatique du format email dans les navigateurs modernes.",
            "mode_specifique": "video"
        },
        {
            "question": "Comment spécifier qu'un champ de formulaire est obligatoire en HTML5 ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "required",
                "B": "mandatory",
                "C": "obligatory",
                "D": "force"
            },
            "reponse_correcte": "A",
            "explication": "L'attribut 'required' rend un champ obligatoire. Le formulaire ne peut pas être soumis sans remplir ce champ.",
            "mode_specifique": "audio"
        },
        {
            "question": "Quel attribut permet de limiter le nombre de caractères dans un champ texte ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "facile",
            "options": {
                "A": "limit",
                "B": "maxchars",
                "C": "maxlength",
                "D": "maxsize"
            },
            "reponse_correcte": "C",
            "explication": "L'attribut 'maxlength' limite le nombre de caractères qu'un utilisateur peut saisir dans un champ.",
            "mode_specifique": "texte"
        },
        {
            "question": "Quel type d'input permet de sélectionner une couleur ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "moyen",
            "options": {
                "A": "type='color'",
                "B": "type='picker'",
                "C": "type='hsl'",
                "D": "type='rgb'"
            },
            "reponse_correcte": "A",
            "explication": "type='color' crée un sélecteur de couleur. C'est une fonctionnalité HTML5.",
            "mode_specifique": "video"
        },
        {
            "question": "Quel attribut est utilisé pour l'autocomplétion des champs de formulaire ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "moyen",
            "options": {
                "A": "autocomplete",
                "B": "autofill",
                "C": "suggest",
                "D": "complete"
            },
            "reponse_correcte": "A",
            "explication": "L'attribut 'autocomplete' permet au navigateur de suggérer des valeurs basées sur les entrées précédentes.",
            "mode_specifique": "audio"
        },
        {
            "question": "Comment spécifier un intervalle de valeurs pour un champ number (min=10, max=100) ?",
            "type_question": "choix_multiple",
            "points": 15,
            "difficulte": "moyen",
            "options": {
                "A": "min='10' max='100'",
                "B": "between='10-100'",
                "C": "range='10-100'",
                "D": "values='10,100'"
            },
            "reponse_correcte": "A",
            "explication": "Les attributs 'min' et 'max' définissent respectivement les valeurs minimale et maximale pour un champ number.",
            "mode_specifique": "texte"
        },
        {
            "question": "Quel type d'input crée une liste déroulante avec des suggestions (texte libre possible) ?",
            "type_question": "choix_multiple",
            "points": 15,
            "difficulte": "difficile",
            "options": {
                "A": "datalist",
                "B": "select",
                "C": "dropdown",
                "D": "combobox"
            },
            "reponse_correcte": "A",
            "explication": "L'élément <datalist> associé à <input list='id'> permet de combiner une liste déroulante avec la saisie libre.",
            "mode_specifique": "video"
        },
        {
            "question": "Quel encodage (enctype) est nécessaire pour envoyer des fichiers via un formulaire ?",
            "type_question": "choix_multiple",
            "points": 15,
            "difficulte": "difficile",
            "options": {
                "A": "multipart/form-data",
                "B": "application/x-www-form-urlencoded",
                "C": "text/plain",
                "D": "application/json"
            },
            "reponse_correcte": "A",
            "explication": "multipart/form-data est obligatoire pour l'upload de fichiers. Il permet d'envoyer des données binaires.",
            "mode_specifique": "texte"
        },
        {
            "question": "Quel attribut désactive la validation HTML5 d'un formulaire ?",
            "type_question": "choix_multiple",
            "points": 10,
            "difficulte": "moyen",
            "options": {
                "A": "novalidate",
                "B": "novalidation",
                "C": "skip-validate",
                "D": "no-validate"
            },
            "reponse_correcte": "A",
            "explication": "L'attribut 'novalidate' sur la balise <form> désactive la validation HTML5 intégrée.",
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
                RETURNING id
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
            
            question_id = cur.fetchone()[0]
            questions_creees += 1
            print(f"  ✅ Question créée (ID {question_id}): {q['question'][:50]}...")
            
        except Exception as e:
            print(f"  ❌ Erreur: {e}")
    
    conn.commit()
    cur.close()
    conn.close()
    
    print(f"\n📊 RÉSUMÉ:")
    print(f"   • Cours: {cours_titre} (ID: {cours_id})")
    print(f"   • Questions créées: {questions_creees}")
    print(f"   • Questions existantes: {questions_existantes}")
    print(f"   • Total: {questions_creees + questions_existantes}")
    
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
            WHERE q.cours_id = 8
            ORDER BY q.id
        """)
        
        questions = cur.fetchall()
        
        if questions:
            print("\n📋 QUESTIONS EXISTANTES POUR LE COURS FORMULAIRES")
            print("=" * 80)
            for q in questions:
                print(f"ID: {q[0]} | {q[3]} | {q[1][:60]}... | Points: {q[4]} | Diff: {q[2]}")
        else:
            print("\n📋 Aucune question existante pour ce cours")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

def menu():
    
    print("\n" + "=" * 60)
    print("🎓 QUESTIONS POUR COURS: FORMULAIRES HTML AVANCÉS")
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
        inserer_questions_formulaires()
    elif choix == "3":
        lister_questions_existantes()
        inserer_questions_formulaires()
    elif choix == "4":
        print("\n👋 Au revoir !")
        return False
    else:
        print("❌ Choix invalide.")
    
    return True

if __name__ == "__main__":
    print("\n" + "🌟" * 30)
    print("🔧 INSERTION DES QUESTIONS FORMULAIRES HTML")
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