
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

def inserer_cours_javascript_functions():
    
    
    admin_id = get_admin_user()
    if not admin_id:
        print("❌ Impossible de trouver un utilisateur")
        return False
    
    chapitre_id = get_chapitre_id()
    
    conn = get_connection()
    if not conn:
        return False
    
    cur = conn.cursor()
    
    slug_cours = "javascript-functions"
    
    cur.execute("SELECT id FROM cours_html WHERE slug = %s", (slug_cours,))
    existing = cur.fetchone()
    
    contenu_html = """
    <h1>🎯 JavaScript Functions - Les Fonctions</h1>
    
    <div class="info-box">
        <p><strong>💡 À savoir :</strong> Les fonctions sont des blocs de code réutilisables. Elles permettent d'organiser le code, d'éviter les répétitions et de créer des programmes modulaires.</p>
    </div>
    
    <h2>Qu'est-ce qu'une fonction ?</h2>
    <p>Une fonction est un bloc de code qui effectue une tâche spécifique. Elle est déclarée une fois et peut être exécutée plusieurs fois quand on en a besoin.</p>
    
    <div class="tip-box">
        <p><strong>💡 Pourquoi utiliser des fonctions ?</strong>
        <br>- Éviter la répétition de code (DRY: Don't Repeat Yourself)
        <br>- Organiser le code en blocs logiques
        <br>- Faciliter la maintenance et le débogage
        <br>- Rendre le code plus lisible</p>
    </div>
    
    <h2>1. Déclarer une fonction</h2>
    <p>On utilise le mot-clé <code>function</code> suivi du nom de la fonction, puis des parenthèses et des accolades.</p>
    
    <pre><code>// Déclaration d'une fonction simple
function direBonjour() {
    console.log("Bonjour !");
}

// Fonction pour chanter "Joyeux Anniversaire"
function chanterAnniversaire() {
    console.log("Joyeux anniversaire à toi");
    console.log("Joyeux anniversaire cher ami");
}</code></pre>
    
    <h2>2. Appeler (invoquer) une fonction</h2>
    <p>Pour exécuter une fonction, on utilise son nom suivi de parenthèses.</p>
    
    <pre><code>// Appeler la fonction
direBonjour();  // Affiche "Bonjour !"
chanterAnniversaire();  // Affiche le message d'anniversaire</code></pre>
    
    <h2>3. Paramètres et arguments</h2>
    <p>Les paramètres sont des placeholders qui permettent à la fonction de recevoir des valeurs (arguments).</p>
    
    <pre><code>// Fonction avec paramètres
function direBonjourUtilisateur(nom) {
    console.log("Bonjour " + nom + " !");
}

// Appel avec argument
direBonjourUtilisateur("Jean");  // "Bonjour Jean !"

// Fonction avec plusieurs paramètres
function messagePersonnalise(nom, age) {
    console.log(nom + " a " + age + " ans.");
}</code></pre>
    
    <h2>4. Le mot-clé return</h2>
    <p>Le mot-clé <code>return</code> permet à une fonction de renvoyer une valeur. Une fois return exécuté, la fonction s'arrête.</p>
    
    <pre><code>// Fonction qui retourne une valeur
function addition(x, y) {
    return x + y;
}

let resultat = addition(5, 3);
console.log(resultat);  // 8

// Fonction qui retourne un booléen
function estPair(nombre) {
    return nombre % 2 === 0;
}</code></pre>
    
    <h2>5. Exemples de fonctions mathématiques</h2>
    
    <pre><code>function addition(x, y) {
    return x + y;
}

function soustraction(x, y) {
    return x - y;
}

function multiplication(x, y) {
    return x * y;
}

function division(x, y) {
    return x / y;
}

console.log(addition(10, 5));      // 15
console.log(soustraction(10, 5));  // 5
console.log(multiplication(10, 5)); // 50
console.log(division(10, 5));      // 2</code></pre>
    
    <h2>6. Vérifier si un nombre est pair</h2>
    
    <pre><code>// Version avec if/else
function estPair(nombre) {
    if (nombre % 2 === 0) {
        return true;
    } else {
        return false;
    }
}

// Version avec opérateur ternaire (plus concise)
function estPair(nombre) {
    return nombre % 2 === 0 ? true : false;
}

// Version encore plus courte
function estPair(nombre) {
    return nombre % 2 === 0;
}</code></pre>
    
    <h2>7. Validation d'email</h2>
    
    <pre><code>function validerEmail(email) {
    return email.includes("@") ? true : false;
}

// Version plus courte
function validerEmail(email) {
    return email.includes("@");
}

console.log(validerEmail("user@example.com"));  // true
console.log(validerEmail("userexample.com"));   // false</code></pre>
    
    <h2>8. Expressions de fonction vs déclarations</h2>
    
    <pre><code>// Déclaration de fonction (hoisted)
function direBonjour() {
    console.log("Bonjour");
}

// Expression de fonction (non hoisted)
const direAuRevoir = function() {
    console.log("Au revoir");
};

// Fonction fléchée (Arrow function - ES6)
const multiplier = (x, y) => x * y;</code></pre>
    
    <h2>9. Exemple complet</h2>
    
    <pre><code>&lt;!DOCTYPE html&gt;
&lt;html&gt;
&lt;body&gt;
    &lt;h2&gt;Démonstration des Fonctions JavaScript&lt;/h2&gt;
    &lt;p id="demo"&gt;&lt;/p&gt;
    
    &lt;script&gt;
        // Fonctions mathématiques
        function addition(x, y) { return x + y; }
        function soustraction(x, y) { return x - y; }
        function multiplication(x, y) { return x * y; }
        function division(x, y) { return x / y; }
        
        // Fonction pair/impair
        function estPair(nombre) { return nombre % 2 === 0; }
        
        // Validation email
        function validerEmail(email) { return email.includes("@"); }
        
        // Création du message
        let output = "&lt;strong&gt;Fonctions mathématiques :&lt;/strong&gt;&lt;br&gt;";
        output += "10 + 5 = " + addition(10, 5) + "&lt;br&gt;";
        output += "10 - 5 = " + soustraction(10, 5) + "&lt;br&gt;";
        output += "10 * 5 = " + multiplication(10, 5) + "&lt;br&gt;";
        output += "10 / 5 = " + division(10, 5) + "&lt;br&gt;&lt;br&gt;";
        
        output += "&lt;strong&gt;Pair ou impair ?&lt;/strong&gt;&lt;br&gt;";
        output += "7 est pair ? " + estPair(7) + "&lt;br&gt;";
        output += "8 est pair ? " + estPair(8) + "&lt;br&gt;&lt;br&gt;";
        
        output += "&lt;strong&gt;Validation email :&lt;/strong&gt;&lt;br&gt;";
        output += "user@example.com est valide ? " + validerEmail("user@example.com") + "&lt;br&gt;";
        output += "user.example.com est valide ? " + validerEmail("user.example.com");
        
        document.getElementById("demo").innerHTML = output;
    &lt;/script&gt;
&lt;/body&gt;
&lt;/html&gt;</code></pre>
    
    <h2>Tableau récapitulatif</h2>
    
    <table border="1" style="border-collapse: collapse; width: 100%;">
        <thead style="background-color: #f2f2f2;">
            <th style="padding: 8px; text-align: left;">Concept</th>
            <th style="padding: 8px; text-align: left;">Syntaxe</th>
            <th style="padding: 8px; text-align: left;">Exemple</th>
        </thead>
        <tbody>
            <tr><td style="padding: 8px;">Déclaration</td>
                <td style="padding: 8px;"><code>function nom() { }</code></td>
                <td style="padding: 8px;"><code>function direBonjour() { }</code></td>
            </tr>
            <tr><td style="padding: 8px;">Appel</td>
                <td style="padding: 8px;"><code>nom()</code></td>
                <td style="padding: 8px;"><code>direBonjour()</code></td>
            </tr>
            <tr><td style="padding: 8px;">Paramètres</td>
                <td style="padding: 8px;"><code>function nom(param)</code></td>
                <td style="padding: 8px;"><code>function direNom(nom)</code></td>
            </tr>
            <tr><td style="padding: 8px;">Return</td>
                <td style="padding: 8px;"><code>return valeur</code></td>
                <td style="padding: 8px;"><code>return x + y</code></td>
            </tr>
            <tr><td style="padding: 8px;">Expression</td>
                <td style="padding: 8px;"><code>const f = function() { }</code></td>
                <td style="padding: 8px;"><code>const add = function(a,b) { }</code></td>
            </tr>
        </tbody>
    </table>
    
    <div class="info-box">
        <p><strong>💡 À retenir :</strong> Les fonctions sont des blocs de code réutilisables. Les paramètres permettent la flexibilité, et return permet de renvoyer des résultats.</p>
    </div>
    """.strip()
    
    cours_data = {
        "titre": "JavaScript Functions - Les Fonctions",
        "slug": slug_cours,
        "description": "Apprenez à utiliser les fonctions en JavaScript : déclaration, appel, paramètres, arguments, mot-clé return, et applications pratiques (mathématiques, validation d'email, pair/impair).",
        "contenu_texte": contenu_html,
        "difficulte": "debutant",
        "duree_estimee": 25,
        "ordre_affichage": 9,
        "chapitre_id": chapitre_id,
        "tags": ["javascript", "functions", "return", "parameters", "arguments", "debutant"],
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

def inserer_questions_javascript_functions(cours_id):
    
    
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
            "question": "Qu'est-ce qu'une fonction en JavaScript ?",
            "options": '{"A": "Un bloc de code réutilisable", "B": "Une variable spéciale", "C": "Une boucle", "D": "Un type de données"}',
            "reponse_correcte": "A",
            "points": 10,
            "difficulte": "facile",
            "explication": "Une fonction est un bloc de code réutilisable qui effectue une tâche spécifique.",
            "mode_specifique": "texte"
        },
        {
            "question": "Que fait le mot-clé 'return' dans une fonction ?",
            "options": '{"A": "Affiche une valeur", "B": "Arrête la fonction et renvoie une valeur", "C": "Déclare une variable", "D": "Crée une boucle"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "return arrête l'exécution de la fonction et renvoie une valeur à l'appelant.",
            "mode_specifique": "texte"
        },
        
        
        {
            "question": "Comment appelle-t-on une fonction en JavaScript ?",
            "options": '{"A": "functionName", "B": "functionName()", "C": "call functionName", "D": "run functionName"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "Pour appeler une fonction, on utilise son nom suivi de parenthèses.",
            "mode_specifique": "audio"
        },
        {
            "question": "Quelle est la différence entre paramètre et argument ?",
            "options": '{"A": "C\'est la même chose", "B": "Paramètre = place dans la définition, argument = valeur passée", "C": "Argument = place, paramètre = valeur", "D": "Il n\'y a pas de différence"}',
            "reponse_correcte": "B",
            "points": 15,
            "difficulte": "moyen",
            "explication": "Un paramètre est un placeholder dans la définition de la fonction. Un argument est la valeur réelle passée lors de l'appel.",
            "mode_specifique": "audio"
        },
        {
            "question": "Quel mot-clé utilise-t-on pour déclarer une fonction ?",
            "options": '{"A": "func", "B": "function", "C": "def", "D": "define"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "On utilise le mot-clé 'function' pour déclarer une fonction en JavaScript.",
            "mode_specifique": "audio"
        },
        
        
        {
            "question": "Que retourne la fonction addition(5, 3) ?",
            "options": '{"A": "53", "B": "8", "C": "2", "D": "15"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "addition(5, 3) retourne 8, car 5 + 3 = 8.",
            "mode_specifique": "video"
        },
        {
            "question": "Comment savoir si un nombre est pair en JavaScript ?",
            "options": '{"A": "nombre / 2", "B": "nombre % 2 === 0", "C": "nombre * 2", "D": "nombre - 2"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "Le modulo (%) retourne le reste. Si nombre % 2 === 0, le nombre est pair.",
            "mode_specifique": "video"
        },
        {
            "question": "Comment valider qu'un email contient le caractère '@' ?",
            "options": '{"A": "email.contains(\'@\')", "B": "email.has(\'@\')", "C": "email.includes(\'@\')", "D": "email.indexOf(\'@\')"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "includes() vérifie si une chaîne contient une sous-chaîne et retourne true ou false.",
            "mode_specifique": "video"
        },
        {
            "question": "Que fait le code 'return nombre % 2 === 0 ? true : false' ?",
            "options": '{"A": "Une boucle", "B": "Un opérateur ternaire", "C": "Une déclaration de variable", "D": "Une fonction fléchée"}',
            "reponse_correcte": "B",
            "points": 15,
            "difficulte": "moyen",
            "explication": "C'est l'opérateur ternaire, une forme raccourcie de if/else.",
            "mode_specifique": "video"
        },
        {
            "question": "Quelle est la syntaxe correcte pour une fonction fléchée ?",
            "options": '{"A": "function => (x, y) x + y", "B": "(x, y) => x + y", "C": "function(x, y) => x + y", "D": "=> (x, y) x + y"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "La syntaxe des fonctions fléchées est (paramètres) => expression.",
            "mode_specifique": "video"
        },
        {
            "question": "Une fois le mot-clé 'return' exécuté, que se passe-t-il ?",
            "options": '{"A": "La fonction continue", "B": "La fonction s\'arrête immédiatement", "C": "La fonction redémarre", "D": "Une erreur se produit"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "return arrête immédiatement l'exécution de la fonction et renvoie la valeur spécifiée.",
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
    print("🎓 INSERTION DU COURS: JAVASCRIPT FUNCTIONS")
    print("=" * 60)
    
    
    conn = get_connection()
    if not conn:
        print("❌ Impossible de se connecter à la base de données")
        return
    
    conn.close()
    print("✅ Connexion à la base de données établie")
    
    
    cours_id = inserer_cours_javascript_functions()
    
    if cours_id:
        inserer_questions_javascript_functions(cours_id)
        print(f"\n🎉 Succès ! Cours 'JavaScript Functions - Les Fonctions' créé (ID: {cours_id})")
    else:
        print("\n❌ Échec de l'insertion")

if __name__ == "__main__":
    main()