
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

def inserer_cours_javascript_conditions():
    
    
    admin_id = get_admin_user()
    if not admin_id:
        print("❌ Impossible de trouver un utilisateur")
        return False
    
    chapitre_id = get_chapitre_id()
    
    conn = get_connection()
    if not conn:
        return False
    
    cur = conn.cursor()
    
    slug_cours = "javascript-conditions"
    
    cur.execute("SELECT id FROM cours_html WHERE slug = %s", (slug_cours,))
    existing = cur.fetchone()
    
    contenu_html = """
    <h1>🤔 JavaScript Conditions - If, Else, Else If</h1>
    
    <div class="info-box">
        <p><strong>💡 À savoir :</strong> Les conditions permettent à votre programme de prendre des décisions en fonction de différentes situations. Elles sont essentielles pour créer une logique dynamique.</p>
    </div>
    
    <h2>Introduction aux Conditions</h2>
    <p>Les programmes ont souvent besoin de prendre des décisions. Les instructions conditionnelles (<code>if</code>, <code>else</code>, <code>else if</code>) permettent d'exécuter différents blocs de code selon si une condition est vraie ou fausse.</p>
    
    <div class="tip-box">
        <p><strong>💡 Booléens :</strong> Les conditions utilisent des booléens (true/false). Les opérateurs de comparaison (>, <, ==, ===, >=, <=) et logiques (&&, ||, !) retournent des booléens.</p>
    </div>
    
    <h2>1. L'instruction if</h2>
    <p>L'instruction <code>if</code> exécute un bloc de code seulement si la condition est vraie (<code>true</code>).</p>
    
    <pre><code>let age = 18;

if (age >= 18) {
    console.log("Vous êtes majeur !");
}

// Exemple avec comparaison de nombres
let x = 10;
let y = 5;

if (x > y) {
    console.log("x est plus grand que y");
}</code></pre>
    
    <h2>2. L'instruction else</h2>
    <p><code>else</code> fournit un bloc alternatif qui s'exécute si la condition du if est fausse (<code>false</code>).</p>
    
    <pre><code>let age = 16;

if (age >= 18) {
    console.log("Vous êtes majeur !");
} else {
    console.log("Vous êtes mineur !");
}

// Avec booléen
let isRaining = true;

if (isRaining) {
    console.log("Prends un parapluie !");
} else {
    console.log("Bon temps, sors !");
}</code></pre>
    
    <h2>3. L'instruction else if</h2>
    <p><code>else if</code> permet de vérifier plusieurs conditions à la suite.</p>
    
    <pre><code>let note = 85;

if (note >= 90) {
    console.log("Excellent !");
} else if (note >= 80) {
    console.log("Très bien !");
} else if (note >= 70) {
    console.log("Bien !");
} else if (note >= 60) {
    console.log("Passable");
} else {
    console.log("Échec");
}</code></pre>
    
    <h2>4. Conditions avec opérateurs logiques</h2>
    
    <h3>ET logique (&&)</h3>
    <pre><code>let age = 25;
let aPermis = true;

if (age >= 18 && aPermis) {
    console.log("Vous pouvez conduire !");
}</code></pre>
    
    <h3>OU logique (||)</h3>
    <pre><code>let jour = "samedi";

if (jour === "samedi" || jour === "dimanche") {
    console.log("C'est le weekend !");
}</code></pre>
    
    <h3>NON logique (!)</h3>
    <pre><code>let estConnecte = false;

if (!estConnecte) {
    console.log("Veuillez vous connecter.");
}</code></pre>
    
    <h2>5. Conditions imbriquées</h2>
    <p>On peut placer des conditions à l'intérieur d'autres conditions.</p>
    
    <pre><code>let age = 20;
let aPermis = true;

if (age >= 18) {
    if (aPermis) {
        console.log("Vous pouvez conduire !");
    } else {
        console.log("Vous devez passer le permis.");
    }
} else {
    console.log("Vous êtes trop jeune pour conduire.");
}</code></pre>
    
    <h2>6. L'opérateur ternaire (raccourci)</h2>
    <p>L'opérateur ternaire <code>condition ? valeur_si_vrai : valeur_si_faux</code> est une forme courte de if/else.</p>
    
    <pre><code>let age = 18;
let statut = (age >= 18) ? "Majeur" : "Mineur";
console.log(statut); // "Majeur"

// Version équivalente avec if/else
let statut2;
if (age >= 18) {
    statut2 = "Majeur";
} else {
    statut2 = "Mineur";
}</code></pre>
    
    <h2>7. Exemple complet</h2>
    
    <pre><code>&lt;!DOCTYPE html&gt;
&lt;html&gt;
&lt;body&gt;
    &lt;h2&gt;Démonstration des Conditions JavaScript&lt;/h2&gt;
    &lt;p id="demo"&gt;&lt;/p&gt;
    
    &lt;script&gt;
        let age = 20;
        let aPermis = true;
        let note = 85;
        
        let message = "&lt;strong&gt;Conditions avec if/else :&lt;/strong&gt;&lt;br&gt;";
        
        // Vérification de l'âge et du permis
        if (age >= 18 && aPermis) {
            message += "✅ Vous pouvez conduire !&lt;br&gt;";
        } else if (age >= 18 && !aPermis) {
            message += "⚠️ Vous devez passer le permis.&lt;br&gt;";
        } else {
            message += "❌ Vous êtes trop jeune.&lt;br&gt;";
        }
        
        // Système de notation avec else if
        message += "&lt;br&gt;&lt;strong&gt;Système de notation :&lt;/strong&gt;&lt;br&gt;";
        
        if (note >= 90) {
            message += "Note " + note + " : Excellent !";
        } else if (note >= 80) {
            message += "Note " + note + " : Très bien !";
        } else if (note >= 70) {
            message += "Note " + note + " : Bien !";
        } else if (note >= 60) {
            message += "Note " + note + " : Passable";
        } else {
            message += "Note " + note + " : Échec";
        }
        
        // Opérateur ternaire
        let jour = "lundi";
        let estWeekend = (jour === "samedi" || jour === "dimanche") ? "Oui" : "Non";
        message += "&lt;br&gt;&lt;br&gt;&lt;strong&gt;Weekend ?&lt;/strong&gt; " + jour + " : " + estWeekend;
        
        document.getElementById("demo").innerHTML = message;
    &lt;/script&gt;
&lt;/body&gt;
&lt;/html&gt;</code></pre>
    
    <h2>Tableau récapitulatif</h2>
    
    <table border="1" style="border-collapse: collapse; width: 100%;">
        <thead style="background-color: #f2f2f2;">
            <th style="padding: 8px; text-align: left;">Instruction</th>
            <th style="padding: 8px; text-align: left;">Quand l'utiliser</th>
            <th style="padding: 8px; text-align: left;">Exemple</th>
        </thead>
        <tbody>
            <tr><td style="padding: 8px;"><code>if</code></td>
                <td style="padding: 8px;">Une seule condition à vérifier</td>
                <td style="padding: 8px;"><code>if (x > 5) { ... }</code></td>
            </tr>
            <tr><td style="padding: 8px;"><code>if/else</code></td>
                <td style="padding: 8px;">Deux cas (vrai/faux)</td>
                <td style="padding: 8px;"><code>if (ok) { ... } else { ... }</code></td>
            </tr>
            <tr><td style="padding: 8px;"><code>if/else if/else</code></td>
                <td style="padding: 8px;">Plusieurs cas mutuellement exclusifs</td>
                <td style="padding: 8px;"><code>if (a) {...} else if (b) {...} else {...}</code></td>
            </tr>
            <tr><td style="padding: 8px;">Conditions imbriquées</td>
                <td style="padding: 8px;">Vérifications dépendantes</td>
                <td style="padding: 8px;"><code>if (a) { if (b) {...} }</code></td>
            </tr>
        </tbody>
    </table>
    
    <div class="info-box">
        <p><strong>💡 À retenir :</strong> Les conditions sont la base de la logique programmatique. <code>if</code>, <code>else if</code> et <code>else</code> vous permettent de rendre votre code intelligent et réactif.</p>
    </div>
    """.strip()
    
    cours_data = {
        "titre": "JavaScript Conditions - If, Else, Else If",
        "slug": slug_cours,
        "description": "Apprenez à utiliser les conditions en JavaScript : if, else, else if. Découvrez comment prendre des décisions dans votre code, utiliser les opérateurs de comparaison et logiques, et maîtriser les booléens.",
        "contenu_texte": contenu_html,
        "difficulte": "debutant",
        "duree_estimee": 20,
        "ordre_affichage": 5,
        "chapitre_id": chapitre_id,
        "tags": ["javascript", "conditions", "if", "else", "else if", "booleans", "comparison", "logical", "debutant"],
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

def inserer_questions_javascript_conditions(cours_id):
    
    
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
            "question": "Quelle instruction JavaScript permet d'exécuter un bloc de code si une condition est vraie ?",
            "options": '{"A": "for", "B": "while", "C": "if", "D": "switch"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "if est l'instruction conditionnelle de base qui exécute un bloc si la condition est vraie.",
            "mode_specifique": "texte"
        },
        {
            "question": "Que fait l'opérateur && en JavaScript ?",
            "options": '{"A": "OU logique", "B": "ET logique", "C": "NON logique", "D": "Assignation"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "&& est l'opérateur ET logique. Il retourne true seulement si les deux opérandes sont true.",
            "mode_specifique": "texte"
        },
        
        
        {
            "question": "Que se passe-t-il si la condition d'un if est fausse et qu'il n'y a pas de else ?",
            "options": '{"A": "Une erreur se produit", "B": "Le code continue normalement", "C": "Le programme s\'arrête", "D": "La condition devient vraie"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "Si la condition est fausse et qu'il n'y a pas de else, rien ne s'exécute et le programme continue.",
            "mode_specifique": "audio"
        },
        {
            "question": "Quel est le résultat de l'expression (5 > 3 || 2 > 10) ?",
            "options": '{"A": "true", "B": "false", "C": "undefined", "D": "Erreur"}',
            "reponse_correcte": "A",
            "points": 15,
            "difficulte": "moyen",
            "explication": "5 > 3 est true, donc l'opérateur OR (||) retourne true (la deuxième condition n'est même pas vérifiée).",
            "mode_specifique": "audio"
        },
        {
            "question": "Quelle instruction permet de vérifier plusieurs conditions à la suite ?",
            "options": '{"A": "else", "B": "else if", "C": "switch", "D": "while"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "else if permet de vérifier plusieurs conditions dans l'ordre jusqu'à ce qu'une soit vraie.",
            "mode_specifique": "audio"
        },
        
        
        {
            "question": "Que fait l'opérateur ternaire ?",
            "options": '{"A": "Une forme raccourcie de if/else", "B": "Une boucle", "C": "Une fonction", "D": "Une variable"}',
            "reponse_correcte": "A",
            "points": 15,
            "difficulte": "moyen",
            "explication": "L'opérateur ternaire (condition ? valeur_si_vrai : valeur_si_faux) est une forme concise de if/else.",
            "mode_specifique": "video"
        },
        {
            "question": "Si on a une variable age = 15, que retourne (age >= 18) ?",
            "options": '{"A": "true", "B": "false", "C": "undefined", "D": "null"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "15 >= 18 est false car 15 n'est pas supérieur ou égal à 18.",
            "mode_specifique": "video"
        },
        {
            "question": "Quelle est la bonne syntaxe pour un bloc else if ?",
            "options": '{"A": "elseif (condition) { }", "B": "else if (condition) { }", "C": "else-if (condition) { }", "D": "elif (condition) { }"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "La syntaxe correcte est 'else if (condition) { }' avec un espace entre else et if.",
            "mode_specifique": "video"
        },
        {
            "question": "Quel opérateur logique représente le NON (inverse) ?",
            "options": '{"A": "&&", "B": "||", "C": "!", "D": "=="}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "! est l'opérateur logique NOT. Il inverse la valeur d'un booléen (!true donne false).",
            "mode_specifique": "video"
        },
        {
            "question": "Que se passe-t-il si plusieurs conditions sont vraies dans une chaîne else if ?",
            "options": '{"A": "Toutes s\'exécutent", "B": "Seule la première vraie s\'exécute", "C": "Aucune ne s\'exécute", "D": "Une erreur se produit"}',
            "reponse_correcte": "B",
            "points": 15,
            "difficulte": "moyen",
            "explication": "Dès qu'une condition est vraie, son bloc s'exécute et le reste de la chaîne est ignoré.",
            "mode_specifique": "video"
        },
        {
            "question": "Que signifie 'condition' dans le contexte d'un if ?",
            "options": '{"A": "Une valeur qui peut être true ou false", "B": "Une chaîne de caractères", "C": "Un nombre", "D": "Une fonction"}',
            "reponse_correcte": "A",
            "points": 10,
            "difficulte": "facile",
            "explication": "Une condition est une expression qui est évaluée à true ou false (booléen).",
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
    print("🎓 INSERTION DU COURS: JAVASCRIPT CONDITIONS (IF/ELSE)")
    print("=" * 60)
    
    
    conn = get_connection()
    if not conn:
        print("❌ Impossible de se connecter à la base de données")
        return
    
    conn.close()
    print("✅ Connexion à la base de données établie")
    
    
    cours_id = inserer_cours_javascript_conditions()
    
    if cours_id:
        inserer_questions_javascript_conditions(cours_id)
        print(f"\n🎉 Succès ! Cours 'JavaScript Conditions - If, Else, Else If' créé (ID: {cours_id})")
    else:
        print("\n❌ Échec de l'insertion")

if __name__ == "__main__":
    main()