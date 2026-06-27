
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

def inserer_cours_javascript_data_types():
    
    
    admin_id = get_admin_user()
    if not admin_id:
        print("❌ Impossible de trouver un utilisateur")
        return False
    
    chapitre_id = get_chapitre_id()
    
    conn = get_connection()
    if not conn:
        return False
    
    cur = conn.cursor()
    
    slug_cours = "javascript-data-types"
    
    cur.execute("SELECT id FROM cours_html WHERE slug = %s", (slug_cours,))
    existing = cur.fetchone()
    
    contenu_html = """
    <h1>🔢 JavaScript Data Types - Les Types de Données</h1>
    
    <div class="info-box">
        <p><strong>💡 À savoir :</strong> JavaScript possède sept types de données fondamentaux : Boolean, Null, Undefined, Number, String, Symbol et Object.</p>
    </div>
    
    <h2>Types de données en JavaScript</h2>
    <p>JavaScript distingue différents types de données qui déterminent comment les valeurs peuvent être manipulées.</p>
    
    <h2>1. Boolean (booléen)</h2>
    <p>Représente une valeur logique : vrai ou faux (true/false).</p>
    
    <pre><code>let isActive = true;
let isLogged = false;

if (isActive) {
    console.log("L'utilisateur est actif");
}</code></pre>
    
    <h2>2. Null (nul)</h2>
    <p>Représente une valeur vide ou inexistante. C'est une valeur d'assignation signifiant "aucune valeur".</p>
    
    <pre><code>let emptyValue = null;
console.log(emptyValue); // null
console.log(null + 5); // 5 (null se comporte comme 0 en math)</code></pre>
    
    <div class="info-box">
        <p><strong>📝 Note :</strong> Null est un type à part entière en JavaScript. Il est différent de undefined.</p>
    </div>
    
    <h2>3. Undefined (indéfini)</h2>
    <p>Une variable déclarée mais non assignée a la valeur undefined.</p>
    
    <pre><code>let declaredVariable;
console.log(declaredVariable); // undefined
console.log(undefined + 5); // NaN (Not a Number)</code></pre>
    
    <div class="warning-box">
        <p><strong>⚠️ Important :</strong> Une variable déclarée sans valeur est undefined. Les opérations mathématiques avec undefined donnent NaN.</p>
    </div>
    
    <h2>4. Number (nombre)</h2>
    <p>Représente les nombres entiers et décimaux.</p>
    
    <pre><code>let integer = 42;
let decimal = 3.14;
let result = 3.6 + 6.4; // 10

console.log(typeof integer); // "number"
console.log(typeof decimal); // "number"</code></pre>
    
    <h2>5. String (chaîne de caractères)</h2>
    <p>Représente du texte entre guillemets simples ou doubles.</p>
    
    <pre><code>let firstName = "John";
let lastName = 'Doe';
let fullName = firstName + " " + lastName; // "John Doe"

console.log(typeof firstName); // "string"</code></pre>
    
    <h2>6. Symbol (symbole) - ES6</h2>
    <p>Identifiant unique et immuable. Deux symboles avec la même description ne sont pas égaux.</p>
    
    <pre><code>let sym1 = Symbol("id");
let sym2 = Symbol("id");
console.log(sym1 === sym2); // false

console.log(String(sym1)); // "Symbol(id)"</code></pre>
    
    <div class="tip-box">
        <p><strong>💡 Astuce :</strong> Les Symboles sont parfaits pour créer des identifiants uniques dans vos objets.</p>
    </div>
    
    <h2>7. Object (objet)</h2>
    <p>Collection de paires clé-valeur. Permet de structurer des données complexes.</p>
    
    <pre><code>let myCar = {
    make: "Ford",
    model: "Mustang",
    year: 2020
};

console.log(myCar.make); // "Ford"
console.log(myCar["model"]); // "Mustang"

// Ajouter une propriété
myCar.color = "red";</code></pre>
    
    <h2>Tableau récapitulatif</h2>
    
    <table border="1" style="border-collapse: collapse; width: 100%;">
        <thead style="background-color: #f2f2f2;">
            <th style="padding: 8px; text-align: left;">Type</th>
            <th style="padding: 8px; text-align: left;">Description</th>
            <th style="padding: 8px; text-align: left;">Exemple</th>
        </thead>
        <tbody>
            <tr><td style="padding: 8px;">Boolean</td><td style="padding: 8px;">Vrai ou faux</td><td style="padding: 8px;"><code>let x = true;</code></td></tr>
            <tr><td style="padding: 8px;">Null</td><td style="padding: 8px;">Valeur nulle</td><td style="padding: 8px;"><code>let x = null;</code></td></tr>
            <tr><td style="padding: 8px;">Undefined</td><td style="padding: 8px;">Non définie</td><td style="padding: 8px;"><code>let x;</code></td></tr>
            <tr><td style="padding: 8px;">Number</td><td style="padding: 8px;">Nombre</td><td style="padding: 8px;"><code>let x = 42;</code></td></tr>
            <tr><td style="padding: 8px;">String</td><td style="padding: 8px;">Texte</td><td style="padding: 8px;"><code>let x = "Hello";</code></td></tr>
            <tr><td style="padding: 8px;">Symbol</td><td style="padding: 8px;">Identifiant unique</td><td style="padding: 8px;"><code>let x = Symbol();</code></td></tr>
            <tr><td style="padding: 8px;">Object</td><td style="padding: 8px;">Collection de paires clé-valeur</td><td style="padding: 8px;"><code>let x = {key: "value"};</code></td></tr>
        </tbody>
    </table>
    
    <h2>Exemple complet</h2>
    
    <pre><code>&lt;!DOCTYPE html&gt;
&lt;html&gt;
&lt;body&gt;
    &lt;h2&gt;Démonstration des Types de Données JavaScript&lt;/h2&gt;
    &lt;p id="demo"&gt;&lt;/p&gt;
    
    &lt;script&gt;
        // Boolean
        let isJavaScriptFun = true;
        
        // Null
        let empty = null;
        
        // Undefined
        let notAssigned;
        
        // Number
        let score = 100;
        let average = 85.5;
        let sum = 3.6 + 6.4;
        
        // String
        let message = "JavaScript Data Types";
        
        // Symbol
        let id1 = Symbol("id");
        let id2 = Symbol("id");
        
        // Object
        let person = {
            name: "Alice",
            age: 25,
            city: "Paris"
        };
        
        // Affichage
        let output = "&lt;strong&gt;Types de données :&lt;/strong&gt;&lt;br&gt;";
        output += "Boolean : " + isJavaScriptFun + "&lt;br&gt;";
        output += "Null : " + empty + "&lt;br&gt;";
        output += "Undefined : " + notAssigned + "&lt;br&gt;";
        output += "Number : score = " + score + ", average = " + average + "&lt;br&gt;";
        output += "String : " + message + "&lt;br&gt;";
        output += "Symbols : id1 == id2 ? " + (id1 === id2) + "&lt;br&gt;";
        output += "Object : " + person.name + " a " + person.age + " ans";
        
        document.getElementById("demo").innerHTML = output;
    &lt;/script&gt;
&lt;/body&gt;
&lt;/html&gt;</code></pre>
    
    <div class="info-box">
        <p><strong>💡 À retenir :</strong> JavaScript est un langage à typage dynamique. Une variable peut changer de type au cours de l'exécution.</p>
    </div>
    """.strip()
    
    cours_data = {
        "titre": "JavaScript Data Types - Types de Données",
        "slug": slug_cours,
        "description": "Apprenez les 7 types de données fondamentaux en JavaScript : Boolean, Null, Undefined, Number, String, Symbol et Object. Découvrez comment chaque type se comporte et les différences entre null et undefined.",
        "contenu_texte": contenu_html,
        "difficulte": "debutant",
        "duree_estimee": 25,
        "ordre_affichage": 3,
        "chapitre_id": chapitre_id,
        "tags": ["javascript", "data-types", "boolean", "null", "undefined", "number", "string", "symbol", "object", "debutant"],
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

def inserer_questions_javascript_data_types(cours_id):
    
    
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
            "question": "Quel type de données représente une valeur logique (vrai/faux) en JavaScript ?",
            "options": '{"A": "Number", "B": "String", "C": "Boolean", "D": "Object"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "Boolean représente les valeurs true (vrai) et false (faux).",
            "mode_specifique": "texte"
        },
        {
            "question": "Que se passe-t-il quand on utilise undefined dans une opération mathématique ?",
            "options": '{"A": "0", "B": "undefined", "C": "NaN", "D": "Erreur"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "undefined + 5 donne NaN (Not a Number).",
            "mode_specifique": "texte"
        },
        
        
        {
            "question": "Quelle est la différence entre null et undefined ?",
            "options": '{"A": "C\'est la même chose", "B": "null est une valeur assignée, undefined est une variable non assignée", "C": "undefined est une valeur assignée, null est non assigné", "D": "null est pour les nombres, undefined pour les textes"}',
            "reponse_correcte": "B",
            "points": 15,
            "difficulte": "moyen",
            "explication": "null est une valeur assignée signifiant 'aucune valeur', undefined signifie qu'une variable a été déclarée mais pas assignée.",
            "mode_specifique": "audio"
        },
        {
            "question": "Quel type de données représente du texte en JavaScript ?",
            "options": '{"A": "Number", "B": "String", "C": "Boolean", "D": "Symbol"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "String représente les chaînes de caractères (texte).",
            "mode_specifique": "audio"
        },
        {
            "question": "Quel type de données permet de créer des identifiants uniques en JavaScript ?",
            "options": '{"A": "Number", "B": "String", "C": "Object", "D": "Symbol"}',
            "reponse_correcte": "D",
            "points": 15,
            "difficulte": "moyen",
            "explication": "Symbol est un type introduit en ES6 pour créer des identifiants uniques et immuables.",
            "mode_specifique": "audio"
        },
        
        
        {
            "question": "Combien y a-t-il de types de données fondamentaux en JavaScript ?",
            "options": '{"A": "5", "B": "6", "C": "7", "D": "8"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "Il y a 7 types : Boolean, Null, Undefined, Number, String, Symbol, Object.",
            "mode_specifique": "video"
        },
        {
            "question": "Quel type de données est utilisé pour stocker des collections de paires clé-valeur ?",
            "options": '{"A": "Array", "B": "Object", "C": "String", "D": "Number"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "Object permet de stocker des données sous forme de paires clé-valeur.",
            "mode_specifique": "video"
        },
        {
            "question": "Deux symboles créés avec la même description sont-ils égaux ?",
            "options": '{"A": "Oui", "B": "Non", "C": "Dépend du navigateur", "D": "Seulement en mode strict"}',
            "reponse_correcte": "B",
            "points": 15,
            "difficulte": "moyen",
            "explication": "Deux symboles avec la même description ne sont pas égaux car chaque symbole est unique.",
            "mode_specifique": "video"
        },
        {
            "question": "Que donne null + 5 en JavaScript ?",
            "options": '{"A": "null5", "B": "5", "C": "NaN", "D": "Erreur"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "null se comporte comme 0 dans les opérations mathématiques, donc null + 5 = 5.",
            "mode_specifique": "video"
        },
        {
            "question": "Quelle est la valeur d'une variable déclarée mais non assignée ?",
            "options": '{"A": "null", "B": "0", "C": "undefined", "D": "NaN"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "Une variable déclarée mais non assignée a la valeur undefined.",
            "mode_specifique": "video"
        },
        {
            "question": "Quel opérateur permet de connaître le type d'une variable en JavaScript ?",
            "options": '{"A": "type()", "B": "typeof", "C": "getType()", "D": "instanceof"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "typeof est l'opérateur qui retourne le type d'une variable.",
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
            print(f"     Question: {q['question']}")
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
    print("🎓 INSERTION DU COURS: JAVASCRIPT DATA TYPES")
    print("=" * 60)
    
    
    conn = get_connection()
    if not conn:
        print("❌ Impossible de se connecter à la base de données")
        return
    
    conn.close()
    print("✅ Connexion à la base de données établie")
    
    
    cours_id = inserer_cours_javascript_data_types()
    
    if cours_id:
        inserer_questions_javascript_data_types(cours_id)
        print(f"\n🎉 Succès ! Cours 'JavaScript Data Types - Types de Données' créé (ID: {cours_id})")
    else:
        print("\n❌ Échec de l'insertion")

if __name__ == "__main__":
    main()