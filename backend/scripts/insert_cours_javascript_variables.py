
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

def inserer_cours_javascript_variables():
    
    
    admin_id = get_admin_user()
    if not admin_id:
        print("❌ Impossible de trouver un utilisateur")
        return False
    
    chapitre_id = get_chapitre_id()
    
    conn = get_connection()
    if not conn:
        return False
    
    cur = conn.cursor()
    
    slug_cours = "javascript-variables"
    
    cur.execute("SELECT id FROM cours_html WHERE slug = %s", (slug_cours,))
    existing = cur.fetchone()
    
    contenu_html = """
    <h1>📦 JavaScript Variables - Les Variables</h1>
    
    <div class="info-box">
        <p><strong>💡 À savoir :</strong> Les variables sont des conteneurs qui permettent de stocker des données en mémoire. Elles sont essentielles en programmation.</p>
    </div>
    
    <h2>Qu'est-ce qu'une variable ?</h2>
    <p>Une variable est un conteneur qui stocke une valeur. On peut imaginer une variable comme une boîte dans laquelle on met une valeur.</p>
    
    <pre><code>// Déclaration de variables
let goldCoins = 5;
let diamonds = 6;
let pizzaCoupons = 0;</code></pre>
    
    <h2>1. Déclarer des variables</h2>
    <p>Il existe trois façons de déclarer une variable en JavaScript :</p>
    
    <ul>
        <li><strong>var</strong> : Ancienne méthode (à éviter)</li>
        <li><strong>let</strong> : Variable dont la valeur peut changer</li>
        <li><strong>const</strong> : Variable dont la valeur ne peut pas changer (constante)</li>
    </ul>
    
    <pre><code>// let - valeur modifiable
let age = 25;
age = 26;  // OK

// const - valeur non modifiable
const birthYear = 1995;
birthYear = 1996;  // ERREUR !

// var - ancienne méthode (à éviter)
var oldWay = "déprécié";</code></pre>
    
    <div class="tip-box">
        <p><strong>💡 Bonne pratique :</strong> Utilisez <code>const</code> par défaut. Utilisez <code>let</code> uniquement si la valeur doit changer. Évitez <code>var</code>.</p>
    </div>
    
    <h2>2. Règles de nommage (identifiants)</h2>
    
    <ul>
        <li>Peut contenir des lettres, chiffres, $ et _</li>
        <li>Doit commencer par une lettre, $ ou _ (pas un chiffre)</li>
        <li>Pas de mots réservés comme let, const, if, for, etc.</li>
        <li>Respecte la casse : <code>carName</code> ≠ <code>carname</code></li>
    </ul>
    
    <pre><code>// Noms valides
let firstName = "Jean";
let _private = "privé";
let $dollar = 100;
let age2 = 25;

// Noms invalides
// let 2age = 25;     // Ne peut pas commencer par un chiffre
// let my-name = "test";  // Le tiret n'est pas autorisé
// let let = "mot réservé";  // Mot réservé</code></pre>
    
    <h2>3. L'opérateur d'assignation (=)</h2>
    <p>Le signe <code>=</code> assigne une valeur à une variable. Ce n'est pas un signe d'égalité mathématique.</p>
    
    <pre><code>let x = 5;      // x vaut 5
x = x + 3;      // x vaut maintenant 8 (5 + 3)

let y = 10;
y += 5;         // y vaut 15 (équivaut à y = y + 5)</code></pre>
    
    <h2>4. Types de données</h2>
    
    <ul>
        <li><strong>Numbers</strong> : Nombres, écrits sans guillemets</li>
        <li><strong>Strings</strong> : Texte, entre guillemets simples ou doubles</li>
        <li><strong>Booleans</strong> : true ou false</li>
    </ul>
    
    <pre><code>let number = 42;           // Number
let text = "Hello";        // String
let isActive = true;       // Boolean</code></pre>
    
    <h3>Attention : Addition vs Concaténation</h3>
    <pre><code>let a = 5 + 10;      // 15 (addition)
let b = "5" + 10;    // "510" (concaténation - string + nombre)
let c = "Hello" + 5; // "Hello5"</code></pre>
    
    <h2>5. Exemple complet</h2>
    
    <pre><code>&lt;!DOCTYPE html&gt;
&lt;html&gt;
&lt;body&gt;
    &lt;h2&gt;Démonstration des Variables JavaScript&lt;/h2&gt;
    
    &lt;p id="demo"&gt;&lt;/p&gt;
    
    &lt;script&gt;
        // Déclaration de variables
        const playerName = "Alice";
        let score = 0;
        let level = 1;
        
        // Calcul du score
        score = 100 + 50;
        
        // Message
        let message = "Joueur: " + playerName + "<br>";
        message += "Score: " + score + "<br>";
        message += "Niveau: " + level;
        
        // Affichage
        document.getElementById("demo").innerHTML = message;
        
        // Modification d'une variable let
        level = 2;
        console.log("Nouveau niveau: " + level);
        
        // Constante (ne peut pas être modifiée)
        const MAX_SCORE = 1000;
        // MAX_SCORE = 2000; // ERREUR !
    &lt;/script&gt;
&lt;/body&gt;
&lt;/html&gt;</code></pre>
    
    <h2>Résumé des mots-clés</h2>
    
    <table border="1" style="border-collapse: collapse; width: 100%;">
        <thead style="background-color: #f2f2f2;">
            <th style="padding: 8px; text-align: left;">Mot-clé</th>
            <th style="padding: 8px; text-align: left;">Modifiable</th>
            <th style="padding: 8px; text-align: left;">Quand l'utiliser</th>
        </thead>
        <tbody>
            <tr><td style="padding: 8px;"><strong>const</strong></td><td style="padding: 8px;">Non</td> <td style="padding: 8px;">Valeurs qui ne changent pas (recommandé)</td> </tr>
            <tr><td style="padding: 8px;"><strong>let</strong></td><td style="padding: 8px;">Oui</td><td style="padding: 8px;">Valeurs qui peuvent changer</td></tr>
            <tr><td style="padding: 8px;"><strong>var</strong></td><td style="padding: 8px;">Oui</td><td style="padding: 8px;">À éviter (ancienne méthode)</td></tr>
        </tbody>
    </table>
    
    <div class="info-box">
        <p><strong>💡 À retenir :</strong> Utilisez <code>const</code> par défaut. Si la valeur doit changer, utilisez <code>let</code>. Évitez <code>var</code>.</p>
    </div>
    """.strip()
    
    cours_data = {
        "titre": "JavaScript Variables - Les Variables",
        "slug": slug_cours,
        "description": "Apprenez à utiliser les variables en JavaScript : déclaration avec var, let, const, règles de nommage, types de données (nombres, chaînes), et opérateur d'assignation.",
        "contenu_texte": contenu_html,
        "difficulte": "debutant",
        "duree_estimee": 20,
        "ordre_affichage": 2,
        "chapitre_id": chapitre_id,
        "tags": ["javascript", "variables", "let", "const", "var", "data-types", "debutant"],
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

def inserer_questions_javascript_variables(cours_id):
    
    
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
            "question": "Quels sont les trois mots-clés pour déclarer des variables en JavaScript ?",
            "options": '{"A": "variable, let, const", "B": "var, let, const", "C": "var, let, constant", "D": "v, l, c"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "var, let et const sont les trois mots-clés pour déclarer des variables en JavaScript.",
            "mode_specifique": "texte"
        },
        {
            "question": "Quelle est la bonne pratique pour déclarer une variable dont la valeur ne changera pas ?",
            "options": '{"A": "var", "B": "let", "C": "const", "D": "static"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "const est utilisé pour les valeurs qui ne doivent pas changer.",
            "mode_specifique": "texte"
        },
        
        
        {
            "question": "Quel mot-clé doit-on utiliser pour une variable qui peut changer de valeur ?",
            "options": '{"A": "const", "B": "let", "C": "var", "D": "static"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "let est utilisé pour les variables dont la valeur peut changer.",
            "mode_specifique": "audio"
        },
        {
            "question": "Que signifie le signe '=' en JavaScript ?",
            "options": '{"A": "Égalité", "B": "Assignation", "C": "Comparaison", "D": "Multiplication"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "En JavaScript, '=' est l'opérateur d'assignation, pas de comparaison.",
            "mode_specifique": "audio"
        },
        {
            "question": "Quel caractère n'est PAS autorisé dans un nom de variable ?",
            "options": '{"A": "_", "B": "$", "C": "-", "D": "lettre"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "Le tiret '-' n'est pas autorisé dans les noms de variables.",
            "mode_specifique": "audio"
        },
        
        
        {
            "question": "Que se passe-t-il quand on fait '5' + 10 en JavaScript ?",
            "options": '{"A": "15", "B": "510", "C": "Erreur", "D": "undefined"}',
            "reponse_correcte": "B",
            "points": 15,
            "difficulte": "moyen",
            "explication": "'5' + 10 donne '510' (concaténation car '5' est une chaîne).",
            "mode_specifique": "video"
        },
        {
            "question": "JavaScript est-il sensible à la casse (case-sensitive) pour les noms de variables ?",
            "options": '{"A": "Oui", "B": "Non", "C": "Parfois", "D": "Seulement sur mobile"}',
            "reponse_correcte": "A",
            "points": 10,
            "difficulte": "facile",
            "explication": "JavaScript est sensible à la casse : 'carName' et 'carname' sont différents.",
            "mode_specifique": "video"
        },
        {
            "question": "Quelle est la valeur de x après l'opération x = x + 3 si x valait 5 ?",
            "options": '{"A": "5", "B": "3", "C": "8", "D": "53"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "x = x + 3 calcule 5 + 3, donc x devient 8.",
            "mode_specifique": "video"
        },
        {
            "question": "Lequel de ces noms de variable est VALIDE ?",
            "options": '{"A": "2player", "B": "player-name", "C": "player_name", "D": "player name"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "player_name est valide (le tiret bas est autorisé).",
            "mode_specifique": "video"
        },
        {
            "question": "Quel mot-clé est considéré comme déprécié et à éviter ?",
            "options": '{"A": "let", "B": "const", "C": "var", "D": "static"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "var est l'ancienne méthode à éviter. let et const sont préférés.",
            "mode_specifique": "video"
        },
        {
            "question": "Que signifie 'const' en JavaScript ?",
            "options": '{"A": "Variable modifiable", "B": "Variable non modifiable", "C": "Variable temporaire", "D": "Variable globale"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "const déclare une constante dont la valeur ne peut pas être modifiée.",
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
            print(f"     Options: {q['options']}")
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
    print("🎓 INSERTION DU COURS: JAVASCRIPT VARIABLES")
    print("=" * 60)
    
    
    conn = get_connection()
    if not conn:
        print("❌ Impossible de se connecter à la base de données")
        return
    
    conn.close()
    print("✅ Connexion à la base de données établie")
    
    
    cours_id = inserer_cours_javascript_variables()
    
    if cours_id:
        inserer_questions_javascript_variables(cours_id)
        print(f"\n🎉 Succès ! Cours 'JavaScript Variables - Les Variables' créé (ID: {cours_id})")
    else:
        print("\n❌ Échec de l'insertion")

if __name__ == "__main__":
    main()