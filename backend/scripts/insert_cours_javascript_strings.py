
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
        
        # Chercher un admin
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
        
        # Sinon, prendre le premier utilisateur
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

def inserer_cours_javascript_strings():
    
    
    admin_id = get_admin_user()
    if not admin_id:
        print("❌ Impossible de trouver un utilisateur")
        return False
    
    chapitre_id = get_chapitre_id()
    
    conn = get_connection()
    if not conn:
        return False
    
    cur = conn.cursor()
    
    slug_cours = "javascript-strings"
    
    cur.execute("SELECT id FROM cours_html WHERE slug = %s", (slug_cours,))
    existing = cur.fetchone()
    
    contenu_html = """
    <h1>📝 JavaScript Strings - Chaînes de Caractères</h1>
    
    <div class="info-box">
        <p><strong>💡 À savoir :</strong> Les chaînes de caractères sont des séquences de caractères utilisées pour stocker et manipuler du texte en JavaScript. Elles sont immuables, ce qui signifie que les modifications créent de nouvelles chaînes.</p>
    </div>
    
    <h2>Introduction aux Strings</h2>
    <p>Les chaînes de caractères sont essentielles pour :</p>
    <ul>
        <li>Valider les entrées utilisateur (emails, mots de passe)</li>
        <li>Extraire des hashtags</li>
        <li>Formater des numéros de téléphone</li>
        <li>Nettoyer des données</li>
    </ul>
    
    <div class="tip-box">
        <p><strong>💡 Important :</strong> Les chaînes sont immuables. Toute opération qui modifie une chaîne crée une nouvelle chaîne.</p>
    </div>
    
    <h2>1. Propriété .length</h2>
    <p>La propriété <code>length</code> retourne le nombre de caractères dans une chaîne.</p>
    
    <pre><code>let message = "Bonjour";
console.log(message.length);  // 7

let texte = "Hello World!";
console.log(texte.length);    // 12</code></pre>
    
    <h2>2. .toUpperCase() et .toLowerCase()</h2>
    
    <pre><code>let nom = "Jean";
console.log(nom.toUpperCase());  // "JEAN"
console.log(nom.toLowerCase());  // "jean"

let email = "User@Example.com";
let emailNormalise = email.toLowerCase();
console.log(emailNormalise);  // "user@example.com"</code></pre>
    
    <h2>3. .includes()</h2>
    <p>La méthode <code>includes()</code> vérifie si une sous-chaîne existe dans une chaîne. Retourne true ou false.</p>
    
    <pre><code>let phrase = "JavaScript est génial !";
console.log(phrase.includes("JavaScript"));  // true
console.log(phrase.includes("Python"));      // false

// Utile pour analyser des avis ou des commentaires
let avis = "Ce produit est excellent !";
if (avis.includes("excellent")) {
    console.log("Avis positif");
}</code></pre>
    
    <h2>4. .trim()</h2>
    <p>La méthode <code>trim()</code> supprime les espaces au début et à la fin d'une chaîne. Idéale pour nettoyer les entrées utilisateur dans les formulaires.</p>
    
    <pre><code>let inputUtilisateur = "  email@exemple.com  ";
let emailPropre = inputUtilisateur.trim();
console.log(emailPropre);  // "email@exemple.com"

let messageAvecEspaces = "   Bonjour le monde   ";
console.log(messageAvecEspaces.trim());  // "Bonjour le monde"</code></pre>
    
    <h2>5. .split()</h2>
    <p>La méthode <code>split()</code> divise une chaîne en un tableau de sous-chaînes selon un séparateur.</p>
    
    <pre><code>// Convertir une chaîne CSV en tableau
let csv = "pomme,banane,orange,mangue";
let fruits = csv.split(",");
console.log(fruits);  // ["pomme", "banane", "orange", "mangue"]

// Extraire le nom d'utilisateur d'un email
let email = "jean.dupont@email.com";
let username = email.split("@")[0];
console.log(username);  // "jean.dupont"

// Séparer les mots d'une phrase
let phrase = "JavaScript est puissant";
let mots = phrase.split(" ");
console.log(mots);  // ["JavaScript", "est", "puissant"]</code></pre>
    
    <h2>6. Autres méthodes utiles</h2>
    
    <table border="1" style="border-collapse: collapse; width: 100%;">
        <thead style="background-color: #f2f2f2;">
            <th style="padding: 8px; text-align: left;">Méthode</th>
            <th style="padding: 8px; text-align: left;">Description</th>
            <th style="padding: 8px; text-align: left;">Exemple</th>
        </thead>
        <tbody>
            <tr><td style="padding: 8px;"><code>charAt()</code></td><td style="padding: 8px;">Retourne le caractère à une position donnée</td><td style="padding: 8px;">"Hello".charAt(1) → "e"</td></tr>
            <tr><td style="padding: 8px;"><code>indexOf()</code></td><td style="padding: 8px;">Retourne la position d'une sous-chaîne</td><td style="padding: 8px;">"Hello".indexOf("e") → 1</td></tr>
            <tr><td style="padding: 8px;"><code>slice()</code></td><td style="padding: 8px;">Extrait une partie de la chaîne</td><td style="padding: 8px;">"Hello".slice(1,4) → "ell"</td></tr>
            <tr><td style="padding: 8px;"><code>replace()</code></td><td style="padding: 8px;">Remplace une sous-chaîne</td><td style="padding: 8px;">"Hello".replace("H","J") → "Jello"</td></tr>
            <tr><td style="padding: 8px;"><code>repeat()</code></td><td style="padding: 8px;">Répète la chaîne n fois</td><td style="padding: 8px;">"Ha".repeat(3) → "HaHaHa"</td></tr>
            <tr><td style="padding: 8px;"><code>startsWith()</code></td><td style="padding: 8px;">Vérifie le début de la chaîne</td><td style="padding: 8px;">"Hello".startsWith("He") → true</td></tr>
            <tr><td style="padding: 8px;"><code>endsWith()</code></td><td style="padding: 8px;">Vérifie la fin de la chaîne</td><td style="padding: 8px;">"Hello".endsWith("lo") → true</td></tr>
        </tbody>
    </table>
    
    <h2>7. Exemple complet</h2>
    
    <pre><code>&lt;!DOCTYPE html&gt;
&lt;html&gt;
&lt;body&gt;
    &lt;h2&gt;Manipulation des chaînes JavaScript&lt;/h2&gt;
    &lt;p id="demo"&gt;&lt;/p&gt;
    
    &lt;script&gt;
        let texte = "  Apprenez JavaScript avec W3Schools!  ";
        let email = "  utilisateur@exemple.com  ";
        
        let output = "&lt;strong&gt;Démonstration des méthodes String :&lt;/strong&gt;&lt;br&gt;&lt;br&gt;";
        
        // .length
        output += "1. .length : " + texte.length + " caractères&lt;br&gt;";
        
        // .trim()
        let textePropre = texte.trim();
        output += "2. .trim() : '" + textePropre + "'&lt;br&gt;";
        
        // .toUpperCase()
        output += "3. .toUpperCase() : " + textePropre.toUpperCase() + "&lt;br&gt;";
        
        // .includes()
        let contientJS = textePropre.includes("JavaScript");
        output += "4. .includes('JavaScript') : " + contientJS + "&lt;br&gt;";
        
        // .split()
        let mots = textePropre.split(" ");
        output += "5. .split(' ') : [" + mots.join(", ") + "]&lt;br&gt;";
        
        // Nettoyage d'email
        let emailPropre = email.trim().toLowerCase();
        let username = emailPropre.split("@")[0];
        output += "6. Email nettoyé : " + emailPropre + "&lt;br&gt;";
        output += "   Nom d'utilisateur : " + username;
        
        document.getElementById("demo").innerHTML = output;
    &lt;/script&gt;
&lt;/body&gt;
&lt;/html&gt;</code></pre>
    
    <h2>Bonnes pratiques</h2>
    
    <ul>
        <li><strong>Toujours utiliser .trim()</strong> pour nettoyer les entrées utilisateur</li>
        <li><strong>Normaliser les emails</strong> avec .toLowerCase() avant comparaison</li>
        <li><strong>Utiliser .includes()</strong> pour rechercher du texte</li>
        <li><strong>Maîtriser .split()</strong> pour convertir des chaînes en tableaux</li>
        <li><strong>Pratiquez au moins 10 méthodes</strong> pour renforcer vos compétences</li>
    </ul>
    
    <div class="info-box">
        <p><strong>💡 À retenir :</strong> Les méthodes des chaînes sont des outils essentiels pour tout développeur. Apprenez leur syntaxe, leurs arguments et leurs types de retour.</p>
    </div>
    """.strip()
    
    cours_data = {
        "titre": "JavaScript Strings - Chaînes de Caractères",
        "slug": slug_cours,
        "description": "Apprenez à manipuler les chaînes de caractères en JavaScript : propriété length, méthodes toUpperCase(), toLowerCase(), includes(), trim(), split(), et bien plus. Découvrez comment nettoyer, valider et transformer du texte pour des applications web.",
        "contenu_texte": contenu_html,
        "difficulte": "debutant",
        "duree_estimee": 25,
        "ordre_affichage": 7,
        "chapitre_id": chapitre_id,
        "tags": ["javascript", "strings", "length", "toUpperCase", "toLowerCase", "includes", "trim", "split", "debutant"],
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

def inserer_questions_javascript_strings(cours_id):
    
    
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
            "question": "Que signifie qu'une chaîne de caractères est 'immuable' en JavaScript ?",
            "options": '{"A": "Elle peut être modifiée directement", "B": "Elle ne peut pas être modifiée; toute modification crée une nouvelle chaîne", "C": "Elle est automatiquement convertie en nombre", "D": "Elle ne peut pas être utilisée dans des conditions"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "Les chaînes sont immuables, ce qui signifie qu'une fois créées, elles ne peuvent pas être modifiées. Toute opération qui semble modifier une chaîne crée en réalité une nouvelle chaîne.",
            "mode_specifique": "texte"
        },
        {
            "question": "Que fait la méthode trim() sur une chaîne ?",
            "options": '{"A": "Supprime tous les espaces", "B": "Supprime les espaces au début et à la fin", "C": "Ajoute des espaces", "D": "Convertit en minuscules"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "trim() supprime les espaces au début et à la fin d'une chaîne, idéal pour nettoyer les entrées utilisateur.",
            "mode_specifique": "texte"
        },
        
        
        {
            "question": "Quelle propriété retourne le nombre de caractères dans une chaîne ?",
            "options": '{"A": ".size", "B": ".count", "C": ".length", "D": ".charCount"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "length est une propriété qui retourne le nombre de caractères dans une chaîne.",
            "mode_specifique": "audio"
        },
        {
            "question": "Que retourne la méthode includes() ?",
            "options": '{"A": "Le nombre d\'occurrences", "B": "La position de la sous-chaîne", "C": "true ou false (booléen)", "D": "La sous-chaîne trouvée"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "includes() retourne un booléen (true ou false) selon que la sous-chaîne est présente ou non.",
            "mode_specifique": "audio"
        },
        {
            "question": "Comment convertir une chaîne CSV (valeurs séparées par des virgules) en tableau ?",
            "options": '{"A": ".toArray()", "B": ".split(",")", "C": ".join(",")", "D": ".slice()"}',
            "reponse_correcte": "B",
            "points": 15,
            "difficulte": "moyen",
            "explication": "split(',') divise la chaîne à chaque virgule et retourne un tableau de valeurs.",
            "mode_specifique": "audio"
        },
        
        
        {
            "question": "Que fait toUpperCase() sur une chaîne ?",
            "options": '{"A": "Convertit en minuscules", "B": "Convertit en majuscules", "C": "Supprime les espaces", "D": "Inverse la chaîne"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "toUpperCase() convertit tous les caractères d'une chaîne en majuscules.",
            "mode_specifique": "video"
        },
        {
            "question": "Quel est le résultat de 'Hello World'.includes('World') ?",
            "options": '{"A": "true", "B": "false", "C": "5", "D": "World"}',
            "reponse_correcte": "A",
            "points": 10,
            "difficulte": "facile",
            "explication": "'Hello World' contient la sous-chaîne 'World', donc includes() retourne true.",
            "mode_specifique": "video"
        },
        {
            "question": "Comment extraire le nom d'utilisateur d'un email avec split() ?",
            "options": '{"A": "email.split(\\".\\")[0]", "B": "email.split(\\"@\\")[1]", "C": "email.split(\\"@\\")[0]", "D": "email.split(\\",\\")[0]"}',
            "reponse_correcte": "C",
            "points": 15,
            "difficulte": "moyen",
            "explication": "split('@')[0] divise l'email au niveau du @ et prend la première partie (avant le @).",
            "mode_specifique": "video"
        },
        {
            "question": "Quelle méthode utiliser pour supprimer les espaces inutiles dans un formulaire ?",
            "options": '{"A": ".trim()", "B": ".clean()", "C": ".removeSpaces()", "D": ".strip()"}',
            "reponse_correcte": "A",
            "points": 10,
            "difficulte": "facile",
            "explication": "trim() est la méthode standard pour supprimer les espaces au début et à la fin d'une chaîne.",
            "mode_specifique": "video"
        },
        {
            "question": "Que signifie 'CSV' dans le contexte des chaînes ?",
            "options": '{"A": "Comma-Separated Values", "B": "Character String Value", "C": "Code Source Variable", "D": "Common String Value"}',
            "reponse_correcte": "A",
            "points": 10,
            "difficulte": "facile",
            "explication": "CSV signifie 'Comma-Separated Values' (valeurs séparées par des virgules).",
            "mode_specifique": "video"
        },
        {
            "question": "Quelle est la valeur de 'JavaScript'.length ?",
            "options": '{"A": "8", "B": "9", "C": "10", "D": "11"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "'JavaScript' contient 10 caractères (J,a,v,a,S,c,r,i,p,t).",
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
    print("🎓 INSERTION DU COURS: JAVASCRIPT STRINGS")
    print("=" * 60)
    
    
    conn = get_connection()
    if not conn:
        print("❌ Impossible de se connecter à la base de données")
        return
    
    conn.close()
    print("✅ Connexion à la base de données établie")
    
    
    cours_id = inserer_cours_javascript_strings()
    
    if cours_id:
        inserer_questions_javascript_strings(cours_id)
        print(f"\n🎉 Succès ! Cours 'JavaScript Strings - Chaînes de Caractères' créé (ID: {cours_id})")
    else:
        print("\n❌ Échec de l'insertion")

if __name__ == "__main__":
    main()