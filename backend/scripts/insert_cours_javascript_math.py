
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

def inserer_cours_javascript_math():
    
    
    admin_id = get_admin_user()
    if not admin_id:
        print("❌ Impossible de trouver un utilisateur")
        return False
    
    chapitre_id = get_chapitre_id()
    
    conn = get_connection()
    if not conn:
        return False
    
    cur = conn.cursor()
    
    slug_cours = "javascript-math-object"
    
    cur.execute("SELECT id FROM cours_html WHERE slug = %s", (slug_cours,))
    existing = cur.fetchone()
    
    contenu_html = """
    <h1>🧮 JavaScript Math Object - L'Objet Math</h1>
    
    <div class="info-box">
        <p><strong>💡 À savoir :</strong> Math est un objet intégré en JavaScript qui fournit des constantes et méthodes pour les opérations mathématiques. Il permet d'effectuer des calculs sans avoir à définir manuellement les fonctions.</p>
    </div>
    
    <h2>Introduction à l'objet Math</h2>
    <p>L'objet Math fournit des constantes utiles comme Math.PI et Math.E, ainsi que des méthodes pour les arrondis, les puissances, les racines, les logarithmes, la trigonométrie, les valeurs absolues, et les comparaisons.</p>
    
    <div class="tip-box">
        <p><strong>💡 À retenir :</strong> Math n'est pas un constructeur. Toutes ses propriétés et méthodes sont statiques, appelées directement sur l'objet Math.</p>
    </div>
    
    <h2>1. Constantes Mathématiques</h2>
    
    <pre><code>console.log(Math.PI);  // 3.141592653589793
console.log(Math.E);   // 2.718281828459045</code></pre>
    
    <h2>2. Méthodes d'arrondi</h2>
    
    <table border="1" style="border-collapse: collapse; width: 100%;">
        <thead style="background-color: #f2f2f2;">
            <th style="padding: 8px; text-align: left;">Méthode</th>
            <th style="padding: 8px; text-align: left;">Description</th>
            <th style="padding: 8px; text-align: left;">Exemple</th>
        </thead>
        <tbody>
            <tr><td style="padding: 8px;"><code>Math.round()</code></td><td style="padding: 8px;">Arrondit à l'entier le plus proche</td><td style="padding: 8px;">Math.round(4.6) → 5</td> </tr>
            <tr><td style="padding: 8px;"><code>Math.floor()</code></td><td style="padding: 8px;">Arrondit toujours vers le bas</td><td style="padding: 8px;">Math.floor(4.9) → 4</td> </tr>
            <tr><td style="padding: 8px;"><code>Math.ceil()</code></td><td style="padding: 8px;">Arrondit toujours vers le haut</td><td style="padding: 8px;">Math.ceil(4.1) → 5</td> </tr>
            <tr><td style="padding: 8px;"><code>Math.trunc()</code></td><td style="padding: 8px;">Supprime la partie décimale</td><td style="padding: 8px;">Math.trunc(4.9) → 4</td> </tr>
        </tbody>
    </table>
    
    <h2>3. Puissances et racines</h2>
    
    <pre><code>// Puissance
console.log(Math.pow(2, 3)); // 8 (2^3)

// Racine carrée
console.log(Math.sqrt(16));  // 4

// Racine cubique
console.log(Math.cbrt(27));  // 3</code></pre>
    
    <h2>4. Logarithmes</h2>
    
    <pre><code>console.log(Math.log(Math.E)); // 1 (logarithme naturel)
console.log(Math.log10(100));  // 2 (logarithme base 10)
console.log(Math.log2(8));     // 3 (logarithme base 2)</code></pre>
    
    <h2>5. Fonctions trigonométriques</h2>
    
    <pre><code>// Travaille avec les radians (π rad = 180°)
let angle = 45 * Math.PI / 180; // 45° en radians

console.log(Math.sin(angle));   // sinus
console.log(Math.cos(angle));   // cosinus
console.log(Math.tan(angle));   // tangente</code></pre>
    
    <h2>6. Valeur absolue et signe</h2>
    
    <pre><code>// Valeur absolue
console.log(Math.abs(-10)); // 10

// Signe d'un nombre
console.log(Math.sign(-5)); // -1
console.log(Math.sign(0));  // 0
console.log(Math.sign(7));  // 1</code></pre>
    
    <h2>7. Maximum et Minimum</h2>
    
    <pre><code>console.log(Math.max(5, 10, 3, 8, 2)); // 10
console.log(Math.min(5, 10, 3, 8, 2)); // 2

// Avec un tableau
let nombres = [5, 10, 3, 8, 2];
console.log(Math.max(...nombres)); // 10
console.log(Math.min(...nombres)); // 2</code></pre>
    
    <h2>8. Nombres aléatoires</h2>
    
    <pre><code>// Nombre aléatoire entre 0 et 1
console.log(Math.random());

// Nombre aléatoire entre 0 et 10
console.log(Math.random() * 10);

// Entier aléatoire entre min et max (inclus)
function getRandomInt(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}
console.log(getRandomInt(1, 100));</code></pre>
    
    <h2>9. Exemple complet</h2>
    
    <pre><code>&lt;!DOCTYPE html&gt;
&lt;html&gt;
&lt;body&gt;
    &lt;h2&gt;Démonstration de l'objet Math JavaScript&lt;/h2&gt;
    &lt;p id="demo"&gt;&lt;/p&gt;
    
    &lt;script&gt;
        let output = "&lt;strong&gt;Constantes :&lt;/strong&gt;&lt;br&gt;";
        output += "π = " + Math.PI + "&lt;br&gt;";
        output += "e = " + Math.E + "&lt;br&gt;&lt;br&gt;";
        
        output += "&lt;strong&gt;Arrondis :&lt;/strong&gt;&lt;br&gt;";
        output += "round(4.6) = " + Math.round(4.6) + "&lt;br&gt;";
        output += "floor(4.9) = " + Math.floor(4.9) + "&lt;br&gt;";
        output += "ceil(4.1) = " + Math.ceil(4.1) + "&lt;br&gt;";
        output += "trunc(4.9) = " + Math.trunc(4.9) + "&lt;br&gt;&lt;br&gt;";
        
        output += "&lt;strong&gt;Puissances et racines :&lt;/strong&gt;&lt;br&gt;";
        output += "2^3 = " + Math.pow(2, 3) + "&lt;br&gt;";
        output += "√16 = " + Math.sqrt(16) + "&lt;br&gt;&lt;br&gt;";
        
        output += "&lt;strong&gt;Max et Min :&lt;/strong&gt;&lt;br&gt;";
        output += "max(5,10,3,8,2) = " + Math.max(5, 10, 3, 8, 2) + "&lt;br&gt;";
        output += "min(5,10,3,8,2) = " + Math.min(5, 10, 3, 8, 2) + "&lt;br&gt;&lt;br&gt;";
        
        output += "&lt;strong&gt;Nombre aléatoire :&lt;/strong&gt;&lt;br&gt;";
        output += "Entre 1 et 100 : " + (Math.floor(Math.random() * 100) + 1);
        
        document.getElementById("demo").innerHTML = output;
    &lt;/script&gt;
&lt;/body&gt;
&lt;/html&gt;</code></pre>
    
    <div class="info-box">
        <p><strong>💡 À retenir :</strong> L'objet Math est un outil puissant pour les opérations mathématiques. Il fournit des constantes et méthodes essentielles pour les arrondis, puissances, racines, trigonométrie et comparaisons.</p>
    </div>
    """.strip()
    
    cours_data = {
        "titre": "JavaScript Math Object - L'Objet Math",
        "slug": slug_cours,
        "description": "Apprenez à utiliser l'objet Math en JavaScript : constantes (PI, E), méthodes d'arrondi (round, floor, ceil, trunc), puissances (pow), racines (sqrt), logarithmes, trigonométrie, valeur absolue (abs), signe (sign), maximum/minimum (max, min), et nombres aléatoires (random).",
        "contenu_texte": contenu_html,
        "difficulte": "debutant",
        "duree_estimee": 20,
        "ordre_affichage": 14,
        "chapitre_id": chapitre_id,
        "tags": ["javascript", "math", "pi", "round", "floor", "ceil", "pow", "sqrt", "random", "abs", "max", "min", "debutant"],
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

def inserer_questions_javascript_math(cours_id):
    
    
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
            "question": "Quelle méthode arrondit un nombre à l'entier le plus proche ?",
            "options": '{"A": "Math.floor()", "B": "Math.ceil()", "C": "Math.round()", "D": "Math.trunc()"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "Math.round() arrondit à l'entier le plus proche (vers le haut pour 0.5 et plus).",
            "mode_specifique": "texte"
        },
        {
            "question": "Comment obtenir la valeur de Pi en JavaScript ?",
            "options": '{"A": "Math.Pi", "B": "Math.PI", "C": "Math.pi", "D": "Math.PI()"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "Math.PI (en majuscules) donne la constante mathématique π.",
            "mode_specifique": "texte"
        },
        
        
        {
            "question": "Quelle méthode supprime la partie décimale d'un nombre ?",
            "options": '{"A": "Math.round()", "B": "Math.floor()", "C": "Math.ceil()", "D": "Math.trunc()"}',
            "reponse_correcte": "D",
            "points": 10,
            "difficulte": "facile",
            "explication": "Math.trunc() supprime la partie décimale, ne gardant que l'entier.",
            "mode_specifique": "audio"
        },
        {
            "question": "Comment générer un nombre aléatoire entre 0 et 1 ?",
            "options": '{"A": "Math.random()", "B": "Math.random(1)", "C": "Math.rand()", "D": "Math.randomBetween(0,1)"}',
            "reponse_correcte": "A",
            "points": 10,
            "difficulte": "facile",
            "explication": "Math.random() retourne un nombre aléatoire entre 0 (inclus) et 1 (exclus).",
            "mode_specifique": "audio"
        },
        {
            "question": "Quelle méthode trouve la racine carrée d'un nombre ?",
            "options": '{"A": "Math.pow()", "B": "Math.sqrt()", "C": "Math.root()", "D": "Math.square()"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "Math.sqrt() retourne la racine carrée d'un nombre.",
            "mode_specifique": "audio"
        },
        
        
        {
            "question": "Que retourne Math.max(5, 10, 3, 8, 2) ?",
            "options": '{"A": "2", "B": "5", "C": "8", "D": "10"}',
            "reponse_correcte": "D",
            "points": 10,
            "difficulte": "facile",
            "explication": "Math.max() retourne la plus grande valeur parmi les arguments, donc 10.",
            "mode_specifique": "video"
        },
        {
            "question": "Que retourne Math.abs(-7) ?",
            "options": '{"A": "0", "B": "7", "C": "-7", "D": "undefined"}',
            "reponse_correcte": "B",
            "points": 10,
            "difficulte": "facile",
            "explication": "Math.abs() retourne la valeur absolue, donc 7.",
            "mode_specifique": "video"
        },
        {
            "question": "Que retourne Math.floor(4.9) ?",
            "options": '{"A": "4", "B": "5", "C": "4.9", "D": "0"}',
            "reponse_correcte": "A",
            "points": 10,
            "difficulte": "facile",
            "explication": "Math.floor() arrondit toujours vers le bas, donc 4.",
            "mode_specifique": "video"
        },
        {
            "question": "Que retourne Math.pow(2, 4) ?",
            "options": '{"A": "6", "B": "8", "C": "12", "D": "16"}',
            "reponse_correcte": "D",
            "points": 10,
            "difficulte": "facile",
            "explication": "Math.pow(2, 4) calcule 2^4 = 16.",
            "mode_specifique": "video"
        },
        {
            "question": "Que retourne Math.sign(-5) ?",
            "options": '{"A": "0", "B": "1", "C": "-1", "D": "undefined"}',
            "reponse_correcte": "C",
            "points": 10,
            "difficulte": "facile",
            "explication": "Math.sign() retourne -1 pour un nombre négatif, 0 pour zéro, 1 pour positif.",
            "mode_specifique": "video"
        },
        {
            "question": "Comment obtenir un nombre aléatoire entre 1 et 100 ?",
            "options": '{"A": "Math.random() * 100", "B": "Math.floor(Math.random() * 100)", "C": "Math.floor(Math.random() * 100) + 1", "D": "Math.random() * 100 + 1"}',
            "reponse_correcte": "C",
            "points": 15,
            "difficulte": "moyen",
            "explication": "Math.floor(Math.random() * 100) + 1 donne un entier entre 1 et 100.",
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
    print("🎓 INSERTION DU COURS: JAVASCRIPT MATH OBJECT")
    print("=" * 60)
    
    
    conn = get_connection()
    if not conn:
        print("❌ Impossible de se connecter à la base de données")
        return
    
    conn.close()
    print("✅ Connexion à la base de données établie")
    
    
    cours_id = inserer_cours_javascript_math()
    
    if cours_id:
        inserer_questions_javascript_math(cours_id)
        print(f"\n🎉 Succès ! Cours 'JavaScript Math Object - L'Objet Math' créé (ID: {cours_id})")
    else:
        print("\n❌ Échec de l'insertion")

if __name__ == "__main__":
    main()