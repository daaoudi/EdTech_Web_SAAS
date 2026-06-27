
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

def inserer_cours_javascript_numbers():
    
    
    admin_id = get_admin_user()
    if not admin_id:
        print("❌ Impossible de trouver un utilisateur")
        return False
    
    chapitre_id = get_chapitre_id()
    
    conn = get_connection()
    if not conn:
        return False
    
    cur = conn.cursor()
    
    slug_cours = "javascript-numbers"
    
    cur.execute("SELECT id FROM cours_html WHERE slug = %s", (slug_cours,))
    existing = cur.fetchone()
    
    contenu_html = """
    <h1>🔢 JavaScript Numbers - Les Nombres</h1>
    
    <div class="info-box">
        <p><strong>💡 À savoir :</strong> En JavaScript, tous les nombres sont du type "number", qu'ils soient entiers (integers) ou décimaux (floats).</p>
    </div>
    
    <h2>Introduction aux Nombres</h2>
    <p>JavaScript gère deux types de nombres :</p>
    <ul>
        <li><strong>Entiers (integers)</strong> : Nombres sans virgule (ex: 42, 100, -5)</li>
        <li><strong>Décimaux (floats)</strong> : Nombres avec virgule (ex: 3.14, 2.5, 0.99)</li>
    </ul>
    
    <div class="tip-box">
        <p><strong>💡 Note :</strong> JavaScript ignore les zéros finaux sauf si le nombre contient des décimales.</p>
    </div>
    
    <h2>1. Comparaison de nombres</h2>
    <p>JavaScript peut comparer des entiers et des décimaux. Les nombres et chaînes avec la même valeur ne sont pas égaux en raison de la différence de type.</p>
    
    <pre><code>let entier = 5;
let decimal = 5.0;
console.log(entier === decimal); // true

let nombre = 10;
let chaine = "10";
console.log(nombre === chaine); // false (type différent)</code></pre>
    
    <h2>2. Convertir des chaînes en nombres</h2>
    <p>La fonction <code>Number()</code> convertit une chaîne en nombre. Si la conversion échoue, elle retourne <code>NaN</code> (Not a Number).</p>
    
    <pre><code>let strNumber = "123";
let number = Number(strNumber);
console.log(number); // 123

let invalid = Number("hello");
console.log(invalid); // NaN</code></pre>
    
    <h2>3. Conversion booléenne</h2>
    <pre><code>console.log(Number(true));  // 1
console.log(Number(false)); // 0</code></pre>
    
    <h2>4. Méthodes importantes des nombres</h2>
    
    <table border="1" style="border-collapse: collapse; width: 100%;">
        <thead style="background-color: #f2f2f2;">
            <th style="padding: 8px; text-align: left;">Méthode</th>
            <th style="padding: 8px; text-align: left;">Description</th>
            <th style="padding: 8px; text-align: left;">Exemple</th>
        </thead>
        <tbody>
            <tr><td style="padding: 8px;"><code>Number.isInteger()</code></td><td style="padding: 8px;">Vérifie si la valeur est un entier</td><td style="padding: 8px;"><code>Number.isInteger(5.5) → false</code></td></tr>
            <tr><td style="padding: 8px;"><code>parseFloat()</code></td><td style="padding: 8px;">Convertit en nombre décimal</td><td style="padding: 8px;"><code>parseFloat("3.14") → 3.14</code></td></tr>
            <tr><td style="padding: 8px;"><code>parseInt()</code></td><td style="padding: 8px;">Convertit en entier</td><td style="padding: 8px;"><code>parseInt("123px") → 123</code></td></tr>
            <tr><td style="padding: 8px;"><code>toFixed()</code></td><td style="padding: 8px;">Limite les décimales (retourne une chaîne)</td><td style="padding: 8px;"><code>(3.14159).toFixed(2) → "3.14"</code></td></tr>
            <tr><td style="padding: 8px;"><code>toString()</code></td><td style="padding: 8px;">Convertit en chaîne</td><td style="padding: 8px;"><code>(123).toString() → "123"</code></td></tr>
        </tbody>
    </table>
    
    <pre><code>let valeur = 3.14159;

console.log(Number.isInteger(valeur));  // false
console.log(parseFloat(valeur));        // 3.14159
console.log(parseInt(valeur));          // 3
console.log(valeur.toFixed(2));         // "3.14"
console.log(valeur.toString());         // "3.14159"</code></pre>
    
    <h2>5. Comprendre NaN (Not a Number)</h2>
    <p>NaN est une valeur spéciale qui signifie "Not a Number". Elle apparaît quand une opération mathématique échoue.</p>
    
    <h3>Différence entre Number.isNaN() et isNaN() :</h3>
    <ul>
        <li><strong>Number.isNaN()</strong> : Vérifie si la valeur est NaN ET de type number</li>
        <li><strong>isNaN()</strong> (globale) : Vérifie seulement si la valeur n'est PAS un nombre</li>
    </ul>
    
    <pre><code>console.log(Number.isNaN(NaN));      // true
console.log(Number.isNaN("hello"));   // false (c'est une chaîne, pas NaN)

console.log(isNaN(NaN));              // true
console.log(isNaN("hello"));          // true (ce n'est pas un nombre)</code></pre>
    
    <div class="warning-box">
        <p><strong>⚠️ Important :</strong> Number.isNaN() est plus stricte et fiable car elle vérifie à la fois la valeur et le type.</p>
    </div>
    
    <h2>6. Enchaînement de méthodes</h2>
    <p>On peut chaîner les méthodes pour plus d'efficacité.</p>
    
    <pre><code>let resultat = parseFloat("3.14159").toFixed(2);
console.log(resultat); // "3.14"

// Note : toFixed() retourne déjà une chaîne, toString() est redondant
</code></pre>
    
    <h2>7. Exemple complet</h2>
    
    <pre><code>&lt;!DOCTYPE html&gt;
&lt;html&gt;
&lt;body&gt;
    &lt;h2&gt;Démonstration des Nombres JavaScript&lt;/h2&gt;
    &lt;p id="demo"&gt;&lt;/p&gt;
    
    &lt;script&gt;
        let prix = "19.99";
        let quantite = "3";
        
        // Conversion
        let prixNombre = parseFloat(prix);
        let quantiteNombre = parseInt(quantite);
        
        let total = prixNombre * quantiteNombre;
        
        let output = "&lt;strong&gt;Données originales :&lt;/strong&gt;&lt;br&gt;";
        output += "Prix (string) : " + prix + "&lt;br&gt;";
        output += "Quantité (string) : " + quantite + "&lt;br&gt;&lt;br&gt;";
        
        output += "&lt;strong&gt;Après conversion :&lt;/strong&gt;&lt;br&gt;";
        output += "Prix (number) : " + prixNombre + "&lt;br&gt;";
        output += "Quantité (number) : " + quantiteNombre + "&lt;br&gt;&lt;br&gt;";
        
        output += "&lt;strong&gt;Résultat :&lt;/strong&gt;&lt;br&gt;";
        output += "Total : " + total.toFixed(2) + "€";
        
        document.getElementById("demo").innerHTML = output;
    &lt;/script&gt;
&lt;/body&gt;
&lt;/html&gt;</code></pre>
    
    <h2>Bonnes pratiques</h2>
    
    <ul>
        <li><strong>Utilisez Number.isNaN()</strong> plutôt que isNaN() pour éviter les confusions</li>
        <li><strong>ParseFloat() et parseInt()</strong> pour extraire des nombres de chaînes mixtes</li>
        <li><strong>toFixed()</strong> pour formater les décimales (mais retourne une chaîne)</li>
        <li><strong>Number.isInteger()</strong> pour vérifier si un nombre est un entier</li>
        <li><strong>Méfiez-vous des conversions implicites</strong> entre nombres et chaînes</li>
    </ul>
    
    <div class="info-box">
        <p><strong>💡 À retenir :</strong> Les nombres sont un type fondamental en JavaScript. Maîtrisez les méthodes de conversion et la gestion de NaN.</p>
    </div>
    """.strip()
    
    cours_data = {
        "titre": "JavaScript Numbers - Nombres et Méthodes",
        "slug": slug_cours,
        "description": "Apprenez à manipuler les nombres en JavaScript : entiers et décimaux, conversion de chaînes en nombres (Number(), parseFloat(), parseInt()), méthodes (isInteger(), toFixed()), compréhension de NaN et différence entre isNaN() et Number.isNaN().",
        "contenu_texte": contenu_html,
        "difficulte": "debutant",
        "duree_estimee": 20,
        "ordre_affichage": 8,
        "chapitre_id": chapitre_id,
        "tags": ["javascript", "numbers", "parseFloat", "parseInt", "toFixed", "isNaN", "Number.isNaN", "debutant"],
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

def inserer_questions_javascript_numbers(cours_id):
    
    
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
    
    questions =[
        
        {
            "question": "Que signifie NaN en JavaScript ?",
            "options": '{"A": "Null a Number", "B": "Not a Number", "C": "Number and Null", "D": "New Assignment Number"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "NaN signifie 'Not a Number', une valeur spéciale retournée quand une opération mathématique échoue.",
            "mode_specifique": "texte"
        },
        {
            "question": "Quelle est la différence entre isNaN() et Number.isNaN() ?",
            "options": '{"A": "Elles font la même chose", "B": "isNaN() convertit d\'abord la valeur, Number.isNaN() ne convertit pas", "C": "Number.isNaN() convertit d\'abord la valeur", "D": "isNaN() est plus récente"}',
            "reponse_correcte": "B",
            "points": 15,
            "difficulte": "moyen",
            "explication": "isNaN() convertit d'abord la valeur en nombre, Number.isNaN() vérifie si la valeur est NaN sans conversion.",
            "mode_specifique": "texte"
        },
        
        
        {
            "question": "Que retourne Number(true) ?",
            "options": '{"A": "true", "B": "false", "C": "1", "D": "0"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "Number(true) retourne 1, et Number(false) retourne 0.",
            "mode_specifique": "audio"
        },
        {
            "question": "Que fait parseFloat() ?",
            "options": '{"A": "Convertit en entier", "B": "Convertit en nombre décimal", "C": "Convertit en chaîne", "D": "Convertit en booléen"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "parseFloat() convertit une chaîne en nombre décimal (flottant).",
            "mode_specifique": "audio"
        },
        {
            "question": "Quelle méthode permet de limiter le nombre de décimales ?",
            "options": '{"A": "toDecimal()", "B": "toPrecision()", "C": "toFixed()", "D": "toFloat()"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "toFixed() limite le nombre de décimales et retourne une chaîne.",
            "mode_specifique": "audio"
        },
        
        
        {
            "question": "Quel est le résultat de 5 === '5' en JavaScript ?",
            "options": '{"A": "true", "B": "false", "C": "10", "D": "Erreur"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "5 (nombre) n'est pas égal à '5' (chaîne) car les types sont différents.",
            "mode_specifique": "video"
        },
        {
            "question": "Que retourne parseInt('123px') ?",
            "options": '{"A": "123", "B": "123px", "C": "NaN", "D": "0"}',
            "reponse_correcte": "A",
            "points": 10,
            "difficulte": "facile",
            "explication": "parseInt() extrait l'entier au début de la chaîne, ignorant le reste.",
            "mode_specifique": "video"
        },
        {
            "question": "Que retourne Number('abc') ?",
            "options": '{"A": "abc", "B": "0", "C": "NaN", "D": "Erreur"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "Number('abc') ne peut pas convertir 'abc' en nombre, donc retourne NaN.",
            "mode_specifique": "video"
        },
        {
            "question": "Quelle méthode vérifie si une valeur est un entier ?",
            "options": '{"A": "isInt()", "B": "isInteger()", "C": "Number.isInteger()", "D": "isNumber()"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "Number.isInteger() vérifie si la valeur est un nombre entier.",
            "mode_specifique": "video"
        },
        {
            "question": "Que retourne (3.14159).toFixed(2) ?",
            "options": '{"A": "3.14", "B": "3.14159", "C": "3.15", "D": "3.14"}',
            "reponse_correcte": "D",
            "points": 10,
            "difficulte": "facile",
            "explication": "toFixed(2) retourne une chaîne avec 2 décimales, donc '3.14'.",
            "mode_specifique": "video"
        },
        {
            "question": "Que retourne Number.isNaN('hello') ?",
            "options": '{"A": "true", "B": "false", "C": "NaN", "D": "Erreur"}',
            "reponse_correcte": "B",
            "points": 15,
            "difficulte": "moyen",
            "explication": "Number.isNaN() vérifie si la valeur est NaN ET de type number. 'hello' n'est pas NaN, donc false.",
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
    print("🎓 INSERTION DU COURS: JAVASCRIPT NUMBERS")
    print("=" * 60)
    
    
    conn = get_connection()
    if not conn:
        print("❌ Impossible de se connecter à la base de données")
        return
    
    conn.close()
    print("✅ Connexion à la base de données établie")
    
    
    cours_id = inserer_cours_javascript_numbers()
    
    if cours_id:
        inserer_questions_javascript_numbers(cours_id)
        print(f"\n🎉 Succès ! Cours 'JavaScript Numbers - Nombres et Méthodes' créé (ID: {cours_id})")
    else:
        print("\n❌ Échec de l'insertion")

if __name__ == "__main__":
    main()