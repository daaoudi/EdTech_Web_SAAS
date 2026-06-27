
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

def inserer_cours_javascript_objects():
    
    
    admin_id = get_admin_user()
    if not admin_id:
        print("❌ Impossible de trouver un utilisateur")
        return False
    
    chapitre_id = get_chapitre_id()
    
    conn = get_connection()
    if not conn:
        return False
    
    cur = conn.cursor()
    
    slug_cours = "javascript-objects"
    
    cur.execute("SELECT id FROM cours_html WHERE slug = %s", (slug_cours,))
    existing = cur.fetchone()
    
    contenu_html = """
    <h1>🧍 JavaScript Objects - Les Objets</h1>
    
    <div class="info-box">
        <p><strong>💡 À savoir :</strong> Un objet est une collection de propriétés et de méthodes associées.</p>
    </div>
    
    <h2>Qu'est-ce qu'un Objet ?</h2>
    <p>Un objet regroupe :</p>
    <ul>
        <li><strong>Propriétés</strong> : Des caractéristiques (nom, âge, couleur...)</li>
        <li><strong>Méthodes</strong> : Des actions ou comportements liés à l'objet</li>
    </ul>
    
    <div class="tip-box">
        <p><strong>💡 Pourquoi utiliser des objets ?</strong><br>
        - Modéliser des entités du monde réel<br>
        - Organiser le code de manière logique<br>
        - Regrouper des données et fonctionnalités associées</p>
    </div>
    
    <h2>1. Créer un objet</h2>
    <p>On utilise les accolades <code>{}</code> pour définir un objet avec des paires clé-valeur.</p>
    
    <pre><code>const person1 = {
    firstName: "Spongebob",
    lastName: "Squarepants",
    age: 30,
    isEmployed: true
};

const person2 = {
    firstName: "Patrick",
    lastName: "Star",
    age: 35,
    isEmployed: false
};</code></pre>
    
    <h2>2. Accéder aux propriétés</h2>
    <p>On utilise la notation pointée (dot notation).</p>
    
    <pre><code>console.log(person1.firstName); // "Spongebob"
console.log(person2.lastName);   // "Star"</code></pre>
    
    <h2>3. Ajouter des méthodes</h2>
    
    <pre><code>const person1 = {
    firstName: "Spongebob",
    sayHello: function() {
        console.log("Hi! I am Spongebob!");
    },
    eat: function() {
        console.log("I am eating a Krabby Patty");
    }
};</code></pre>
    
    <h2>4. Appeler les méthodes</h2>
    
    <pre><code>person1.sayHello();
person1.eat();</code></pre>
    
    <div class="info-box">
        <p><strong>💡 À retenir :</strong> Les objets combinent des propriétés (données) et des méthodes (actions).</p>
    </div>
    """.strip()
    
    cours_data = {
        "titre": "JavaScript Objects - Les Objets",
        "slug": slug_cours,
        "description": "Apprenez à utiliser les objets en JavaScript : création d'objets, propriétés, méthodes, accès aux propriétés.",
        "contenu_texte": contenu_html,
        "difficulte": "debutant",
        "duree_estimee": 20,
        "ordre_affichage": 10,
        "chapitre_id": chapitre_id,
        "tags": ["javascript", "objects", "properties", "methods", "dot-notation", "oop", "debutant"],
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

def inserer_questions_javascript_objects(cours_id):
    
    
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
            "question": "Qu'est-ce qu'un objet en JavaScript ?",
            "options": '{"A": "Un tableau de données", "B": "Une collection de propriétés et de méthodes", "C": "Une variable spéciale", "D": "Une boucle"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "Un objet est une collection de propriétés (données) et de méthodes (fonctions).",
            "mode_specifique": "texte"
        },
        {
            "question": "Comment accède-t-on à une propriété d'un objet ?",
            "options": '{"A": "object->property", "B": "object[property]", "C": "object.property", "D": "object:property"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "On utilise la notation pointée : objet.propriete.",
            "mode_specifique": "texte"
        },
        
        {
            "question": "Quelle syntaxe utilise-t-on pour créer un objet en JavaScript ?",
            "options": '{"A": "[]", "B": "()", "C": "{}", "D": "<>"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "Les objets sont créés avec des accolades {}.",
            "mode_specifique": "audio"
        },
        {
            "question": "Qu'est-ce qu'une méthode dans un objet ?",
            "options": '{"A": "Une propriété", "B": "Une fonction liée à l\'objet", "C": "Une variable", "D": "Un tableau"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "Une méthode est une fonction qui appartient à un objet.",
            "mode_specifique": "audio"
        },
        {
            "question": "Pourquoi utilise-t-on des objets en JavaScript ?",
            "options": '{"A": "Pour créer des boucles", "B": "Pour modéliser des entités du monde réel", "C": "Pour déclarer des variables", "D": "Pour importer des modules"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "Les objets modélisent des entités réelles avec leurs propriétés.",
            "mode_specifique": "audio"
        },
        
        {
            "question": "Comment appeler une méthode 'sayHello' d'un objet person1 ?",
            "options": '{"A": "person1.sayHello", "B": "person1.sayHello()", "C": "sayHello(person1)", "D": "person1(sayHello)"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "Pour appeler une méthode, on utilise les parenthèses.",
            "mode_specifique": "video"
        },
        {
            "question": "Que signifie 'this' à l'intérieur d'une méthode d'objet ?",
            "options": '{"A": "L\'objet global", "B": "L\'objet courant", "C": "La fonction parente", "D": "Une variable locale"}',
            "reponse_correcte": "B",
            "points": 15,
            "difficulte": "moyen",
            "explication": "'this' fait référence à l'objet courant.",
            "mode_specifique": "video"
        },
        {
            "question": "Comment ajouter une nouvelle propriété à un objet existant ?",
            "options": '{"A": "object.add(property, value)", "B": "object.property = value", "C": "object[property] = value", "D": "Les réponses B et C"}',
            "reponse_correcte": "D",
            "points": 10,
            "difficulte": "facile",
            "explication": "On peut utiliser la notation pointée ou crochets.",
            "mode_specifique": "video"
        },
        {
            "question": "Les objets peuvent-ils contenir d'autres objets ?",
            "options": '{"A": "Oui", "B": "Non", "C": "Seulement avec des tableaux", "D": "Uniquement en mode strict"}',
            "reponse_correcte": "A",
            "points": 10,
            "difficulte": "facile",
            "explication": "Oui, les objets peuvent contenir d'autres objets (propriétés imbriquées).",
            "mode_specifique": "video"
        },
        {
            "question": "Quelle est la différence entre une propriété et une méthode ?",
            "options": '{"A": "Une propriété est une donnée, une méthode est une action", "B": "Il n\'y a pas de différence", "C": "Une propriété est une fonction", "D": "Une méthode est une variable"}',
            "reponse_correcte": "A",
            "points": 10,
            "difficulte": "facile",
            "explication": "Les propriétés stockent des données, les méthodes définissent des actions.",
            "mode_specifique": "video"
        },
        {
            "question": "Comment supprimer une propriété d'un objet ?",
            "options": '{"A": "object.remove(\'property\')", "B": "delete object.property", "C": "object.property = null", "D": "object.delete(\'property\')"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "L'opérateur delete supprime une propriété.",
            "mode_specifique": "video"
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
                VALUES (%s, %s, 'choix_multiple', %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            """, (
                cours_id, q["question"], q["points"], q["difficulte"],
                q["options"], q["reponse_correcte"], q["explication"],
                q["mode_specifique"], admin_id
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
    
    print(f"\n📊 RÉSUMÉ: {questions_creees} questions créées, {questions_existantes} existantes")
    return True

def main():
    print("\n" + "=" * 60)
    print("🎓 INSERTION DU COURS: JAVASCRIPT OBJECTS")
    print("=" * 60)
    
    conn = get_connection()
    if not conn:
        print("❌ Impossible de se connecter à la base de données")
        return
    
    conn.close()
    print("✅ Connexion à la base de données établie")
    
    cours_id = inserer_cours_javascript_objects()
    
    if cours_id:
        inserer_questions_javascript_objects(cours_id)
        print(f"\n🎉 Succès ! Cours créé (ID: {cours_id})")
    else:
        print("\n❌ Échec de l'insertion")

if __name__ == "__main__":
    main()