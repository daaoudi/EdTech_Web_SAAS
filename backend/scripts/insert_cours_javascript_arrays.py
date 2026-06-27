
import psycopg2
import json
from datetime import datetime

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

def get_chapitre_id():
    
    try:
        conn = get_connection()
        if not conn:
            return None
        
        cur = conn.cursor()
        cur.execute("SELECT id FROM chapitres WHERE id = 3 OR titre ILIKE %s", ('%JavaScript%',))
        result = cur.fetchone()
        cur.close()
        conn.close()
        
        if result:
            chapitre_id = result[0]
            print(f"📚 Chapitre JavaScript trouvé (ID: {chapitre_id})")
            return chapitre_id
        return None
    except Exception as e:
        print(f"⚠️ Erreur récupération chapitre: {e}")
        return None

def inserer_cours_javascript_arrays():
    
    
    admin_id = get_admin_user()
    if not admin_id:
        print("❌ Impossible de trouver un utilisateur")
        return False
    
    chapitre_id = get_chapitre_id()
    
    conn = get_connection()
    if not conn:
        return False
    
    cur = conn.cursor()
    
    slug_cours = "javascript-arrays"
    
    cur.execute("SELECT id FROM cours_html WHERE slug = %s", (slug_cours,))
    existing = cur.fetchone()
    
    contenu_html = """
    <h1>🗃️ JavaScript Arrays - Les Tableaux</h1>
    
    <div class="info-box">
        <p><strong>💡 À savoir :</strong> Un tableau est une variable spéciale qui peut stocker plusieurs valeurs. Les valeurs sont placées entre crochets et séparées par des virgules.</p>
    </div>
    
    <h2>Introduction aux Tableaux</h2>
    <p>Les tableaux permettent d'organiser et de manipuler des collections de données efficacement.</p>
    
    <h2>1. Créer un tableau</h2>
    <pre><code>let fruits = ["pomme", "banane", "orange", "mangue"];
let nombres = [10, 20, 30, 40, 50];</code></pre>
    
    <h2>2. Accéder aux éléments</h2>
    <pre><code>let fruits = ["pomme", "banane", "orange"];
console.log(fruits[0]); // "pomme"
console.log(fruits[1]); // "banane"</code></pre>
    
    <h2>3. Méthodes de tableau</h2>
    <pre><code>fruits.push("orange");   // Ajoute à la fin
fruits.pop();            // Retire de la fin
fruits.unshift("pomme"); // Ajoute au début
fruits.shift();          // Retire du début</code></pre>
    
    <h2>4. Propriété length</h2>
    <pre><code>console.log(fruits.length);</code></pre>
    
    <h2>5. Parcourir un tableau</h2>
    <pre><code>for (let fruit of fruits) {
    console.log(fruit);
}</code></pre>
    
    <div class="info-box">
        <p><strong>💡 À retenir :</strong> Les indices commencent à 0, et la propriété length est dynamique.</p>
    </div>
    """.strip()
    
    cours_data = {
        "titre": "JavaScript Arrays - Les Tableaux",
        "slug": slug_cours,
        "description": "Apprenez à utiliser les tableaux en JavaScript : création, accès aux éléments, méthodes push, pop, shift, unshift, propriété length, parcours et tri.",
        "contenu_texte": contenu_html,
        "difficulte": "debutant",
        "duree_estimee": 20,
        "ordre_affichage": 11,
        "chapitre_id": chapitre_id,
        "tags": ["javascript", "arrays", "push", "pop", "shift", "unshift", "length", "debutant"],
        "est_actif": True,
        "created_by": admin_id,
        "last_modified_by": admin_id
    }
    
    if existing:
        cours_id = existing[0]
        print(f"⚠️ Le cours existe déjà (ID: {cours_id})")
        cur.execute("""
            UPDATE cours_html 
            SET titre = %s, description = %s, contenu_texte = %s, 
                difficulte = %s, duree_estimee = %s, ordre_affichage = %s,
                chapitre_id = %s, tags = %s, est_actif = %s, last_modified_by = %s,
                date_maj = CURRENT_TIMESTAMP
            WHERE slug = %s
            RETURNING id
        """, (cours_data["titre"], cours_data["description"], cours_data["contenu_texte"],
              cours_data["difficulte"], cours_data["duree_estimee"], cours_data["ordre_affichage"],
              cours_data["chapitre_id"], cours_data["tags"], cours_data["est_actif"],
              cours_data["last_modified_by"], slug_cours))
        cours_id = cur.fetchone()[0]
        print(f"✅ Cours mis à jour (ID: {cours_id})")
    else:
        cur.execute("""
            INSERT INTO cours_html 
            (titre, slug, description, contenu_texte, difficulte, 
             duree_estimee, ordre_affichage, chapitre_id, tags, est_actif, 
             created_by, last_modified_by, date_creation, date_maj)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            RETURNING id
        """, (cours_data["titre"], cours_data["slug"], cours_data["description"], cours_data["contenu_texte"],
              cours_data["difficulte"], cours_data["duree_estimee"], cours_data["ordre_affichage"],
              cours_data["chapitre_id"], cours_data["tags"], cours_data["est_actif"],
              cours_data["created_by"], cours_data["last_modified_by"]))
        cours_id = cur.fetchone()[0]
        print(f"✅ Cours créé (ID: {cours_id})")
    
    conn.commit()
    cur.close()
    conn.close()
    return cours_id

def inserer_questions_javascript_arrays(cours_id):
    
    
    admin_id = get_admin_user()
    if not admin_id:
        return False
    
    conn = get_connection()
    if not conn:
        return False
    
    cur = conn.cursor()
    
    
    try:
        cur.execute("ALTER TABLE questions_quiz DISABLE TRIGGER trigger_log_questions")
        conn.commit()
    except:
        pass
    
    
    try:
        cur.execute("DELETE FROM questions_quiz WHERE cours_id = %s", (cours_id,))
        conn.commit()
        print(f"✅ Anciennes questions supprimées")
    except:
        conn.rollback()
    
    questions = [
        
        {
            "question": "Comment crée-t-on un tableau vide en JavaScript ?",
            "options": '{"A": "let arr = {}", "B": "let arr = []", "C": "let arr = ()", "D": "let arr = <>", "E": "let arr = "}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "Un tableau se crée avec des crochets [].",
            "mode_specifique": "texte"
        },
        {
            "question": "Quelle est la propriété qui donne le nombre d'éléments dans un tableau ?",
            "options": '{"A": "size", "B": "count", "C": "length", "D": "items", "E": "amount"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "length est la propriété qui retourne le nombre d'éléments.",
            "mode_specifique": "texte"
        },
        
        
        {
            "question": "Quelle méthode ajoute un élément à la fin d'un tableau ?",
            "options": '{"A": "push()", "B": "pop()", "C": "unshift()", "D": "shift()", "E": "append()"}',
            "reponse_correcte": "A",
            "points": 10,
            "difficulte": "facile",
            "explication": "push() ajoute un élément à la fin du tableau.",
            "mode_specifique": "audio"
        },
        {
            "question": "Quelle méthode supprime le premier élément d'un tableau ?",
            "options": '{"A": "push()", "B": "pop()", "C": "unshift()", "D": "shift()", "E": "removeFirst()"}',
            "reponse_correcte": "D",
            "points": 10,
            "difficulte": "facile",
            "explication": "shift() supprime le premier élément et le retourne.",
            "mode_specifique": "audio"
        },
        {
            "question": "À quel indice commence un tableau en JavaScript ?",
            "options": '{"A": "1", "B": "0", "C": "-1", "D": "depend", "E": "aucune"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "Les indices commencent à 0 en JavaScript.",
            "mode_specifique": "audio"
        },
        
        
        {
            "question": "Que retourne indexOf si l'élément n'est pas trouvé ?",
            "options": '{"A": "0", "B": "null", "C": "undefined", "D": "-1", "E": "false"}',
            "reponse_correcte": "D",
            "points": 10,
            "difficulte": "facile",
            "explication": "indexOf() retourne -1 si l'élément n'est pas dans le tableau.",
            "mode_specifique": "video"
        },
        {
            "question": "Quelle boucle est recommandée pour parcourir un tableau ?",
            "options": '{"A": "for", "B": "while", "C": "for...of", "D": "do...while", "E": "foreach"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "for...of est la boucle recommandée pour parcourir les valeurs d'un tableau.",
            "mode_specifique": "video"
        },
        {
            "question": "Que fait la méthode sort sur un tableau de mots ?",
            "options": '{"A": "Inverse l ordre", "B": "Trie alphabetiquement", "C": "Supprime les doublons", "D": "Ajoute des elements", "E": "Melange"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "sort() trie les éléments d'un tableau dans l'ordre alphabétique.",
            "mode_specifique": "video"
        },
        {
            "question": "Que fait la methode reverse sur un tableau ?",
            "options": '{"A": "Inverse l ordre", "B": "Trie alphabetiquement", "C": "Supprime les doublons", "D": "Ajoute des elements", "E": "Melange"}',
            "reponse_correcte": "A",
            "points": 10,
            "difficulte": "facile",
            "explication": "reverse() inverse l'ordre des éléments du tableau.",
            "mode_specifique": "video"
        },
        {
            "question": "Comment ajouter un element au debut d un tableau ?",
            "options": '{"A": "push()", "B": "pop()", "C": "unshift()", "D": "shift()", "E": "prepend()"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "unshift() ajoute un élément au début du tableau.",
            "mode_specifique": "video"
        },
        {
            "question": "Que signifie fruits[2] si fruits = pomme banane orange ?",
            "options": '{"A": "pomme", "B": "banane", "C": "orange", "D": "undefined", "E": "erreur"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "fruits[2] accède au troisième élément (indice 2).",
            "mode_specifique": "video"
        }
    ]
    
    print(f"\n📝 Insertion de {len(questions)} questions pour le cours ID {cours_id}...")
    
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
                VALUES (%s, %s, 'choix_multiple', %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            """, (
                cours_id,
                q["question"],
                q["points"],
                q["difficulte"],
                q["options"],
                q["reponse_correcte"],
                q["explication"],
                q["mode_specifique"],
                admin_id
            ))
            
            questions_creees += 1
            print(f"  ✅ [{q['mode_specifique'].upper()}] {q['question'][:50]}...")
            conn.commit()
            
        except Exception as e:
            print(f"  ❌ Erreur: {e}")
            conn.rollback()
    
    
    try:
        cur.execute("ALTER TABLE questions_quiz ENABLE TRIGGER trigger_log_questions")
        conn.commit()
    except:
        pass
    
    cur.close()
    conn.close()
    
    print(f"\n📊 RÉSUMÉ:")
    print(f"   • Questions créées: {questions_creees}")
    print(f"   • Questions existantes: {questions_existantes}")
    
    return True

def main():
    print("\n" + "=" * 60)
    print("🎓 INSERTION DU COURS: JAVASCRIPT ARRAYS")
    print("=" * 60)
    
    
    conn = get_connection()
    if not conn:
        print("❌ Impossible de se connecter à la base de données")
        return
    
    conn.close()
    print("✅ Connexion à la base de données établie")
    
    
    cours_id = inserer_cours_javascript_arrays()
    
    if cours_id:
        inserer_questions_javascript_arrays(cours_id)
        print(f"\n🎉 Succès ! Cours 'JavaScript Arrays - Les Tableaux' créé (ID: {cours_id})")
    else:
        print("\n❌ Échec de l'insertion")

if __name__ == "__main__":
    main()