
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

def inserer_cours_javascript_regex():
    
    
    admin_id = get_admin_user()
    if not admin_id:
        print("❌ Impossible de trouver un utilisateur")
        return False
    
    chapitre_id = get_chapitre_id()
    
    conn = get_connection()
    if not conn:
        return False
    
    cur = conn.cursor()
    
    slug_cours = "javascript-regex"
    
    cur.execute("SELECT id FROM cours_html WHERE slug = %s", (slug_cours,))
    existing = cur.fetchone()
    
    contenu_html = """
    <h1>🔍 JavaScript Regular Expressions - Les Expressions Régulières</h1>
    
    <div class="info-box">
        <p><strong>💡 À savoir :</strong> Les expressions régulières (RegEx) sont des séquences de caractères qui définissent des motifs de recherche. Elles sont utilisées pour valider, rechercher et remplacer du texte.</p>
    </div>
    
    <h2>Qu'est-ce qu'une Expression Régulière ?</h2>
    <p>Une expression régulière est un motif qui permet de rechercher, extraire ou remplacer du texte dans une chaîne de caractères. Elle simplifie les opérations complexes sur les chaînes.</p>
    
    <div class="tip-box">
        <p><strong>💡 Cas d'usage :</strong> Validation d'email, recherche de mots, formatage de texte, extraction de données.</p>
    </div>
    
    <h2>1. Créer une Expression Régulière</h2>
    
    <h3>Méthode 1 : Littéral (recommandé)</h3>
    <pre><code>let regex = /pattern/flags;</code></pre>
    
    <h3>Méthode 2 : Constructeur</h3>
    <pre><code>let regex = new RegExp("pattern", "flags");</code></pre>
    
    <h3>Exemples :</h3>
    <pre><code>// Chercher le mot "JavaScript"
let regex1 = /JavaScript/;

// Chercher "javascript" (insensible à la casse)
let regex2 = /javascript/i;

// Chercher globalement
let regex3 = /javascript/gi;</code></pre>
    
    <h2>2. Les Flags (modificateurs)</h2>
    
    <table border="1" style="border-collapse: collapse; width: 100%;">
        <thead style="background-color: #f2f2f2;">
            <th style="padding: 8px; text-align: left;">Flag</th>
            <th style="padding: 8px; text-align: left;">Description</th>
            <th style="padding: 8px; text-align: left;">Exemple</th>
        </thead>
        <tbody>
            <tr><td style="padding: 8px;"><code>g</code></td><td style="padding: 8px;">Recherche globale (toutes les occurrences)</td><td style="padding: 8px;"><code>/test/g</code></td></tr>
            <tr><td style="padding: 8px;"><code>i</code></td><td style="padding: 8px;">Insensible à la casse</td><td style="padding: 8px;"><code>/test/i</code> (TEST, test, Test)</td></tr>
            <tr><td style="padding: 8px;"><code>m</code></td><td style="padding: 8px;">Recherche multiligne</td><td style="padding: 8px;"><code>/^test/m</code></td></tr>
        </tbody>
    </table>
    
    <h2>3. Méthodes des Expressions Régulières</h2>
    
    <h3>test() - Vérifie si un motif existe</h3>
    <pre><code>let regex = /JavaScript/;
console.log(regex.test("J'aime JavaScript")); // true
console.log(regex.test("J'aime Python"));     // false</code></pre>
    
    <h3>exec() - Exécute la recherche et retourne les résultats</h3>
    <pre><code>let regex = /JavaScript/;
let result = regex.exec("J'aime JavaScript");
console.log(result); // Tableau avec l'occurrence trouvée</code></pre>
    
    <h2>4. Méthodes des Chaînes avec RegEx</h2>
    
    <h3>match() - Retourne les correspondances</h3>
    <pre><code>let texte = "Je code en JavaScript et en Python";
let resultat = texte.match(/JavaScript/);
console.log(resultat); // ["JavaScript"]

// Avec flag global
let resultats = texte.match(/[A-Z][a-z]+/g);
console.log(resultats); // ["Je", "JavaScript", "Python"]</code></pre>
    
    <h3>search() - Retourne l'index de la première correspondance</h3>
    <pre><code>let texte = "Je code en JavaScript";
let index = texte.search(/JavaScript/);
console.log(index); // 11 (position du mot)</code></pre>
    
    <h3>replace() - Remplace les correspondances</h3>
    <pre><code>let texte = "J'aime JavaScript";
let nouveauTexte = texte.replace(/JavaScript/, "Python");
console.log(nouveauTexte); // "J'aime Python"

// Avec flag global pour remplacer toutes les occurrences
let phrase = "chat chat chat";
let nouvellePhrase = phrase.replace(/chat/g, "chien");
console.log(nouvellePhrase); // "chien chien chien"</code></pre>
    
    <h2>5. Classes de caractères</h2>
    
    <table border="1" style="border-collapse: collapse; width: 100%;">
        <thead style="background-color: #f2f2f2;">
            <th style="padding: 8px; text-align: left;">Classe</th>
            <th style="padding: 8px; text-align: left;">Description</th>
            <th style="padding: 8px; text-align: left;">Exemple</th>
        </thead>
        <tbody>
            <tr><td style="padding: 8px;"><code>[a-z]</code></td><td style="padding: 8px;">Lettres minuscules</td><td style="padding: 8px;">/^[a-z]+$/</td></tr>
            <tr><td style="padding: 8px;"><code>[0-9]</code></td><td style="padding: 8px;">Chiffres</td><td style="padding: 8px;">/^[0-9]+$/</td></tr>
            <tr><td style="padding: 8px;"><code>\\d</code></td><td style="padding: 8px;">Chiffre (équivalent à [0-9])</td><td style="padding: 8px;">/\\d+/</td></tr>
            <tr><td style="padding: 8px;"><code>\\w</code></td><td style="padding: 8px;">Caractère alphanumérique</td><td style="padding: 8px;">/\\w+/</td></tr>
            <tr><td style="padding: 8px;"><code>\\s</code></td><td style="padding: 8px;">Espace blanc</td><td style="padding: 8px;">/\\s/</td></tr>
        </tbody>
    </table>
    
    <h2>6. Quantificateurs</h2>
    
    <ul>
        <li><code>+</code> : Une ou plusieurs fois</li>
        <li><code>*</code> : Zéro ou plusieurs fois</li>
        <li><code>?</code> : Zéro ou une fois</li>
        <li><code>{n}</code> : Exactement n fois</li>
        <li><code>{n,}</code> : Au moins n fois</li>
        <li><code>{n,m}</code> : Entre n et m fois</li>
    </ul>
    
    <pre><code>let regex1 = /a+/;      // "a", "aa", "aaa"...
let regex2 = /a{2,4}/;  // "aa", "aaa", "aaaa"</code></pre>
    
    <h2>7. Exemples pratiques</h2>
    
    <h3>Validation d'email</h3>
    <pre><code>function validerEmail(email) {
    let regex = /^[^\\s@]+@([^\\s@]+\\.)+[^\\s@]+$/;
    return regex.test(email);
}

console.log(validerEmail("test@example.com")); // true
console.log(validerEmail("test@example"));      // false</code></pre>
    
    <h3>Extraire les nombres d'une chaîne</h3>
    <pre><code>let texte = "J'ai 25 ans et 3 chiens";
let nombres = texte.match(/\\d+/g);
console.log(nombres); // ["25", "3"]</code></pre>
    
    <h3>Supprimer les espaces inutiles</h3>
    <pre><code>let texte = "  Bonjour   monde  ";
let nettoye = texte.replace(/\\s+/g, " ").trim();
console.log(nettoye); // "Bonjour monde"</code></pre>
    
    <h2>8. Exemple complet</h2>
    
    <pre><code>&lt;!DOCTYPE html&gt;
&lt;html&gt;
&lt;body&gt;
    &lt;h2&gt;Démonstration des Expressions Régulières&lt;/h2&gt;
    &lt;p id="demo"&gt;&lt;/p&gt;
    
    &lt;script&gt;
        let output = "&lt;strong&gt;1. Test de correspondance :&lt;/strong&gt;&lt;br&gt;";
        let regex = /JavaScript/;
        output += "Contient 'JavaScript' ? " + regex.test("J'aime JavaScript") + "&lt;br&gt;&lt;br&gt;";
        
        output += "&lt;strong&gt;2. Recherche avec match() :&lt;/strong&gt;&lt;br&gt;";
        let texte = "J'ai 25 ans et 3 chiens. Je code en JavaScript.";
        let nombres = texte.match(/\\d+/g);
        output += "Nombres trouvés : " + nombres.join(", ") + "&lt;br&gt;&lt;br&gt;";
        
        output += "&lt;strong&gt;3. Remplacer avec replace() :&lt;/strong&gt;&lt;br&gt;";
        let remplace = texte.replace(/JavaScript/, "Python");
        output += "Après remplacement : " + remplace + "&lt;br&gt;&lt;br&gt;";
        
        output += "&lt;strong&gt;4. Validation d'email :&lt;/strong&gt;&lt;br&gt;";
        function validerEmail(email) {
            let regex = /^[^\\s@]+@([^\\s@]+\\.)+[^\\s@]+$/;
            return regex.test(email);
        }
        output += "test@example.com : " + validerEmail("test@example.com") + "&lt;br&gt;";
        output += "test@example : " + validerEmail("test@example") + "&lt;br&gt;";
        
        document.getElementById("demo").innerHTML = output;
    &lt;/script&gt;
&lt;/body&gt;
&lt;/html&gt;</code></pre>
    
    <div class="info-box">
        <p><strong>💡 À retenir :</strong> Les expressions régulières sont un outil puissant pour la manipulation de texte. Utilisez-les pour la validation, la recherche et le remplacement.</p>
    </div>
    """.strip()
    
    cours_data = {
        "titre": "JavaScript Regular Expressions - Les Regex",
        "slug": slug_cours,
        "description": "Apprenez à utiliser les expressions régulières en JavaScript : création de regex, flags (g, i, m), méthodes test() et exec(), méthodes des chaînes match(), search(), replace(), classes de caractères, quantificateurs, validation d'email et extraction de données.",
        "contenu_texte": contenu_html,
        "difficulte": "intermediaire",
        "duree_estimee": 25,
        "ordre_affichage": 15,
        "chapitre_id": chapitre_id,
        "tags": ["javascript", "regex", "regular expressions", "pattern", "match", "replace", "search", "test", "validation", "intermediaire"],
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

def inserer_questions_javascript_regex(cours_id):
    
    
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
            "question": "Que signifie l'abréviation RegEx ?",
            "options": '{"A": "Regular Expression", "B": "Regular Text", "C": "Regex Expression", "D": "Real Expression"}',
            "reponse_correcte": "A",
            "points": 10,
            "difficulte": "facile",
            "explication": "RegEx signifie Regular Expression (expression régulière).",
            "mode_specifique": "texte"
        },
        {
            "question": "Quel flag rend une recherche insensible à la casse ?",
            "options": '{"A": "g", "B": "i", "C": "m", "D": "c"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "Le flag 'i' rend la recherche insensible à la casse (case-insensitive).",
            "mode_specifique": "texte"
        },
        
        
        {
            "question": "Quelle méthode RegEx vérifie si un motif existe dans une chaîne ?",
            "options": '{"A": "match()", "B": "test()", "C": "search()", "D": "exec()"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "test() vérifie si un motif existe et retourne true ou false.",
            "mode_specifique": "audio"
        },
        {
            "question": "Quelle méthode de chaîne remplace du texte avec une expression régulière ?",
            "options": '{"A": "match()", "B": "search()", "C": "replace()", "D": "split()"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "replace() remplace les correspondances d'une expression régulière.",
            "mode_specifique": "audio"
        },
        {
            "question": "Que signifie le flag 'g' dans une expression régulière ?",
            "options": '{"A": "Global (trouve toutes les occurrences)", "B": "Group", "C": "Grand", "D": "Greedy"}',
            "reponse_correcte": "A",
            "points": 10,
            "difficulte": "facile",
            "explication": "Le flag 'g' signifie global et trouve toutes les occurrences, pas seulement la première.",
            "mode_specifique": "audio"
        },
        
        
        {
            "question": "Que représente \\\\d en regex ?",
            "options": '{"A": "Une lettre", "B": "Un chiffre", "C": "Un espace", "D": "Un caractère spécial"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "\\\\d représente n'importe quel chiffre (0-9).",
            "mode_specifique": "video"
        },
        {
            "question": "Quelle méthode retourne l'index de la première correspondance ?",
            "options": '{"A": "match()", "B": "test()", "C": "search()", "D": "exec()"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "search() retourne l'index de la première correspondance, ou -1 si non trouvée.",
            "mode_specifique": "video"
        },
        {
            "question": "Que signifie le quantificateur '+' en regex ?",
            "options": '{"A": "Zéro ou une fois", "B": "Une ou plusieurs fois", "C": "Zéro ou plusieurs fois", "D": "Exactement une fois"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "+ signifie une ou plusieurs fois.",
            "mode_specifique": "video"
        },
        {
            "question": "Quel regex valide un email simple ?",
            "options": '{"A": "/^\\d+$/", "B": "/^[a-z]+$/", "C": "/^[^\\s@]+@([^\\s@]+\\.)+[^\\s@]+$/", "D": "/\\s+/"}',
            "reponse_correcte": "C",
            "points": 15,
            "difficulte": "moyen",
            "explication": "Cette expression valide un email avec @ et un domaine.",
            "mode_specifique": "video"
        },
        {
            "question": "Comment écrire une expression régulière pour trouver toutes les occurrences du mot 'test' (insensible à la casse) ?",
            "options": '{"A": "/test/g", "B": "/test/i", "C": "/test/gi", "D": "/test/ig"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "g pour global, i pour insensible à la casse.",
            "mode_specifique": "video"
        },
        {
            "question": "Que retourne la méthode match() ?",
            "options": '{"A": "Un booléen", "B": "Un index", "C": "Un tableau des correspondances", "D": "Une nouvelle chaîne"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "match() retourne un tableau contenant toutes les correspondances trouvées.",
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
    print("🎓 INSERTION DU COURS: JAVASCRIPT REGEX")
    print("=" * 60)
    
    
    conn = get_connection()
    if not conn:
        print("❌ Impossible de se connecter à la base de données")
        return
    
    conn.close()
    print("✅ Connexion à la base de données établie")
    
    
    cours_id = inserer_cours_javascript_regex()
    
    if cours_id:
        inserer_questions_javascript_regex(cours_id)
        print(f"\n🎉 Succès ! Cours 'JavaScript Regular Expressions - Les Regex' créé (ID: {cours_id})")
    else:
        print("\n❌ Échec de l'insertion")

if __name__ == "__main__":
    main()