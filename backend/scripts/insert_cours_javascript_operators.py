
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

def inserer_cours_javascript_operators():
    
    
    admin_id = get_admin_user()
    if not admin_id:
        print("❌ Impossible de trouver un utilisateur")
        return False
    
    chapitre_id = get_chapitre_id()
    
    conn = get_connection()
    if not conn:
        return False
    
    cur = conn.cursor()
    
    slug_cours = "javascript-operators"
    
    cur.execute("SELECT id FROM cours_html WHERE slug = %s", (slug_cours,))
    existing = cur.fetchone()
    
    contenu_html = """
    <h1>➕ JavaScript Operators - Les Opérateurs</h1>
    
    <div class="info-box">
        <p><strong>💡 À savoir :</strong> Les opérateurs en JavaScript permettent d'effectuer des calculs mathématiques, des comparaisons et des opérations logiques.</p>
    </div>
    
    <h2>Types d'opérateurs en JavaScript</h2>
    <p>Il existe plusieurs types d'opérateurs :</p>
    <ul>
        <li>Opérateurs arithmétiques</li>
        <li>Opérateurs d'assignation</li>
        <li>Opérateurs de comparaison</li>
        <li>Opérateurs logiques</li>
    </ul>
    
    <h2>1. L'opérateur d'assignation (=)</h2>
    <p>L'opérateur d'assignation <code>=</code> assigne une valeur à une variable.</p>
    
    <pre><code>let x = 10;      // assigne 10 à x
let message = "Bonjour";  // assigne "Bonjour" à message</code></pre>
    
    <h2>2. Opérateurs arithmétiques</h2>
    <p>Les opérateurs arithmétiques effectuent des calculs sur des nombres.</p>
    
    <table border="1" style="border-collapse: collapse; width: 100%;">
        <thead style="background-color: #f2f2f2;">
            <th style="padding: 8px; text-align: left;">Opérateur</th>
            <th style="padding: 8px; text-align: left;">Description</th>
            <th style="padding: 8px; text-align: left;">Exemple</th>
        </thead>
        <tbody>
            <tr><td style="padding: 8px;">+</td><td style="padding: 8px;">Addition</td><td style="padding: 8px;">5 + 5 = 10</td></tr>
            <tr><td style="padding: 8px;">-</td><td style="padding: 8px;">Soustraction</td><td style="padding: 8px;">10 - 3 = 7</td></tr>
            <tr><td style="padding: 8px;">*</td><td style="padding: 8px;">Multiplication</td><td style="padding: 8px;">4 * 5 = 20</td></tr>
            <tr><td style="padding: 8px;">**</td><td style="padding: 8px;">Exponentiation</td><td style="padding: 8px;">2 ** 3 = 8</td></tr>
            <tr><td style="padding: 8px;">/</td><td style="padding: 8px;">Division</td><td style="padding: 8px;">20 / 5 = 4</td></tr>
            <tr><td style="padding: 8px;">%</td><td style="padding: 8px;">Modulo (reste)</td><td style="padding: 8px;">10 % 3 = 1</td></tr>
            <tr><td style="padding: 8px;">++</td><td style="padding: 8px;">Incrémentation</td><td style="padding: 8px;">x++</td></tr>
            <tr><td style="padding: 8px;">--</td><td style="padding: 8px;">Décrémentation</td><td style="padding: 8px;">x--</td></tr>
        </tbody>
    </table>
    
    <h3>Exemples :</h3>
    <pre><code>let sum = 5 + 10;        // 15
let product = 4 * 3;     // 12
let remainder = 10 % 3;  // 1
let power = 2 ** 4;      // 16</code></pre>
    
    <h2>3. Opérateurs d'assignation composés</h2>
    
    <table border="1" style="border-collapse: collapse; width: 100%;">
        <thead style="background-color: #f2f2f2;">
            <th style="padding: 8px; text-align: left;">Opérateur</th>
            <th style="padding: 8px; text-align: left;">Exemple</th>
            <th style="padding: 8px; text-align: left;">Équivalent</th>
        </thead>
        <tbody>
            <tr><td style="padding: 8px;">+=</td><td style="padding: 8px;">x += 5</td><td style="padding: 8px;">x = x + 5</td></tr>
            <tr><td style="padding: 8px;">-=</td><td style="padding: 8px;">x -= 3</td><td style="padding: 8px;">x = x - 3</td></tr>
            <tr><td style="padding: 8px;">*=</td><td style="padding: 8px;">x *= 2</td><td style="padding: 8px;">x = x * 2</td></tr>
            <tr><td style="padding: 8px;">/=</td><td style="padding: 8px;">x /= 4</td><td style="padding: 8px;">x = x / 4</td></tr>
            <tr><td style="padding: 8px;">%=</td><td style="padding: 8px;">x %= 3</td><td style="padding: 8px;">x = x % 3</td></tr>
            <tr><td style="padding: 8px;">**=</td><td style="padding: 8px;">x **= 2</td><td style="padding: 8px;">x = x ** 2</td></tr>
        </tbody>
    </table>
    
    <h2>4. Opérateurs de comparaison</h2>
    <p>Les opérateurs de comparaison comparent deux valeurs et retournent true ou false.</p>
    
    <table border="1" style="border-collapse: collapse; width: 100%;">
        <thead style="background-color: #f2f2f2;">
            <th style="padding: 8px; text-align: left;">Opérateur</th>
            <th style="padding: 8px; text-align: left;">Description</th>
            <th style="padding: 8px; text-align: left;">Exemple</th>
        </thead>
        <tbody>
            <tr><td style="padding: 8px;">==</td><td style="padding: 8px;">Égal en valeur</td><td style="padding: 8px;">5 == "5" → true</td></tr>
            <tr><td style="padding: 8px;">===</td><td style="padding: 8px;">Égal en valeur et type</td><td style="padding: 8px;">5 === "5" → false</td></tr>
            <tr><td style="padding: 8px;">!=</td><td style="padding: 8px;">Différent en valeur</td><td style="padding: 8px;">5 != "5" → false</td></tr>
            <tr><td style="padding: 8px;">!==</td><td style="padding: 8px;">Différent en valeur ou type</td><td style="padding: 8px;">5 !== "5" → true</td></tr>
            <tr><td style="padding: 8px;">></td><td style="padding: 8px;">Plus grand que</td><td style="padding: 8px;">10 > 5 → true</td></tr>
            <tr><td style="padding: 8px;"><</td><td style="padding: 8px;">Plus petit que</td><td style="padding: 8px;">3 < 8 → true</td></tr>
            <tr><td style="padding: 8px;">>=</td><td style="padding: 8px;">Plus grand ou égal</td><td style="padding: 8px;">5 >= 5 → true</td></tr>
            <tr><td style="padding: 8px;"><=</td><td style="padding: 8px;">Plus petit ou égal</td><td style="padding: 8px;">4 <= 5 → true</td></tr>
        </tbody>
    </table>
    
    <h2>5. Opérateurs logiques</h2>
    
    <table border="1" style="border-collapse: collapse; width: 100%;">
        <thead style="background-color: #f2f2f2;">
            <th style="padding: 8px; text-align: left;">Opérateur</th>
            <th style="padding: 8px; text-align: left;">Description</th>
            <th style="padding: 8px; text-align: left;">Exemple</th>
        </thead>
        <tbody>
            <tr><td style="padding: 8px;">&&</td><td style="padding: 8px;">ET logique</td><td style="padding: 8px;">(5 > 3 && 2 < 4) → true</td></tr>
            <tr><td style="padding: 8px;">||</td><td style="padding: 8px;">OU logique</td><td style="padding: 8px;">(5 > 10 || 3 < 4) → true</td></tr>
            <tr><td style="padding: 8px;">!</td><td style="padding: 8px;">NON logique</td><td style="padding: 8px;">!(5 > 3) → false</td></tr>
        </tbody>
    </table>
    
    <h2>6. Concaténation de chaînes</h2>
    <p>L'opérateur <code>+</code> peut aussi concaténer des chaînes de caractères.</p>
    
    <pre><code>let firstName = "John";
let lastName = "Doe";
let fullName = firstName + " " + lastName;  // "John Doe"</code></pre>
    
    <h3>Addition vs Concaténation</h3>
    <pre><code>let result1 = 5 + 5;      // 10 (nombre)
let result2 = "5" + 5;    // "55" (string, concaténation)
let result3 = "Hello" + 5; // "Hello5"</code></pre>
    
    <h2>7. Exemple complet</h2>
    
    <pre><code>&lt;!DOCTYPE html&gt;
&lt;html&gt;
&lt;body&gt;
    &lt;h2&gt;Démonstration des Opérateurs JavaScript&lt;/h2&gt;
    &lt;p id="demo"&gt;&lt;/p&gt;
    
    &lt;script&gt;
        // Arithmétique
        let a = 10, b = 3;
        let addition = a + b;
        let soustraction = a - b;
        let multiplication = a * b;
        let division = a / b;
        let modulo = a % b;
        
        // Assignation composée
        let x = 5;
        x += 3;  // x devient 8
        
        // Comparaison
        let estPlusGrand = a > b;  // true
        
        // Logique
        let estVrai = (a > 5 && b < 5);  // true && true = true
        
        // Concaténation
        let message = "Le résultat de " + a + " + " + b + " = " + addition;
        
        let output = "&lt;strong&gt;Opérateurs arithmétiques :&lt;/strong&gt;&lt;br&gt;";
        output += a + " + " + b + " = " + addition + "&lt;br&gt;";
        output += a + " - " + b + " = " + soustraction + "&lt;br&gt;";
        output += a + " * " + b + " = " + multiplication + "&lt;br&gt;";
        output += a + " / " + b + " = " + division + "&lt;br&gt;";
        output += a + " % " + b + " = " + modulo + "&lt;br&gt;&lt;br&gt;";
        output += "x += 3 → x = " + x + "&lt;br&gt;&lt;br&gt;";
        output += "a > b : " + estPlusGrand + "&lt;br&gt;";
        output += "(a > 5 && b < 5) : " + estVrai + "&lt;br&gt;&lt;br&gt;";
        output += message;
        
        document.getElementById("demo").innerHTML = output;
    &lt;/script&gt;
&lt;/body&gt;
&lt;/html&gt;</code></pre>
    
    <div class="info-box">
        <p><strong>💡 À retenir :</strong> Les opérateurs sont essentiels pour manipuler les données. <code>===</code> est préféré à <code>==</code> pour éviter les conversions de type implicites.</p>
    </div>
    """.strip()
    
    cours_data = {
        "titre": "JavaScript Operators - Les Opérateurs",
        "slug": slug_cours,
        "description": "Apprenez à utiliser les opérateurs JavaScript : opérateurs arithmétiques (+, -, *, /, %, **), d'assignation (=, +=, -=), de comparaison (==, ===, !=, !==, >, <) et logiques (&&, ||, !). Découvrez la concaténation de chaînes et la différence entre addition et concaténation.",
        "contenu_texte": contenu_html,
        "difficulte": "debutant",
        "duree_estimee": 20,
        "ordre_affichage": 4,
        "chapitre_id": chapitre_id,
        "tags": ["javascript", "operators", "arithmetic", "assignment", "comparison", "logical", "concatenation", "debutant"],
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

def inserer_questions_javascript_operators(cours_id):
    
    
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
            "question": "Quel opérateur JavaScript est utilisé pour l'assignation ?",
            "options": '{"A": "==", "B": "===", "C": "=", "D": "!="}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "L'opérateur = assigne une valeur à une variable.",
            "mode_specifique": "texte"
        },
        {
            "question": "Que signifie l'opérateur % en JavaScript ?",
            "options": '{"A": "Pourcentage", "B": "Modulo (reste de division)", "C": "Division", "D": "Multiplication"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "% est l'opérateur modulo qui retourne le reste d'une division.",
            "mode_specifique": "texte"
        },
        
        
        {
            "question": "Que fait l'opérateur += ?",
            "options": '{"A": "Compare si égal", "B": "Ajoute et assigne", "C": "Multiplie et assigne", "D": "Soustrait et assigne"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "x += y équivaut à x = x + y.",
            "mode_specifique": "audio"
        },
        {
            "question": "Quel opérateur est utilisé pour la concaténation de chaînes ?",
            "options": '{"A": "&", "B": "||", "C": "+", "D": ","}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "L'opérateur + concatène les chaînes en JavaScript.",
            "mode_specifique": "audio"
        },
        {
            "question": "Que retourne 5 === '5' en JavaScript ?",
            "options": '{"A": "true", "B": "false", "C": "undefined", "D": "Erreur"}',
            "reponse_correcte": "B",
            "points": 15,
            "difficulte": "moyen",
            "explication": "=== vérifie l'égalité en valeur ET en type. 5 (number) === '5' (string) donne false.",
            "mode_specifique": "audio"
        },
        
        
        {
            "question": "Quel est le résultat de 5 + '5' en JavaScript ?",
            "options": '{"A": "10", "B": "55", "C": "Erreur", "D": "undefined"}',
            "reponse_correcte": "B",
            "points": 15,
            "difficulte": "moyen",
            "explication": "Lorsqu'on ajoute un nombre et une chaîne, JavaScript convertit le nombre en chaîne et concatène.",
            "mode_specifique": "video"
        },
        {
            "question": "Quel opérateur logique représente le ET ?",
            "options": '{"A": "||", "B": "&&", "C": "!", "D": "&"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "&& est l'opérateur ET logique, true uniquement si les deux opérandes sont true.",
            "mode_specifique": "video"
        },
        {
            "question": "Que signifie l'opérateur ** en JavaScript ?",
            "options": '{"A": "Multiplication", "B": "Exponentiation", "C": "Concaténation", "D": "Comparaison"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "** est l'opérateur d'exponentiation. 2 ** 3 = 8.",
            "mode_specifique": "video"
        },
        {
            "question": "Que fait l'opérateur ++ ?",
            "options": '{"A": "Incrémente de 1", "B": "Décrémente de 1", "C": "Multiplie par 2", "D": "Divise par 2"}',
            "reponse_correcte": "A",
            "points": 10,
            "difficulte": "facile",
            "explication": "L'opérateur ++ incrémente une variable de 1.",
            "mode_specifique": "video"
        },
        {
            "question": "Quelle est la différence entre == et === ?",
            "options": '{"A": "Aucune différence", "B": "== compare la valeur, === compare la valeur et le type", "C": "=== compare uniquement le type", "D": "== est plus rapide"}',
            "reponse_correcte": "B",
            "points": 15,
            "difficulte": "moyen",
            "explication": "== compare uniquement la valeur (avec conversion), === compare la valeur ET le type.",
            "mode_specifique": "video"
        },
        {
            "question": "Que retourne 10 > 5 && 3 < 2 ?",
            "options": '{"A": "true", "B": "false", "C": "undefined", "D": "Erreur"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "10 > 5 est true, 3 < 2 est false, donc true && false = false.",
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
    print("🎓 INSERTION DU COURS: JAVASCRIPT OPERATORS")
    print("=" * 60)
    
    
    conn = get_connection()
    if not conn:
        print("❌ Impossible de se connecter à la base de données")
        return
    
    conn.close()
    print("✅ Connexion à la base de données établie")
    
    
    cours_id = inserer_cours_javascript_operators()
    
    if cours_id:
        inserer_questions_javascript_operators(cours_id)
        print(f"\n🎉 Succès ! Cours 'JavaScript Operators - Les Opérateurs' créé (ID: {cours_id})")
    else:
        print("\n❌ Échec de l'insertion")

if __name__ == "__main__":
    main()